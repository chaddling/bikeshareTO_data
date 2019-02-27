import json
from dateutil.parser import parse
import pandas as pd
import requests
import sys

from parse_names import parseName, lookup
from data_exceptions import missing_coordinates, location_rename, unknown_locations

input_filename, output_filename = sys.argv[1:]
data = pd.read_csv(input_filename)

# drop rows that contain NULL or unknown locations
data.dropna(how='any',axis=0, inplace=True)
data = data[~data['from_station_name'].isin(unknown_locations)]
data = data[~data['to_station_name'].isin(unknown_locations)]

# throw away trip stop time (redundant)
rename_columns = {'trip_start_time' : 'trip_start_date',
                'trip_stop_time' : 'trip_start_time'}
data.rename(index=str, columns=rename_columns, inplace=True)
data.sort_values('trip_id', inplace=True)
data.reset_index(drop=True, inplace=True)

# new column for days of the week
# monday = 0, sunday = 6
if 'wkday' not in data.index:
    new_col_index = data.columns.get_loc('trip_start_date')
    data.insert(new_col_index, 'wkday', 0)

# if no station_id columns, insert to LEFT of name columns
if 'from_station_id' not in data.columns:
    new_col_index = data.columns.get_loc('from_station_name')
    data.insert(new_col_index, 'from_station_id', 0)

if 'to_station_id' not in data.columns:
    new_col_index = data.columns.get_loc('to_station_name')
    data.insert(new_col_index, 'to_station_id', 0)

# create the new lon, lat coordinate columns i
if 'from_lat' and 'from_lon' not in data.columns:
    new_col_index = data.columns.get_loc('from_station_name') + 1
    data.insert(new_col_index, 'from_lat', 0.0)
    new_col_index = data.columns.get_loc('from_lat') + 1
    data.insert(new_col_index, 'from_lon', 0.0)

if 'to_lat' and 'to_lon' not in data.columns:
    new_col_index = data.columns.get_loc('to_station_name') + 1
    data.insert(new_col_index, 'to_lat', 0.0)
    new_col_index = data.columns.get_loc('to_lat') + 1
    data.insert(new_col_index, 'to_lon', 0.0)

# insert a new column to store trip distance to RIGHT of trip duration
if 'trip_distance' not in data.columns:
    new_col_index = data.columns.get_loc('trip_duration_seconds') + 1
    data.insert(new_col_index, 'trip_distance', 0.0)

# json file: https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_information
with open('station_information.json', "r") as f:
    station_info = json.load(f)

# build some dictionaries for the stations, for different searches
id_to_location = {}
name_to_id = {}
intersection_lookup = {}
for station in station_info['data']['stations']:
    # if the json file id/coords do not correspond to the actual station read in csv
    # we correct the data
    if station['station_id'] in missing_coordinates.keys():
        d = {int(station['station_id']): missing_coordinates[station['station_id']] }
    else:
        d = {int(station['station_id']) : [station['lat'], station['lon']]}
    id_to_location.update(d)

    # if a json file station name/id do not reflect the actual station name in csv
    # we modify its name in the dictionary
    if station['name'] in location_rename.keys():
        station['name'] = location_rename[station['name']]
    d = {station['name'] : int(station['station_id'])}
    name_to_id.update(d)

    # build the dictionary for mapping (name1, name2) to a station name, which
    # can be keyed in the name_to_id dictionary
    name1, name2 = parseName(station['name'])
    d = {name2 : station['name']}
    if name1 not in intersection_lookup.keys():
        intersection_lookup.update({name1 : d})
    else:
        intersection_lookup[name1].update(d)

# kwargs for different years, since format is different in different files
# 2016 Q3: dayfirst = False
# 2016 Q4: dayfirst = True
# 2017 Q1, Q2: dayfirst = True
# 2017 Q3, Q4: leave empty
if '2016' in input_filename:
    parse_date_kwargs = {'yearfirst' : 'True', 'dayfirst' : 'True'}
elif '2017' in input_filename:
    parse_date_kwargs = { }

# run OSRM backend using docker: https://hub.docker.com/r/osrm/osrm-backend/
# url to call OSRM server run on localhost
url = 'http://127.0.0.1:5000/route/v1/bicycling/{},{};{},{}?overview=false'

# modify the table entries
for i in data.index:
    # date/time info
    start_date, start_time = data.trip_start_date[i].split()
    data.at[i, 'trip_start_date'] = parse(start_date, **parse_date_kwargs).date().isoformat()
    data.at[i, 'wkday'] = parse(start_date, **parse_date_kwargs).weekday()
    data.at[i, 'trip_start_time'] = start_time

    # look up station ids
    if data.from_station_id[i] == 0 and data.to_station_id[i] == 0:
        from_name = lookup(data.from_station_name[i], intersection_lookup)
        to_name = lookup(data.to_station_name[i], intersection_lookup)
        data.at[i, 'from_station_id'] = name_to_id[from_name]
        data.at[i, 'to_station_id'] = name_to_id[to_name]

    # coordinate info
    data.at[i, 'from_lat'] = id_to_location[data.from_station_id[i]][0]
    data.at[i, 'from_lon'] = id_to_location[data.from_station_id[i]][1]
    data.at[i, 'to_lat'] = id_to_location[data.to_station_id[i]][0]
    data.at[i, 'to_lon'] = id_to_location[data.to_station_id[i]][1]

    # distance info
    req = requests.get(url.format(data.from_lon[i], data.from_lat[i],data.to_lon[i], data.to_lat[i]))
    data.at[i, 'trip_distance'] = req.json()['routes'][0]['legs'][0]['distance']

# save the output
data.to_csv(output_filename, index=False)
