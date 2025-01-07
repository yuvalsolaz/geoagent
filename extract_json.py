import sys
import json
import csv
import random
import geopandas as gpd

from sqlalchemy import create_engine, text
from config import DB_CONNECTION_STRING, SCHEMA_NAME, TABLE_NAME

engine = create_engine(DB_CONNECTION_STRING)

from datetime import datetime


# Extract start and end dates
def extract_start_end_date(input_file):
    with open(input_file, 'r') as file:
        geojson_data = json.load(file)

    start_dates = []
    end_dates = []
    date_format = '%Y-%m-%dZ'

    for feature in geojson_data['features']:
        # Convert dates from string to datetime
        start_date = datetime.strptime(feature['properties']['startdate'], date_format)
        end_date = datetime.strptime(feature['properties']['enddate'], date_format)
        start_dates.append(start_date)
        end_dates.append(end_date)

    # Find minimum and maximum dates
    min_date = min(start_dates)
    max_date = max(end_dates)
    print("Minimum date:", min_date.date())
    print("Maximum date:", max_date.date())


# mapping between input change detection geojson file to output events:
def detections_mapping(gdf: gpd.GeoDataFrame):
    detections = []
    for _, row in gdf.iterrows():
        # copy original record as is:
        before_record = dict(row)

        # create record for the change
        record = dict(row)
        record['class'] = random.choice(['Airport', 'Highway', 'Residential', 'Industrial', 'Other'])
        record['run_date'] = row['enddate']
        detections.append(record)

    return gpd.GeoDataFrame(detections)


# Extract detections geojson file and create events dataframe:
def geojson2dataframe(geojson_file: str):
    try:
        # Read the GeoJSON file using GeoPandas
        gdf = gpd.read_file(geojson_file)

        # Map to database records
        return detections_mapping(gdf)
    except Exception as ex:
        print(f'Error extracting input file:{geojson_file}: {ex}')


def update_table(gdf: gpd.GeoDataFrame, schema, table_name):
    try:
        print(f'Writing {gdf.shape[0]} records to {schema}.{table_name}')
        gdf.to_postgis(con=engine, name=table_name, schema=schema, if_exists='replace', index=False)
        print(f'data saved successfully')

        print(f'creating indexes for {schema}.{table_name}')
        with engine.connect() as conn:
            # add geography column:
            conn.execute(text(f"alter table {schema}.{table_name} add column geog geography;"))

            # update geography column:
            conn.execute(text(f"update {schema}.{table_name} set geog=geography(st_transform(ST_SetSRID(geometry, 4326), 4326));"))

            # Add a spatial geographic index (optional but recommended for performance)
            conn.execute(text(f"CREATE INDEX idx_{table_name}_geog ON {schema}.{table_name} USING GIST (geog);"))

            # Add index on the unique id
            conn.execute(text(f"CREATE INDEX detections_id_idx ON {schema}.{table_name} USING btree (id);"))

            # Add index on start/end date
            conn.execute(text(f"CREATE INDEX detections_startdate_idx ON {schema}.{table_name} USING btree (startdate);"))
            conn.execute(text(f"CREATE INDEX detections_enddate_idx ON {schema}.{table_name} USING btree (enddate);"))
            conn.commit()
        print('Indexes created')

    except Exception as ex:
        print(f'Error writing to {schema}.{table_name}: {ex}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'usage: python {sys.argv[0]} <input file>')
        exit(1)
    input_file = sys.argv[1]
    extract_start_end_date(input_file=input_file)
    gdf = geojson2dataframe(geojson_file=input_file)
    print(f'{gdf.shape[0]} records extracted. saving to table: {SCHEMA_NAME}.{TABLE_NAME} ')
    update_table(gdf=gdf, schema=SCHEMA_NAME, table_name=TABLE_NAME)
