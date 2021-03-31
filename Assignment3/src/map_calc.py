import math

# https://docs.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system
# Mercator projection of spherical Earth
# latitude and longitude in degrees, WGS 84 datum
# level = bing maps resolution level
# tile is 256x256 pixels
earthRad = 6378137 # meters
minLat = -85.05112878
maxLat = 85.05112878
minLon = -180
maxLon = 180

def width(level):
    # in pixels
    # both width and height since map is square
    return 256 * (2 ** level)

def ground_resolution(lat, level):
    # distance on the ground that’s represented by a single pixel in the map
    if lat < minLat or lat > maxLat:
        print('ground_resolution: invalid latitude')
        return
    return (math.cos(lat * math.pi/180) * 2 * math.pi * earthRad) / width(level)

def map_scale(lat, level, dpi):
    # ratio between map distance and ground distance, when measured in the same units
    # returns n, so that the map scale is 1 : n
    if lat < minLat or lat > maxLat:
        print('map_scale: invalid latitude')
        return
    m_per_inch = 0.0254 # meters/inch
    return ground_resolution(lat, level) * dpi / m_per_inch

def latLonToPixelXY(lat, lon, level):
    # the pixel corresponding to the given coordinates
    if lat < minLat or lat > maxLat:
        print('pixel_coordinates: invalid latitude')
        return
    if lon < minLon or lon > maxLon:
        print('pixel_coordinates: invalid longitude')
        return
    sinLat = math.sin(lat * math.pi/180)
    pixelX = ((lon + 180) / 360) * width(level)
    pixelY = (0.5 - math.log((1 + sinLat) / (1 - sinLat)) / (4 * math.pi)) * width(level)
    return (pixelX, pixelY)

def pixelXYToLatLon(pixelX, pixelY, level):
    # be warned! no bounds checking!
    mapSize = width(level)
    x = (pixelX / mapSize) - 0.5
    y = 0.5 - (pixelY / mapSize)
    lat = 90 - 360 * math.atan(math.exp(-y * 2 * math.pi)) / math.pi;
    lon = 360 * x
    return (lat, lon)

def pixelXYToTileXY(pixels):
    # Assuming pixels is the output of latLonToPixelXY
    return (math.floor(pixels[0] / 256), math.floor(pixels[1] / 256))

def tileXYToPixelXY(tileX, tileY):
    # upper left pixel of tile
    return (tileX*256, tileY*256)

def toBase4(b):
    # convert 2-digit binary number to base 4
    if b == '00':
        return '0'
    if b == '01':
        return '1'
    if b == '10':
        return '2'
    if b == '11':
        return '3'
    print('toBase4: incorrect parameter')

def tileXYToQuadkey(tiles):
    # Assuming tiles is the output of pixel_to_tile
    # convert to binary, remove '0b'
    xbin = bin(tiles[0])[2:]
    ybin = bin(tiles[1])[2:]
    # make them same length
    xbin = xbin.zfill(len(ybin))
    ybin = ybin.zfill(len(xbin))
    # interleave
    weave = ['{}{}'.format(y,x) for (y,x) in zip(ybin,xbin)] # y first
    convert = map(toBase4, weave)
    return ''.join(convert)

def quadKeyToTileXY(quadkey):
    tileX = tileY = 0
    level = len(quadkey)
    for i in range(level, 0, -1):
        mask = 1 << i - 1
        next  = quadkey[level - i]
        if next == '0':
            break
        elif next == '1':
            tileX = tileX | mask
        elif next == '2':
            tileY = tileY | mask
        elif next == '3':
            tileX = tileX | mask
            tileY = tileY | mask
        else:
            print('quadKeyToTileXY: invalid quadkey')
    return (tileX, tileY)

############################################

def getBestLevel_naive(lat1, lon1, lat2, lon2):
    # the highest level for which the bounding box fits in one tile
    # integer 0 - 20
    for i in range(2,21):
        pixelA = latLonToPixelXY(lat1, lon1, i)
        pixelB = latLonToPixelXY(lat2, lon2, i)
        tileA = pixelXYToTileXY(pixelA)
        tileB = pixelXYToTileXY(pixelB)
        if tileA != tileB:
            return i-1
    return 20

def getBestLevel(lat1, lon1, lat2, lon2):
    # the level at which the composite of relevant tiles
    # does not exceed 4096x4096
    for i in range(23, 0, -1):
        # get tile coordinates for corners of bounding box
        NWTile = latLonToTileXY(lat2, lon1, i)
        NETile = latLonToTileXY(lat2, lon2, i)
        SWTile = latLonToTileXY(lat1, lon1, i)
        SETile = latLonToTileXY(lat1, lon2, i)
        # width and height of bounding box in tiles
        width = NETile[0] - NWTile[0] + 1
        height = SWTile[1] - NWTile[1] + 1
        # convert to pixels: each tile is 256x256 pixels
        width *= 256
        height *= 256
        if width <= 4096 and height <= 4096:
            return i


def latLonToTileXY(lat, lon, level):
    return pixelXYToTileXY(latLonToPixelXY(lat, lon, level))

def latLonToQuadkey(lat, lon, level):
    return tileXYToQuadkey(pixelXYToTileXY(latLonToPixelXY(lat, lon, level)))
