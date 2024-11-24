'''
This script uses Yelp GraphQL or Fusion API to input relevant restaurant information using lat/lon coords from PSRC data

input files: trips_od_rest.csv
    this file contains the origin and destination lat/long coordinates for each trip, from PSRC
output files: trips_od_yelp.csv
    this file inputs the corresponding restaurant POI information
'''

# import our modules
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import pandas as pd
import time
import requests
import json 


def yelp_scraper(lat, lon):
    '''
    this function uses the Yelp GraphQL API to obtain restaurant information
    '''
    api_key = "qDE55CXHwZ5qjG7hiBJJhrxE2H-Wbz5eZw8Bv8SWLRWsq4KjaqVsQBANXu9UlQxtB_Y_GC64D76TuKrQ-Iumm6TXtznito9FjGZP5TDJDA6rUP0zksHlmch1V9AAZHYx"

    # define our authentication process.
    header = {'Authorization': 'bearer {}'.format(api_key),
            'Content-Type':"application/json"}

    # Build the request framework
    transport = RequestsHTTPTransport(url='https://api.yelp.com/v3/graphql', headers=header, use_json=True)

    # Create the client
    client = Client(transport=transport, fetch_schema_from_transport=True)
            
    # define a simple query
    query = gql('''
    query {
        search(term: "food", latitude: ''' + str(lat) + ''', longitude: ''' + str(lon) + ''', sort_by: "distance", radius: 0, limit:1) {
        business {
            name
            rating
            price
            categories {
            title
            }
        }
        }
    }
    ''')

    # return this query
    return client.execute(query)


def coord_to_poi(row):
    '''
    this function obtains yelp information for a single row in df
    '''
    # determine whether to look at origin or destination for lat/long
    if row.origin_purpose == "Went to restaurant to eat/get take-out":
        lat = row.origin_lat
        lon = row.origin_lng
    elif row.dest_purpose == "Went to restaurant to eat/get take-out":
        lat = row.dest_lat
        lon = row.dest_lng
    else:
        return

    search_results = yelp_scraper(lat, lon)
    # make sure search results are not empty
    if len(search_results["search"]["business"]) == 0:
        return
    
    # get first POI information, which is the one at specified lat/long
    poi = search_results["search"]["business"][0]

    return poi


def poi_finder(row):
    '''
    this function uses the Yelp REST API to pull in restaurant information
    '''
    # api_key = "IjLentrV1J7lZCkutbmgOD_gfHxmPDvi968CcAUJKXW3aAwjs0xWyKlPmtNtSf_DJOx87loLFYjDDMbnuVWlECTXhUzs0CBHBEHGfMogSrluZgd82ABuWbPf5KE1ZHYx"
    # api_key = "qDE55CXHwZ5qjG7hiBJJhrxE2H-Wbz5eZw8Bv8SWLRWsq4KjaqVsQBANXu9UlQxtB_Y_GC64D76TuKrQ-Iumm6TXtznito9FjGZP5TDJDA6rUP0zksHlmch1V9AAZHYx"
    # api_key = "dsznnqlqd9AusZ2IuJFyfWYjPtSSmIHgqFL0RVObsmN9yjkgootqg7qLdKW_AHa6_Nn3NTS8XOv02mglziLOPZYGt5pvFiKOjAtY_7g0UDQYEfyqgCnua5m_6OY2ZHYx"
    # api_key = "IvfCog6qvL71SgvqIOvrx9qez1TGHrwuuMH-OjR4wHAFAbKPDpjw633D5Ho2lYjKRsuF8yAKnWIPmGH3dE0mT5rGaq-yZFtId83Fay_y2iV9sbYEK9id4kCx3c8AZHYx"
    api_key = "DZasEIumuqrfjLvLtY-1i8Ws2r6dzsFyxmUe-wKExIRfVUYRbfQCGxyRTlqlW49RIATzyeu2HtB9qwDGAA3jb_DomAmGYcO2qaPfqC_HmMMzKH-e-D9IRdnKWPo2ZHYx"

    # determine whether to look at origin or destination for lat/long
    if row.origin_purpose == "Went to restaurant to eat/get take-out":
        lat = row.origin_lat
        lon = row.origin_lng
    elif row.dest_purpose == "Went to restaurant to eat/get take-out":
        lat = row.dest_lat
        lon = row.dest_lng

    # search by lat/lon, search for "food", sort by distance (to obtain closest food poi to point)
    radius = 0
    url = "https://api.yelp.com/v3/businesses/search?latitude="+str(lat)+"&longitude=" + str(lon)+ "&term=food&radius=" + str(radius) + "&sort_by=distance&limit=1"

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + api_key
    }

    response = requests.get(url, headers=headers)
    poi_dict = json.loads(response.text)

    print(row.name)
    # print(poi_dict)
    if len(poi_dict["businesses"]) > 0:
        return poi_dict["businesses"][0]
    return

def main():
    # run time
    time0 = time.time()

    # files
    all_trips = pd.read_csv('/Users/kaitlynng/Desktop/UW/Research/code/git/processed_trip_data/restaurant_clustering/trips_od_rest.csv')
    # partial_trips = all_trips[:4500] #1
    partial_trips = all_trips[4500:9000] #2
    # partial_trips = all_trips[9000:13500] #3
    # partial_trips = all_trips[13500:18000] #4
    # partial_trips = all_trips[18000:] #5
    # partial_trips = all_trips[17923:17925]

    # # get yelp info and apply to df column
    partial_trips["restaurant_info"] = partial_trips.apply(poi_finder, axis=1)
    
    # save to csv
    partial_trips.to_csv('/Users/kaitlynng/Desktop/UW/Research/code/git/restaurant_clustering/trips_od_yelp_2.csv')
    # print(partial_trips)

    time1 = time.time()
    print("Time elapsed: ", time1-time0)

main()

# runtime notes for Graph QL:
# 100 entries took 60 seconds and used up 1,309 GraphQl points
# currently have 250,000 GraphQl points per day
# trips_od_rest has 21,142 entries
# split file in two
# file ran at 10:05 am

# for REST API
# split file into 4x4,500 and 1x3,142
# 3142 entries took 1362 seconds
# 4500 entries took 2204 seconds