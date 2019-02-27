# single-name or mismatched addresses
# missing addresses are mapped to the nearest addresses, so they can have an id
location_rename = {
                    'St. James Park (King St. E.)' : 'Bay St / Bloor St W',
                    'Temperance St / Yonge St' : 'Temperance St Station',
                    'Roxton Rd / College St' : 'Ossington Ave / College St',
                    'Davenport Rd / Bedford Rd' : 'Davenport Rd / Avenue Rd',
                    'Landsdowne Subway Green P' : 'Lansdowne Subway Green P',
                    'Bremner Blvd / Spadina Ave' : 'Spadina Ave / Bremner Blvd',
                    'Simcoe St / Wellington St W' : 'Simcoe St / Wellington St 1',
                    'Bloor GO / UP Station/ Rail Path' : 'Bloor GO / UP Station (West Toronto Railpath)'
                    }

# spelling mistakes / renaming a street
street_name_spelling = {
                    'Lake Shore Blvd' : 'Lakeshore Blvd',
                    'Berkely St' : 'Berkeley St',
                    'Michael Sweet Ave' : 'Dundas St'
                    }

# missing locations
missing_coordinates = {
                    '7029' : [43.6697157, -79.3894773] # Bay St / Bloor St W
                    }

# don't know what these entires correspond to
unknown_locations = ['Base Station', 'Fringe Next Stage - 7219']
