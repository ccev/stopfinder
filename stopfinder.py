import s2sphere
import requests
import json

from pymysql import connect
from configparser import ConfigParser
from urllib.parse import quote

class config():
    def __init__(self):
        config_file = ConfigParser()
        config_file.read("config.ini")

        self.bbox = list(config_file.get("Config", "bbox").split(","))

        self.scan_type = config_file.get("Config", "db_schema").lower()
        self.db_name_scan = config_file.get("Config", "db_name")
        self.db_host = config_file.get("Config", "db_host")
        self.db_port = config_file.getint("Config", "db_port")
        self.db_user = config_file.get("Config", "db_user")
        self.db_password = config_file.get("Config", "db_password")

class queries():
    def __init__(self, schema, cursor):
        self.cursor = cursor
        self.schema = schema
    
    def count_in_cell(self, area):
        if self.schema == "mad":
            self.cursor.execute(f"SELECT (SELECT COUNT(pokestop_id) FROM pokestop WHERE ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude))), (SELECT COUNT(gym_id) FROM gym WHERE ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(latitude, longitude)));")
        elif self.schema == "rdm":
            self.cursor.execute(f"SELECT (SELECT COUNT(id) FROM pokestop WHERE ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon))), (SELECT COUNT(id) FROM gym WHERE ST_CONTAINS(ST_GEOMFROMTEXT('POLYGON(({area}))'), point(lat, lon)));")
        count = self.cursor.fetchone()

        return count

class s2cell():
    def __init__(self, queries, lat, lon):
        """
        I copied most of this code from Map-A-Droid.
        """
        level = 17
        ll = s2sphere.LatLng.from_degrees(lat, lon)
        cell = s2sphere.CellId().from_lat_lng(ll)
        cellId = cell.parent(level).id()
        cell = s2sphere.Cell(s2sphere.CellId(cellId))

        path = []
        for v in range(0, 4):
            vertex = s2sphere.LatLng.from_point(cell.get_vertex(v))
            path.append([vertex.lat().degrees, vertex.lng().degrees])

        stringfence = ""
        for coordinates in path:
            stringfence = f"{stringfence}{coordinates[0]} {coordinates[1]},"
        stringfence = f"{stringfence}{path[0][0]} {path[0][1]}"
        count = queries.count_in_cell(stringfence)

        self.path = path
        self.stops = count[0] + count[1]

    def empty(self):
        if self.stops == 0:
            return True
        else:
            return False

def osm_uri(p1_lon, p1_lat, p2_lon, p2_lat):
    """Generate the OSM uri for the OSM data"""
    OSM_API = "https://overpass-api.de/api/interpreter"
    OSM_TAGS = """
    nwr["historic"="monument"];
    nwr["historic"="memorial"];
    nwr["historic"="archaeological_site"];
    nwr["amenity"="public_bookcase"];
    nwr["sport"="skateboard"];
    nwr["sport"="roller_skating"];
    nwr["sport"="bmx"];
    nwr["leisure"="pitch"];
    nwr["leisure"="track"];
    nwr["leisure"="sports_centre"];
    nwr["leisure"="playground"];
    nwr["amenity"="toy_library"][!"shop"];
    nwr["tourism"="museum"];
    nwr["historic"="castle"];
    nwr["amenity"="community_centre"];
    nwr["amenity"="townhall"];
    nwr["amenity"="place_of_worship"];
    nwr["amenity"="fountain"];
    nwr["information"="board"]["!traffic_sign"];
    nwr.cultural;
    nwr.sporty;
    nwr.playgrounds;
    nwr.publicbuildings;
    nwr.religious;
    nwr.addons;
    """
    osm_bbox = f"[bbox:{p1_lat},{p1_lon},{p2_lat},{p2_lon}]"
    osm_data = "?data="
    osm_type = "[out:json]"
    #date = '[date:"{osm_date}"];'.format(osm_date=osm_date)
    tag_data = OSM_TAGS.replace("\n", "").replace(" ", "")
    osm_tag_data = f";({tag_data});"
    osm_end = "out;>;out skel qt;"
    uri = OSM_API + osm_data + quote(osm_type + osm_bbox + osm_tag_data + osm_end)
    return uri

config = config()
mydb = connect(host = config.db_host, user = config.db_user, password = config.db_password, database = config.db_name_scan, port = config.db_port, autocommit = True)
cursor = mydb.cursor()
queries = queries(config.scan_type, cursor)

try:
    with open("data.json", "r") as f:
        osm_json = json.loads(f.read())

except:
    url = osm_uri(config.bbox[0], config.bbox[1], config.bbox[2], config.bbox[3])
    print(url)
    session = requests.Session()
    response = session.get(url)
    response.raise_for_status()
    osm_json = response.json()

    with open("data.json", "w+") as f:
        f.write(response.text) 

final = ""
for element in osm_json["elements"]:
    if "lat" in element and "lon" in element and "tags" in element:
        cell = s2cell(queries, element["lat"], element["lon"])
        if cell.empty():
            final = f"{final}id: {element['id']}  |  coords: {element['lat']},{element['lon']}\n{element['tags']}\n\n"

with open("output.txt", "w+") as f:
        f.write(final) 
print("Done. Find everything in output.txt")

cursor.close()
mydb.close()