###############################################################################
# this script simply joins all the cleaned quarter-year bike share datasets and
# the raw monthly weather data
#
# Author: Chad Gu
# Date: 2017-02-27
###############################################################################
import pandas as pd

header_hourly = 13 # number of rows to skip in reading the csv file

weather_frames = []
current_year = 2016
first_month = 7
last_month = 12
days_in_a_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

if current_year == 2016:
    quarters = ['q3', 'q4']
else:
    quarters = ['q1', 'q2', 'q3', 'q4']

for month in range(first_month, last_month+1):
    current_month = str(month).zfill(2)
    first_day = '01'
    start_date = '{}{}{}'.format(current_month, first_day, current_year)

    last_day = '{}'.format(days_in_a_month[month-1])
    end_date = '{}{}{}'.format(current_month, last_day, current_year)

    filename = 'weather/environment_canada/eng-hourly-{}-{}.csv'.format(start_date, end_date)

    df = pd.read_csv(filename, header=header_hourly)
    weather_frames.append(df)

# rename some columns
rename_columns = {'Temp (°C)' : 'Temp',
                  'Dew Point Temp (°C)' : 'DewPointTemp',
                  'Rel Hum (%)' : 'RelHum',
                  'Wind Spd (km/h)' : 'WindSpd',
                  'Stn Press (kPa)' : 'StnPress',
                  'Wind Chill' : 'WindChill'
}

weather_joined = pd.concat(weather_frames, ignore_index=True)
weather_joined.rename(index=str, columns=rename_columns, inplace=True)
weather_joined.reset_index(drop=True, inplace=True)
# go to the file and remove some brackets and symbols in the col names
output_filename = 'weather/{}_weather_joined.csv'.format(current_year)
weather_joined.to_csv(output_filename, index=False)

data_frames = []
for q in quarters:
    filename = 'cleaned/{}_{}_events_cleaned.csv'.format(q, current_year)

    df = pd.read_csv(filename)
    data_frames.append(df)

data_joined = pd.concat(data_frames)
data_joined.reset_index(drop=True, inplace=True)
output_filename = 'cleaned/{}_events_joined.csv'.format(current_year)
data_joined.to_csv(output_filename, index=False)
