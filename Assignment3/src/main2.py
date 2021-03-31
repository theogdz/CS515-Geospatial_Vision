import sys
import os
import requests
import json
from map_calc import *
from PIL import Image

bing_key = ''
base_url = 'http://dev.virtualearth.net/REST/v1/'
base_params = {'key': bing_key}

def getBingKeyFromFile():
    with open('bing_key.txt', 'r') as f:
        return f.readline()

def getImage(lat1, lon1, lat2, lon2, outFile):
    '''
    lat1 = South Latitude
    lon1 = West Longitude
    lat2 = North Latitude
    lon2 = East Longitude
    '''

    level = getBestLevel(lat1, lon1, lat2, lon2)
    print('level: ', level)

    NWTile = latLonToTileXY(lat2, lon1, level)
    NETile = latLonToTileXY(lat2, lon2, level)
    SWTile = latLonToTileXY(lat1, lon1, level)
    SETile = latLonToTileXY(lat1, lon2, level)

    width_start = NWTile[0] # SWTile[0]
    width_end = NETile[0] # SETile[0]
    height_start = NWTile[1] # NETile[0]
    height_end = SWTile[1] # SETile[1]

    params = {
        'key': bing_key,
        'mapSize': '256,256',
        'format': 'png'
    }
    url = base_url + 'Imagery/Map/Aerial'

    true_width = width_end-width_start+1
    true_height = height_end-height_start+1
    print('Tiles: ', true_width * true_height)

    final = Image.new('RGB', (true_width*256, true_height*256))

    # retrieve the relevant tiles
    inc = 1
    for i in range(width_start, width_end+1):
        for j in range(height_start, height_end+1):
            print(inc)
            inc += 1
            # get upper left pixel of tile (i,j)
            pixels = tileXYToPixelXY(i, j)
            # get the center pixel of the tile
            center = (pixels[0]+128, pixels[1]+128)
            # convert the center pixel to coordinates
            coords = pixelXYToLatLon(center[0], center[1], level)
            # format the centerpoint for the API
            centerPoint = '{},{}'.format(coords[0], coords[1])
            # construct the API endpoint URL
            new_url = url + '/' + centerPoint
            new_url += '/' + str(level)
            # call the bing API
            response = requests.get(new_url, params=params)
            # check for proper status
            if response.status_code != 200:
                print(response.content)
                exit()
            # write the retrieved image to the file
            with open('temp.png', 'wb') as f:
                f.write(response.content)
            # paste into final image
            with Image.open('temp.png') as im:
                x = (i - width_start)*256
                y = (j - height_start)*256
                final.paste(im, box=(x,y))

    # save result
    final.save(outFile, 'PNG')

def findPointsOfInterest(lat1, lon1, lat2, lon2):
# 1 = 111 km
    # Finding the center point of the box
    aveLat = (lat1 + lat2)/2
    aveLong = (lon1 + lon2)/2
    # Finding the maximum radius that would fix the box
    radius = 111*(min(abs(lat1-lat2),abs(lon1-lon2))/2)
    # Range of radius: 1 < radius < 1000
    if radius < 1:
        radius = 1
    if radius > 1000:
        radius = 1000
    para = {'key': bing_key}
    # Places of interest
    attraction = {"Park":'7947',"Art Center":'7929',"Obsevation Point":'114',"Museum":'8410'}
    for attr in attraction.items():
        print("Most popular {} in the area is: ".format(attr[0]))
        u ="http://spatial.virtualearth.net/REST/v1/data/Microsoft/PointsOfInterest?spatialFilter=nearby({},{},{})&$filter=EntityTypeID%20eq%20'{}'&$select=DisplayName,AddressLine&$top=3&$format=json".format(aveLat,aveLong,radius,attr[-1])
        response = requests.get(u, params=para)
        metadata = json.loads(response.content)
        for meta in metadata["d"]["results"]:
            print(meta["DisplayName"],", ",meta["AddressLine"])


if __name__ == '__main__':
    if len(sys.argv) != 6:
        print('Incorrect number of arguments.')
        print('Usage: ./main2.py lat1 lon1 lat2 lon2 outFile.png')
        print('lat1 = South Latitude')
        print('lon1 = West Longitude')
        print('lat2 = North Latitude')
        print('lon2 = East Longitude')
        exit()
    coords = []
    for i in range(1,5):
        a = sys.argv[i]
        try:
            coords.append(float(a))
        except ValueError:
            print('Incorrect type of arguments.')
            print('Usage: ./main2.py lat1 lon1 lat2 lon2 outFile.png')
            print('lat1 = South Latitude')
            print('lon1 = West Longitude')
            print('lat2 = North Latitude')
            print('lon2 = East Longitude')
            exit()
    outFile = sys.argv[5]
    bing_key = getBingKeyFromFile()
    if bing_key == None or bing_key == '':
        print('Please place Bing API Key into bing_key.txt')
        exit()
    getImage(*coords, outFile)
    findPointsOfInterest(*coords)