###############################################################################
# Some functions used to generate name strings from an intersection / station
# name 
#
# Author: Chad Gu
# Date: 2017-02-25
###############################################################################
from data_exceptions import street_name_spelling, location_rename, missing_coordinates

# return the "name" found in json file
def lookup(location: str, intersection: dict):
    if location in location_rename:
        location = location_rename[location]

    key1, key2 = parseName(location)

    if key1 in street_name_spelling:
        key1 = street_name_spelling[key1]

    if key2 in street_name_spelling:
        key2 = street_name_spelling[key2]

    return intersection[key1][key2] # returns the name to be found in name_to_id


# returns the minimal street names of an intersection
def parseName(intersection: str):
    if intersection.find('/') == -1:   # station is a single landmark / street
        return minStreetName(intersection), ''
    elif intersection.find('/') > intersection.find('(') > -1: # occurs in 1 name
        return minStreetName(intersection), ''
    elif intersection.find(' /') > -1:  # station is an intersection separated by /
        streets = intersection.split(' /')
        return minStreetName(streets[0]), minStreetName(streets[1])
    elif intersection.find('/') > -1:   # some name entries have no space before /
        streets = intersection.split('/')
        return minStreetName(streets[0]), minStreetName(streets[1])

# returns the "minimum" street name and removes punctuations
def minStreetName(name: str):
    name = name.strip(' ')

    # extra symbols which are removed
    l = [name.find('('), name.find('-'), name.find('SMART'), name.find('Green P')]
    l_found = sorted([x for x in l if x > -1])

    if len(l_found) == 0:
        lim = len(name)
    else:
        lim = l_found[0]

    if name[:lim].split()[-1] in ['E', 'W']:
        word_list = [word for word in name[:lim].split()[:-1]]
    else:
        word_list = [word for word in name[:lim].split()]

    min_street_name = ('{} '*(len(word_list)-1) + '{}').format(*word_list)
    min_street_name = min_street_name.replace('.', '')
    min_street_name = min_street_name.replace('\'', '')
    return min_street_name
