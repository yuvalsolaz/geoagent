# GeoAgent

## DB Creation
## extract events from detection geojson file to postgres table:
### python extract_json.py data/detection_polygons.json
### NOTES 
1. The script will create new table with schema & table_name from config.py module  
2. If the table exists the script will add/update the records to the existing table (based on record values)
3. after loading the records the script creates indexes on geography ,id and date fields (for improved performances):
4. The script will create 1 change detection event for each detection in the input file.
5. Class field value for "change events" randomly sampled from Airport Highway Residential Industrial or Other classes
6. The classification date ("run date" column) will be set as the end date for each detection 

# Borderlines geodata creation:
The borderlines vector data downloaded from:
[Cartography Vectors](https://cartographyvectors.com)
Cartograhy Vectors is the trusted site for providing quality mapping vectors in all the popular formats, 
including KML, GeoJSON, SVG, EPS, SHP, PNG, and more.
© 2024 Cagle Online Enterprises, Inc.

One geojson file downloaded into the geo data directory for each borderline. 

On service startup all geojson files are loaded into the geo database object.

The geometry boundary for each geojson file stored in the geo database as a linestring with the NAME_EN attribute as 
the boundary key  

Currently there are 4 borderlines geojson files in the default geodata directory (data/borderline):

Israel, Lebanon, Syria & Jorden

New borderlines can be added as geojson files with NAME_EN attribute to the geo data directory


## Running the Geographic Query Interface:
### python gradio_chat.py

## Then open browser with the interface url: 
- [ ] [Geographic Query Interface](http://localhost:7866)
- 


