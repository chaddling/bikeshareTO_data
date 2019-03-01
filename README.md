# Bike Share Toronto Data

This repository contains the cleaned/augmented datasets of Bike Share Toronto trip events from 2016 (partial) to 2017, as well as Python scripts used to perform the data engineering. Each start/end station pair is additionally assigned their latitude/longitude coordinates and the distance of a trip between the pair. 

Inspired by the [UCI Machine Learning Bike Sharing Dataset](https://archive.ics.uci.edu/ml/datasets/bike+sharing+dataset), I also generate hourly usage datasets containing local weather information. Cleaned datasets are located in [this folder](https://github.com/chaddling/bikeshareTO_data/tree/master/cleaned).

Go here for a clustering analysis of the data (TBD). 

1. Data sources
===============
From [Open Data Catalogue](https://www.toronto.ca/city-government/data-research-maps/open-data/open-data-catalogue/) published by the city of Toronto:

- [Bike Share Toronto Ridership Data](https://www.toronto.ca/city-government/data-research-maps/open-data/open-data-catalogue/#343faeaa-c920-57d6-6a75-969181b6cbde)
- [Bike Share Toronto Station Information (JSON format)](https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_information)

Additional sources: 

- Historical weather data from [Environment Canada](http://climate.weather.gc.ca/climate_data/hourly_data_e.html?hlyRange=2013-06-11%7C2019-02-26&dlyRange=2013-06-13%7C2019-02-26&mlyRange=%7C&StationID=51459&Prov=ON&urlExtension=_e.html&searchType=stnName&optLimit=specDate&StartYear=1840&EndYear=2019&selRowPerPage=25&Line=3&searchMethod=contains&txtStationName=toronto&timeframe=1&Year=2016&Month=7&Day=1#)
- [Open Source Routing Machine (OSRM) API](https://hub.docker.com/r/osrm/osrm-backend/)

2. Comments on the data
=======================
Each raw dataset contains important columns such as:

- ``trip_duration``: duration of travel, including timestamp ``trip_start_time``. I dropped the `trip_start_time` timestamp and add a column `wkday` for the day of the week.

- ``from_station_name``, ``to_station_name`` and their IDs ``from_station_id``, ``to_station_id``, which can be used to look up their corresponding latitude and longitude coordinates in [Station Information](https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_information). The IDs are missing in some datasets.

- ``user_type``: whether the user is a Bike Share Toronto member or not.
- See [readme.txt](https://github.com/chaddling/bikeshareTO_data/blob/master/cleaned/readme.txt) for information on the cleaned data columns.

Cleaning the data
-----------------
Some datasets only contain station names, which is not great for identification/location purposes. For such datasets, I use the station name to look up an ID as well as its latitude/longitude in [Station Information](https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_information). This is tricky due to differences in spelling between the two sources. 

I parsed the station names into street names, ignoring designations such as E/W and other extra symbols. Using the parsed names in [Station Information](https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_information), I build a dictionary ``intersection_lookup`` that can be searched as follow: 

    intersection_lookup[name1][name2] = station_name

For example `station_name =` "Fort York  Blvd / Capreol Crt" is parsed into, and can be looked up by `name1 = ` "Fort York Blvd" and `name2 =` "Capreaol Crt". Values of the name columns in the [Bike Share Ridership Data](https://www.toronto.ca/city-government/data-research-maps/open-data/open-data-catalogue/#343faeaa-c920-57d6-6a75-969181b6cbde) are parsed into `name1`, `name2` and looked up to find their names, identifies and coordinates, etc. in the JSON file. Station names with a single street name/string (e.g. "424 Wellington St 1", "Union Station") are looked up with `name2 = ''`.

Exceptions (in `data_exceptions.py`)
------------------------------------
- Removal of data points: these include station name columns which contain NaN and name instances ("Base Station", "Fringe Next Stage - 7219") which cannot be identified by a location.
- Names which are not found in [Station Information](https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_information) are either mapped to their nearest station, handled as spelling exceptions, or renamed to match the correct entry in the JSON file.
- <b> Huge error in the data (!!)</b> In the 2017 data, "Bay St / Bloor St W" has `id = 7029` but in the JSON file this is associated with "St. James Park (King St. E.)". This `id` is kept consistent (since St. James Park does not show up in any of the datasets) and its coordinates are put in by hand to ensure distances are calculated correctly - given the centrality of the Bay St / Bloor St intersection, this is quite important to not be overlooked.

3. Generating hourly usage data
===============================
Using the cleaned data tables containing all events within a year as well as [weather information](http://climate.weather.gc.ca/climate_data/hourly_data_e.html?hlyRange=2013-06-11%7C2019-02-26&dlyRange=2013-06-13%7C2019-02-26&mlyRange=%7C&StationID=51459&Prov=ON&urlExtension=_e.html&searchType=stnName&optLimit=specDate&StartYear=1840&EndYear=2019&selRowPerPage=25&Line=3&searchMethod=contains&txtStationName=toronto&timeframe=1&Year=2016&Month=7&Day=1#), I tallied the total, as well as a breakdown of casual vs member hourly-usage. Each row in the hourly-usage table is assigned temperature/weather condition.

Adjusted temperature `adjtemp` is calculated either as [wind chill](https://en.wikipedia.org/wiki/Wind_chill#North_American_and_United_Kingdom_wind_chill_index) (when < 5 degree Celsius) or [humidex](https://en.wikipedia.org/wiki/Humidex#The_humidex_computation_formula), using some additional information such as wind speed/dew point temperature from the weather data. Numerical data columns as normalized (see [readme.txt](https://github.com/chaddling/bikeshareTO_data/blob/master/cleaned/readme.txt)).

In the raw weather data, weather condition is recorded every 3-hour interval starting from 1:00am, with more frequent in-between recordings if the condition changes. Thus, empty recordings are assigned the last observed condition(s). The `condition` column in the hourly-usage tables are human annotated, is assigned an integer 1 (good weather condition) to 4 (severe weather condition). See [readme.txt](https://github.com/chaddling/bikeshareTO_data/blob/master/cleaned/readme.txt) for how this value was assigned.

