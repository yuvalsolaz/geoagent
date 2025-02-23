import json
import geopandas as gpd
from shapely import wkt
from config import SIMPLIFY_SHAPE_TOLERANCE
from utils.geo_state_manager import GeoStateManager
from utils import PostgresHandler

geo_state = GeoStateManager()


def clean_sql_query(query: str) -> str:
    """Clean SQL query by removing unnecessary quotes and whitespace"""
    # Remove outer quotes if they exist
    # query = query.strip('"\'') ## create errors
    # Remove extra whitespace
    query = ' '.join(query.split())
    # Remove any trailing semicolons and quotes
    query = query.rstrip(';"\'')
    # Remove any escaped quotes
    query = query.replace('\\"', '"').replace("\\'", "'")
    return query


def build_locations_sql(_geo_state: GeoStateManager):
    epsg = '4326'
    geometries = _geo_state.get_geometries()
    locations = _geo_state.get_location_keys()
    # Simplify the geometries (optional)
    if SIMPLIFY_SHAPE_TOLERANCE > 0.0:
        for loc in locations:
            geometries[loc] = [g.simplify(SIMPLIFY_SHAPE_TOLERANCE, preserve_topology=True) for g in geometries[loc]]

    # geometry union option:
    union_list = []
    for loc in locations:
        union_list.append(
        " ST_Union(ARRAY[" + ",".join(
            [f'''ST_MakeValid(ST_GeomFromText('{geom.wkt}','{epsg}')) ''' for geom in geometries[loc]]) + "]) " + f''' as "{loc}" '''
        )
    location_queries = " , ".join(union_list)

    locations_sql = f'''
        with locations_store as (
                select 
                    {location_queries}
            )
        '''

    print(f'\nlocations sql: {locations_sql}')
    return locations_sql


def execute_sql_query(query: str) -> str:
    query = clean_sql_query(query)
    try:
        with PostgresHandler() as db:
            locations_sql = build_locations_sql(_geo_state=GeoStateManager())
            result = db.execute_query(f'{locations_sql}  {query}')
            if result["status"] != "success":
                return json.dumps(result, indent=2)

            gdf = gpd.GeoDataFrame(result["data"])
            gdf['geom'] = gdf['geometry_wkt'].apply(wkt.loads)
            gdf = gdf.set_geometry('geom')
            gdf = gdf.set_crs(epsg=4326)

            geo_state.set_gdf(gdf)

            total_results = len(result['data'])
            max_display = 10

            response = f"Total results found: {total_results}\n\n"

            if total_results > 0:
                columns = [k for k in result['data'][0].keys() if k != 'geometry_wkt']

                for i, row in enumerate(result['data'][:max_display], 1):
                    items = [f"{col}: {row[col]}" for col in columns]
                    response += f"{i}. {', '.join(items)}\n"

                if total_results > max_display:
                    response += f"\n... and {total_results - max_display} more results\n"

            return response.strip()

    except Exception as e:
        return f"An error occurred while executing the query: {str(e)}"
