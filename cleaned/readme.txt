A. Individual trip events datasets:
===================================
The data tables that contain all individual trip events (e.g. q1_2017_events_cleaned.csv, 2017_events_joined.csv) have the following columns:

1.  trip_id (int) : the ID of the trip in the Bike Share Toronto 
2.  wkday (int) : the day of the week, Monday = 0, Sunday = 6
3.  trip_start_date (str) : YYYY-MM-DD, year-month-date format
4.  trip_start_time (str) : hh:mm, hour-minute format
5.  trip_duration_seconds (int) : the duration of the trip, in seconds
6.  trip_distance (float) : the distance between the start/end stations, in meters
7.  from_station_id (int) : ID of the station where a trip started 
8.  from_station_name (str) : name of the station where a trip started
9.  from_lat (float) : latitude of the station
10. from_lon (float) : longitude of the station
11. to_station_id (int) : ID of the station where a trip ended
12. to_station_name (str) : name of the tation where a trip ended
13. to_lat (float) : latitude of the station
14. to_lon (float) : longitude of the station
15. user_type (str) : if the user was a member, = Member or Casual

B. Hourly events datasets:
==========================
We extract historical weather data from Environment Canada and calculate hourly event totals using the individual trip events tables to form new tables which contain hourly bike share usage information:

1. season (int) : Q1 (Jan-March)/Winter = 1, Q2 (Apr - June)/Spring = 2, Q3 (July - Sept)/Summer = 3, Q4 (Oct - Dec)/Winter = 4
2. wkday (int) : the day of the week, Monday = 0, Sunday = 6 
3. date (str) : YYYY-MM-DD, year-month-date format
4. hr (int) : 0 - 23
5. holiday (int) : = 1 if day is weekend or statutory holiday, = 0 if not
6. temp (float) : 0 < normalized temperature < 1, temp = (temp - min_temp) / (max_temp - max_temp),
7. windspd (float) : 0 < normalized wind speed < 1, windspd = windspd / max_windspd
8, hum (float) : 0 < relative humidity < 1
9. adjtemp (float) : 0 < normalized adjusted temperature < 1, adjtemp = (adjtemp - min_adjtemp) / (max_adjtemp - max_adjtemp), this column is calculated as a wind chill value or humidex
10. condition (int) : annotated condition, 1 = good, 2 = ok, 3 = bad, 4 = severe. Categories are defined in get_hourly_data_script.py:

conditions_rating = {
    'Clear' : 1, 'Mainly Clear' : 1, 'Mostly Cloudy' : 1,
    'Cloudy' : 2, 'Fog' : 2, 'Drizzle' : 2,
    'Snow Showers' : 3, 'Rain Showers' : 3, 'Moderate Rain Showers' : 3, 'Snow' : 3,
    'Moderate Snow' : 3, 'Moderate Rain' : 3, 'Rain' : 3, 'Snow Grains' : 3, 'Ice Pellets' : 3,
    'Freezing Fog' : 4, 'Thunderstorms' : 4, 'Heavy Rain Showers' : 4, 'Freezing Rain' : 4,
    'Blowing Snow' : 4, 'Freezing Drizzle' : 4, 'Heavy Rain' : 4, 'Heavy Snow' :4,
    'Heavy Snow Showers' : 4, 'Moderate Freezing Rain' : 4
}

11. casual (int) : number of casual users in the current hour
12. member (int) : number of members in the current hour
13. total (int) : number of casual + member
