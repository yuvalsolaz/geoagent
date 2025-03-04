from geopy.geocoders import Nominatim
import geopy
from shapely.geometry import Point, shape
from psycopg2 import connect, Error
import geopandas as gpd
from utils.geo_state_manager import GeoStateManager
from utils import GeoDatabase
from utils import clean_text
from config import REGION, GEO_DATA_DIR
import re
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

geo_state = GeoStateManager()

geo_database = GeoDatabase(GEO_DATA_DIR)

def geocode_location(query):
    geolocator = Nominatim(user_agent="your-application-name")
    try:
        locations = geolocator.geocode(query=query, exactly_one=False, timeout=10, geometry='geojson')
        if not locations:
            return []

        print("locations:")
        print("\n".join([f"{l.raw['name']} : {l.raw['addresstype']}" for l in locations]))

        return [shape(loc.raw['geojson']) for loc in locations]

    except Exception as e:
        logger.error(f"Error in geocoding: {str(e)}")
        return []

def geocode_bodrer(query):
    try:
        geometry = geo_database.get_geometry(query)
        return [geometry] if geometry else []

    except Exception as e:
        logger.error(f"Error in geocoding: {str(e)}")
        return []

def reverse_geocoding(query):

    '''
    zoom	address detail
    ---------------------------
    3	country
    5	state
    8	county
    10	city
    12	town / borough
    13	village / suburb
    14	neighbourhood
    15	any settlement
    16	major streets
    17	major and minor streets
    18 building
    '''

    geolocator = Nominatim(user_agent="your-application-name")
    try:
        p = geopy.point.Point(clean_text(query))
        point = geopy.point.Point(p.longitude, p.latitude)
        location_names = geolocator.reverse(point, exactly_one=True, addressdetails=False, zoom=15, language='en'
        , timeout=10)
        if not location_names:
            return ''

        print(f"locations: {location_names}")
        return location_names.raw['name']

    except Exception as e:
        logger.error(f"Error in reverse geocoding: {str(e)}")
        return []

def process_location_query(location_input: str) -> dict:
    try:
        location_input = clean_text(location_input)

        if '|type:' in location_input:
            location_parts = location_input.split('|type:', 1)
            location_name = location_parts[0].strip()
            location_type = location_parts[1].strip()
            if location_type in ['border']:
                geometries = geocode_bodrer(query=location_name)
            else:
                query = f"{location_name} {location_type}" #{location_type: location_name}
                if REGION:
                    # query.update({"country": REGION})
                    query += f" {REGION}"

                geometries = geocode_location(query=query)
        else:
            # query = {"country": REGION, "query":location_input} if REGION else location_input
            query = f"{location_input} {REGION}"
            geometries = geocode_location(query=query)
        
        if geometries:
            geo_state.set_geometries(location_input, geometries)
            return {
                "status": "success",
                "location_query": location_input,
                "num_results": len(geometries),
                "message": "Geometries stored successfully"
            }
        else:
            return {
                "status": "error",
                "location_query": location_input,
                "num_results": 0,
                "message": "No geometries found"
            }
            
    except Exception as e:
        logger.error(f"Error processing location query: {str(e)}")
        return {
            "status": "error",
            "location_query": location_input,
            "num_results": 0,
            "message": f"Error processing query: {str(e)}"
        }
