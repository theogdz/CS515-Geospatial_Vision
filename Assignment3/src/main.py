import sys
import os
import requests
import json
from map_calc import *

bing_key = 'AogarSll2NamWfb6ANEeogx-3loYg8pDCpWdDzS_SHFBDgcRI8Z-m6eMURM_HjfM'
base_url = 'http://dev.virtualearth.net/REST/v1/'
base_params = {'key': bing_key}

def retrieveTile(lat1, lon1, lat2, lon2):
    '''
    lat1 = South Latitude
    lon1 = West Longitude
    lat2 = North Latitude
    lon2 = East Longitude
    '''

    # call api
    boundingBox = '{},{},{},{}'.format(lat1, lon1, lat2, lon2)
    imagerySet = 'Aerial'
    zoomLevel = getBestLevel_naive(lat1, lon1, lat2, lon2)
    print(zoomLevel)
    params = {
        'key': bing_key,
        'mapArea': boundingBox,
        'zoomLevel': zoomLevel,
        'format': 'png'
    }
    url = base_url + 'Imagery/Map/Aerial'
    response = requests.get(url, params=params)

    with open("test.png", "wb") as f:
        f.write(response.content)

    # at this point the image would be cropped to th e exact bounding box

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('Incorrect number of arguments.')
        exit()
    coords = []
    for i in range(1,5):
        a = sys.argv[i]
        try:
            coords.append(float(a))
        except ValueError:
            print('Incorrect type of arguments.')
            exit()
    retrieveTile(*coords)
