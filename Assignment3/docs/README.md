# CS513 Assignment 3

## Team members
- Theo Guidroz, A20426895
- Hunter Negron, A20417545
- Zhengcong Xiao, A20453141

## Environment
- Create python virtual environment
- `pip install -r requirements.txt`
- `main.py` is the old, first approach. Do not run.
- Make sure `map_calc.py` is in the same directory as `main2.py`
- Place Bing Maps API Key into `bing_key.txt` in the same directory as `main2.py`

## Usage
`./main2.py lat1 lon1 lat2 lon2 output.png`
- `lat1` = South Latitude
- `lon1` = West Longitude
- `lat2` = North Latitude
- `lon2` = East Longitude
- `output.png` = name of resulting image file (do not call it `temp.png`)
  * all output images are automatically saved in `output` directory
  * images do not exceed 4096x4096 pixels

## Results
Example 1
- `./main2.py 41.830781 -87.630025 41.838600 -87.623159 illinois_tech.png`
  * see `results/illinois_tech.png`

Example 2
- `./main2.py 24.350755 -87.867736 31.133314 -79.507140 florida.png`
  * see `results/florida.png`

Example 3
- `./main2.py -49.685612 90.971393 9.351771 179.216107 austrailia.png`
  * see `results/austrailia.png`
