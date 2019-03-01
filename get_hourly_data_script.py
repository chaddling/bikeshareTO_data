###############################################################################
# this script produces the hourly usage datasets from the cleaned annual bike
# share datasets and the annual weather datasets
#
# Author: Chad Gu
# Date: 2017-02-28
###############################################################################
import pandas as pd
import numpy as np
import math

# calculate adjusted temperature either as wind chill or humidex
def calculateAdjTemp(temp, dew_point_temp, wind_spd):
    if temp < 5:
        return round(calculateWindchill(temp, wind_spd), 3)
    else: # adj all temperatures?
        return round(calculateHumidex(temp, dew_point_temp), 3)

def calculateHumidex(temp, dew_point_temp):
        return temp + 0.5555*(6.11*math.exp(5417.7530*(1/273.16 - 1/(dew_point_temp+273.15))) - 10)

def calculateWindchill(temp, wind_spd):
    return 13.12 + 0.6215*temp - 11.37*math.pow(wind_spd, 0.16) + 0.3965*temp*math.pow(wind_spd, 0.16)

# label statutory holidays in Ontario
holidays = { 2017 : ['2017-01-01','2017-02-20', '2017-04-14', '2017-05-22', '2017-07-03', '2017-09-04',
                    '2017-10-09', '2017-12-25', '2017-12-26'],
             2016 : ['2016-07-01', '2016-09-05', '2016-10-10', '2016-12-25', '2016-12-26']
}

# annotated weather conditions
conditions_rating = {
    'Clear' : 1, 'Mainly Clear' : 1, 'Mostly Cloudy' : 1,
    'Cloudy' : 2, 'Fog' : 2, 'Drizzle' : 2,
    'Snow Showers' : 3, 'Rain Showers' : 3, 'Moderate Rain Showers' : 3, 'Snow' : 3,
    'Moderate Snow' : 3, 'Moderate Rain' : 3, 'Rain' : 3, 'Snow Grains' : 3, 'Ice Pellets' : 3,
    'Freezing Fog' : 4, 'Thunderstorms' : 4, 'Heavy Rain Showers' : 4, 'Freezing Rain' : 4,
    'Blowing Snow' : 4, 'Freezing Drizzle' : 4, 'Heavy Rain' : 4, 'Heavy Snow' :4,
    'Heavy Snow Showers' : 4, 'Moderate Freezing Rain' : 4
}

year = 2017
weather_filename = 'weather/{}_weather_joined.csv'.format(year)
weather = pd.read_csv(weather_filename)
hrs_in_year = len(weather)

data_filename = 'cleaned/{}_events_joined.csv'.format(year)
data = pd.read_csv(data_filename)

hourlyDF = pd.DataFrame({'season' : [0]*hrs_in_year,
                        'wkday' : ' ',
                        'date' : ' ',
                        'hr' : weather.Time,
                        'holiday' : [0]*hrs_in_year,
                        'temp' : weather.Temp,
                        'windspd' : weather.WindSpd,
                        'hum' : weather.RelHum,
                        'adjtemp' : [0.0]*hrs_in_year,
                        'condition' : [0]*hrs_in_year, # to do
                        'casual' : [0]*hrs_in_year,
                        'member' : [0]*hrs_in_year,
                        'total' : [0]*hrs_in_year
})

countDF = pd.DataFrame({'date': data.trip_start_date,
                        'hr': data['trip_start_time'].str.split(':', expand=True)[0],
                        'user_type': data.user_type
})

# just keep track of integer 0 - 23 for hour
# IS THERE A BETTER WAY TO DO THIS?
for i in data.index:
    countDF.at[i, 'hr'] = int(countDF.at[i, 'hr'])

countDFc = countDF[countDF['user_type'] == 'Casual']
countDFm = countDF[countDF['user_type'] == 'Member']

countDF_casual = countDFc.groupby(['date', 'hr']).count()
countDF_member = countDFm.groupby(['date', 'hr']).count()

for i in weather.index:
    # which quarter is it
    if weather.Month[i] <= 3:
        hourlyDF.at[i, 'season'] = 1
    elif 4 <= weather.Month[i] <= 6:
        hourlyDF.at[i, 'season'] = 2
    elif 7 <= weather.Month[i] <= 9:
        hourlyDF.at[i, 'season'] = 3
    else:
        hourlyDF.at[i, 'season'] = 4

    hourlyDF.at[i, 'date'] = pd.Timestamp(weather.Year[i], weather.Month[i], weather.Day[i]).date().isoformat()
    hourlyDF.at[i, 'wkday'] = pd.Timestamp(weather.Year[i], weather.Month[i], weather.Day[i]).weekday()

    if hourlyDF.at[i, 'wkday'] > 4 or hourlyDF.at[i, 'date'] in holidays[year]:
        hourlyDF.at[i, 'holiday'] = 1
    else:
        hourlyDF.at[i, 'holiday'] = 0

    hourlyDF.at[i, 'hr'] = int(hourlyDF.at[i, 'hr'].split(':')[0])
    hourlyDF.at[i, 'adjtemp'] = calculateAdjTemp(weather.Temp[i], weather.DewPointTemp[i], weather.WindSpd[i])

    # assign previous recorded weather condition
    if not isinstance(weather.Weather[i], str):
        if i-1 >=0 and isinstance(weather.Weather[i-1], str):
            weather.at[i, 'Weather'] = weather.Weather[i-1]
        elif i+1 < len(weather) and isinstance(weather.Weather[i+1], str):
            weather.at[i, 'Weather'] = weather.Weather[i+1]

    # if the condition contains several observations, we take the worst weather condition
    conds = [conditions_rating[key] for key in weather.Weather[i].split(',')]
    hourlyDF.at[i, 'condition'] = max(conds)

    try:
        hourlyDF.at[i, 'casual'] = countDF_casual['user_type'][hourlyDF.date[i]][hourlyDF.hr[i]]
    except Exception as e:    # the count is zero if there are no riders in that particular date/hour
        hourlyDF.at[i,'casual'] = 0

    try:
        hourlyDF.at[i, 'member'] = countDF_member['user_type'][hourlyDF.date[i]][hourlyDF.hr[i]]
    except Exception as e:
        hourlyDF.at[i, 'member'] = 0

    hourlyDF.at[i, 'total'] = hourlyDF.casual[i] + hourlyDF.member[i]

# normalize numerical temp/adjtemp values - by their own max/min
Dt = hourlyDF.temp.max() - hourlyDF.temp.min()
hourlyDF['temp'] = round((hourlyDF['temp'] - hourlyDF.temp.min()) / Dt, 4)
Dt = hourlyDF.adjtemp.max() - hourlyDF.adjtemp.min()
hourlyDF['adjtemp'] = round((hourlyDF['adjtemp'] - hourlyDF.adjtemp.min()) / Dt, 4)
# normalize by max
hourlyDF['hum'] /= 100
hourlyDF['windspd'] = round(hourlyDF['windspd']/weather.WindSpd.max(), 4)

# save file
hourlyDF.to_csv('cleaned/{}_hourly.csv'.format(year), index=False)
