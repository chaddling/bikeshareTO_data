A. Individual trip events datasets:
===================================

The data tables that contain all individual trip events (e.g. q1_2017_events_cleane.csv) have the following columns:

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
