# Stop Finder
This Script will search for possible Stops in your area, check if they're in a free level 17 S2 Cell and compile them.

### Credits
- u/un1matr1x_0 who made [this overpass query](http://overpass-turbo.eu/s/Rpy) this is based off
- [madao](https://github.com/M4d40/PMSFnestScript) and [MAD](https://github.com/Map-A-Droid/MAD) the overpass api and s2cell code

## Setup
- `cp config.ini.example config.ini`, `pip3 install -r requirements.txt`, fill out config.ini with your DB stuff
- Go to [bboxfinder.com](http://bboxfinder.com/), select your area, copy the part after `Box` in the bottom and paste it in your config
- Done. Now run the script with `python3 stopfinder.py`

## Notes
- Right now, this will only look for nodes (single points) and leave out all areas (Mostly playgrounds and sportfields)
- Got to <http://overpass-turbo.eu/s/Rpy> to view _all_ the queried POIs on a map
- If you want to analyze another area, you'll have to delete data.json and change the bbox
- You can use the IDs from the output to view them directly by going to`https://www.openstreetmap.org/node/{id}`
