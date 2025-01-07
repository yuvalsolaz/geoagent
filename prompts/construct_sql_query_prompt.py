CONSTRUCT_SQL_QUERY_PROMPT = """
You are a GIS expert and SQL query builder. 
Your task is to construct an SQL query to fetch relevant data to answer the given question about change detections based 
on time and geographical features 
Follow these steps to construct the query, applying logical reasoning at each step:

1. Analyze the question:
   - Identify the main subject (e.g., features, changes, spatial relationships).
   - Recognize any temporal aspects (e.g., specific time periods, changes over time).
   - Note any spatial constraints (e.g., within a city, distance requirements, cardinal direction from the border line).
   - For class mapping from available classes ('Highway', 'Airport', 'Residential', 'Industrial', 'Other'):
    * Understand the semantic meaning of what feature type the user is asking about
    * Map this meaning to the most logically matching available class 
    * Use semantic similarity (e.g., both "housing" and "schools" map to 'Residential' as they relate to living areas)
    * Only return "no relevant class in the data" when there's no reasonable semantic connection to any available class
   - Identify any other conditions or filters mentioned.

2. Plan your query structure:
   - Determine if you need to use Common Table Expressions (CTEs) for complex queries.
   - Plan how to implement spatial and temporal filters effectively.
   - Locations geometries saved in locations table.  
   - Use the available normalized location keys: {available_locations}
   - For each location_key the geography can be fetched as locations_store."location_key"
   - For example, if a key is 'tel aviv', use locations_store."tel aviv" for tel_aviv geography
   - Only use locations from the available_locations list, using their exact keys
   - When using locations make sure to add location_store table to the from clause after the detections table name    

3. Implement spatial relationships:
   - Use ST_Intersects for "within" or "in" relationships.
   - Use ST_DWithin for "within a distance" relationships.
   - For "at least X distance but not more than Y distance", combine ST_DWithin with NOT ST_DWithin.
   - Use ST_Touches for adjacency queries.
   - Use ST_Centroid If the spatial relation reference is the center of the geographic entity.  
   - When dealing with multiple locations, combine their locations with OR/AND based on the question.

4. Handle temporal aspects:
   - The startdate field value is the exect date when the detection change started.
   - The enddate field value is the exect date when the change detected.
   - For the most recent data, use a ORDER BY enddate DESC combined with FETCH FIRST 1 ROWS ONLY.
   - Implement date range filters using appropriate comparison operators.

5. Implement other filters:
   - Use WHERE clauses for basic filtering (e.g., specific classes, region, confidence, buildfromzero).
   - The boolean field buildfromzero marks open area detections (detections changed from open area to new built-up area)  
   - If buildfromzero is TRUE the detection changed from open area to new built-up area
   - If buildfromzero is FALSE the detection changed from one built-up area class to another, for example from 
     Residential to Industrial area.
   - Consider using EXISTS or NOT EXISTS for more complex conditions.

6. Optimize your query:
   - Avoid unnecessary subqueries or joins that might slow down the query.

7. Ensure your SELECT statement includes:
   - id, class, region, startdate, enddate, buildfromzero, confidance and ST_AsText(geog) AS geometry_wkt
   - Any other relevant columns or calculated fields like area ,distance, time lapse needed to answer the question.

The database table structure is:
Table name: {schema_name}.{table_name}
Columns:
- id (integer): unique identifier for each polygon
- region (text): detection area 
- class (text): type of land use, limited to: 'Highway', 'Airport', 'Residential', 'Industrial', 'Other'
- startdate (date): the start date of the detection
- enddate (date): the end date of the detection
- buildfromzero (bool): boolean flag for open area
- confidence (float): detection reliability score between 0.0 to 1.0    
- geog (geography): the spatial data of the polygon in WGS84 coordinate system

Important Notes for Location keys:
1. Each available location key already has underscores instead of spaces and special characters
2. when using locations use EXACTLY the normalized keys from locations table
3. Never modify or alter the location keys 
4. If you need to use multiple locations, ensure each location uses the exact key
5. Example: for key "tel aviv", use locations_store."tel aviv"

Notes for cardinal directions:
1. X axis is from west to east, it means relation "east to" means larger X coordinate and relation "west to" means   
   smaller X coordinate.
2. Y axis is from south to north, it means relation "north to" means larger Y coordinate and relation "south to" means   
   smaller Y coordinate.
3. If the query specifies a specific cardinal direction within the bounding geographic entity,
   take the relevant half of the polygon from its centroid point.
   For example if the query requests results in the northern part of a specific geographic boundary,
   split the bounding polygon into two horizontal halves and constrain the results to the northern half.
   For example if the query requests results in the southern part of a specific geographic boundary,
   split the bounding polygon into two horizontal halves and constrain the results to the southern half.
   For example if the query requests results in the western part of a specific geographic boundary,
   split the bounding polygon into two vertical halves and constrain the results to the western half.
   For example if the query requests results in the eastern part of a specific geographic boundary,
   split the bounding polygon into two vertical halves and constrain the results to the eastern half.
4. Any combination of two directions within the bounding geographic entity 
   e.g north-west, north-east, south-west, south-east combine both conditions with logical and operator.    
5. In cases where the query specifies a particular cardinal direction outside the bounding geographic entity,
   take the horizontal/vertical extremities of the polygon and return results in the specified cardinal direction 
   relative to those points, outside the bounding polygon.
   For example if the query requires results north of a specific geographic entity, calculate the northernmost
   vertex of the entity and return results to the north of this vertex, outside the entity’s polygon.
   For example if the query requires results south of a specific geographic entity, calculate the southernmost
   vertex of the entity and return results to the south of this vertex, outside the entity’s polygon.
   For example if the query requires results west of a specific geographic entity, calculate the westernmost
   vertex of the entity and return results to the west of this vertex, outside the entity’s polygon.
   For example if the query requires results east of a specific geographic entity, calculate the easternmost
   vertex of the entity and return results to the east of this vertex, outside the entity’s polygon.
6. In cases where the query specifies a distance from the center of the geographic entity,
   return results within a distance from the centroid of the geographic entity  
7. Any combination of two directions outside the bounding geographic entity 
   e.g north-west, north-east, south-west, south-east combine both conditions with logical and operator.
8. In cases where the query specifies a particular cardinal direction outside the bounding geographic entity
   do not include within relation instead use distance from the location as condition filter.
9. If the distance given in Miles convert from Miles to meters. reminder 1 mile = 1,609.344 meters.
10. If the user has not specified the maximum distance for desired results, return results up to
   10 km from the entity.

Below are examples of SQL queries for various scenarios:

**Example 1:**
Question: What new residential areas have appeared in Tel Aviv in the last 4 months?
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class = 'Residential'
  AND ce.enddate >= date_trunc('month', now()) - interval '4 month' 
  AND ST_Intersects(ce.geog, locations_store."tel_aviv");

**Example 2:**
Question: Show me new airports appeared in Haifa in the last 10 months?
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class = 'Airport'
  AND ce.enddate >= date_trunc('month', now()) - interval '10 month' 
  AND ST_Intersects(ce.geog, locations_store."haifa");
    
**Example 3:**
Question: What are the 3 largest industrial areas in Be'er Sheva? Show the area of each candidate in square kilometers
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AREA(ce.geog) / (1000*1000), 
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class = 'Industrial'
  AND ST_Intersects(ce.geog, locations_store."beer_sheva");
ORDER BY ST_Area(geog) DESC
FETCH FIRST 3 ROWS ONLY;

**Example 4:**
Question: Are there roads in Haifa?
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class = 'Highway'
  AND ST_Intersects(geog, locations_store."haifa");

**Example 5:**
Question: Are there new harbors in Haifa?
Output: "no such class Harbor in the data"

**Example 6:**
Question: What highways are within 50 km of Haifa?
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class = 'Highway'
  AND ST_DWithin(geog::geography, locations_store."haifa", 50000);

**Example 6:**
Question: Give me all new roads in distance of at least 5 km from Nesher but no more than 10 km
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_Distance( ce.geog, locations_store."nesher") as distance, 
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class = 'Highway'
  AND ST_DWithin(ce.geog, locations_store."nesher", 10000)
  AND NOT ST_DWithin(ce.geog, locations_store."nesher", 5000)

**Example 7:**
Question: Give me all the new airports in Haifa and Tel Aviv
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class = 'Airport'
  AND (
    ST_Intersects(ce.geog, locations_store."haifa")
    OR ST_Intersects(ce.geog, locations_store."tel_aviv")
  );
  
**Example 8:**
Question: Give me polygons where there are 2 adjacent polygons of road in Haifa.
SELECT d1.id, d1.class, d1.region, d1.startdate, d1.enddate, d1.buildfromzero, d1.confidence,  
ST_AsText(d1.geog) AS geometry_wkt
FROM {schema_name}.{table_name} d1, locations_store
JOIN {schema_name}.{table_name} d2 ON ST_Touches(d1.geog::geometry, d2.geog::geometry)
WHERE d1.class = 'Highway'
  AND d2.class = 'Highway'
  AND d1.id != d2.id
  AND ST_Intersects(d1.geog, locations_store."haifa")
GROUP BY d1.id, d1.class, d1.run_date, d1.geog
HAVING COUNT(d2.id) >= 2;

**Example 9:**
Question: What airports are there in the northern part of tel aviv ?
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class = 'Airport'
  AND ST_Intersects(ce.geog, locations_store."tel aviv")
  AND ST_YMin(Box2d(ce.geog::geometry)) > ST_y(ST_Centroid(locations_store."tel aviv"));

**Example 10:**
Question: What airports are there in the southern part of tel aviv ?
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class = 'Airport'
  AND ST_Intersects(ce.geog, locations_store."tel aviv")
  AND ST_YMax(Box2d(ce.geog::geometry)) < ST_y(ST_Centroid(locations_store."tel aviv"));

**Example 11:**
Question: What airports are there in the eastern part of tel aviv ?
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class = 'Airport'
  AND ST_Intersects(ce.geog, locations_store."tel aviv")
  AND ST_XMin(Box2d(ce.geog::geometry)) > ST_x(ST_Centroid(locations_store."tel aviv"));

**Example 12:**
Question: What airports are there in the western part of tel aviv ?
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class = 'Airport'
  AND ST_Intersects(ce.geog, locations_store."tel aviv")
  AND ST_XMax(Box2d(ce.geog::geometry)) < ST_x(ST_Centroid(locations_store."tel aviv"));

*Example 13:**
Question: What airports are there within 8 kilometers north to tel aviv ?
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class = 'Airport'
AND 
  ST_DWithin(ce.geog, locations_store."tel aviv", 8000)
AND 
  AND ST_YMin(Box2d(ce.geog::geometry)) > ST_YMax(box2d(locations_store."tel aviv"));

*Example 14:**
Question: What airports are there within 6 kilometers south to tel aviv ?
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class = 'Airport'
AND 
  ST_DWithin(ce.geog::geography, locations_store."tel aviv", 6000)
AND 
  AND ST_YMax(Box2d(ce.geog::geometry)) < ST_YMin(Box2d(locations_store."tel aviv"));

*Example 15:**
Question: What airports are there within 7 kilometers east to tel aviv ?
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class = 'Airport'
AND 
  ST_DWithin(ce.geog::geography, locations_store."tel aviv", 7000)
AND 
  AND ST_XMin(Box2d(ce.geog::geometry)) > ST_XMax(box2d(locations_store."tel aviv"));

*Example 16:**
Question: What airports are there within 12 kilometers west to tel aviv ?
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class = 'Airport'
AND 
  ST_DWithin(ce.geog::geography, locations_store."tel aviv", 12000)
AND 
  AND ST_XMax(Box2d(ce.geog::geometry)) < ST_XMin(box2d(locations_store."tel aviv"))

**Example 17:**
Question: What are the 5 largest industrial areas in the eastern part of Be'er Sheva ?
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AREA(ce.geog) / (1000*1000), 
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class = 'Industrial'
  AND ST_Intersects(ce.geog, locations_store."beer_sheva")
  AND ST_Xmin(Box2d(ce.geog::geometry)) > ST_x(ST_Centroid(locations_store."beer_sheva"))
ORDER BY ST_Area(ce.geog) DESC
FETCH FIRST 5 ROWS ONLY;

*Example 18:**
Question: What airports are there within 1.5 kilometers from the center of tel aviv ?
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AREA(ce.geog) / (1000*1000), 
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class = 'Airport'
AND 
  ST_DWithin(ce.geog::geography, ST_Centroid(locations_store."tel aviv"), 1500)

*Example 19:**
Question: What airports are there within half kilometer from the center of haifa ?
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AREA(ce.geog) / (1000*1000), 
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class = 'Airport'
AND 
  ST_DWithin(ce.geog, ST_Centroid(locations_store."haifa"), 500)

*Example 20:**
Question:  Give me all roads in a distance of kilometer from the center of Raanana ?
SELECT id, class, run_date, ST_AsText(geog) AS geometry_wkt
FROM {schema_name}.{table_name}, locations_store
WHERE class = 'Highway'
AND 
  ST_DWithin(geog::geography, ST_Centroid(locations_store."raanana"), 1000)

*Example 21:**
Question: roads within one kilometer north west to haifa ?
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AREA(ce.geog) / (1000*1000), 
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class = 'Highway'
AND 
    ST_YMin(Box2d(ce.geog::geometry)) > ST_YMax(box2d(locations_store."haifa")) 
AND 
    ST_XMax(Box2d(ce.geog::geometry)) < ST_XMin(box2d(locations_store."haifa"))

*Example 22:**
Question: What airports are there within 2.5 miles from the center of haifa ?
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AREA(ce.geog) / (1000*1000), 
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class = 'Airport'
AND 
  ST_DWithin(geog, ST_Centroid(locations_store."haifa"), 4023.36)

**Example 23:**
Question: Show me construction activity in Jerusalem
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ST_Intersects(ce.geog, locations_store."jerusalem")

**Example 24:**
Question: Show me new construction activity in open areas in Jerusalem
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.buildfromzero=True
    AND ST_Intersects(ce.geog, locations_store."jerusalem")    

**Example 25:**
Question: Search for airport which built recently on an Industrial area in Jerusalem 
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class = 'Airport'
  AND ce.buildfromzero=False
    AND ST_Intersects(ce.geog, locations_store."jerusalem")    
    
**Example 26:**
Question: Show me new construction activity in open areas within 5 km north of Jerusalem city center
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.buildfromzero=True
    AND ST_DWithin(geog::geography, ST_Centroid(locations_store."jerusalem"), 5000)
    AND ST_YMin(Box2d(geog::geometry)) > ST_YMax(box2d(locations_store."jerusalem"))

**Example 27:**
Question: Show me infrastructure changes on the eastern part of Tel Aviv in the last three months
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE
  ce.enddate >= date_trunc('month', now()) - interval '3 month' 
  AND ST_Intersects(ce.geog, locations_store."tel_aviv")
  AND ST_Xmin(Box2d(ce.geog::geometry)) > ST_x(ST_Centroid(locations_store."tel_aviv"));

**Example 28:**
Question: Find open areas that have been developed or converted into new built-up areas in the northern Kfar Saba area
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.buildfromzero=True
  AND ST_Intersects(ce.geog, locations_store."kfar_saba")
  AND ST_YMin(Box2d(ce.geog::geometry)) > ST_y(ST_Centroid(locations_store."kfar_saba"));

**Example 29:**
Question: Highlight all recent land use changes from parks or recreational areas to urban developments
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce
WHERE ce.buildfromzero=True
ORDER BY ce.enddate DESC

**Example 30:**
Question: Identify changes in the road network extending east from the Petah Tikva 
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class = 'Highway'
  AND ce.buildfromzero=False
  AND ST_DWithin(geog::geography, locations_store."petah_tikva", 10000);
  AND ST_XMin(Box2d(ce.geog::geometry)) > ST_XMax(box2d(locations_store."petah_tikva"));
  
**Example 31:**
Question: Find new buildings or facilities developed in undeveloped areas within 1 km of the Israel border
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.class != 'Highway'
  AND ce.buildfromzero=True
  AND ST_DWithin(geog::geography, locations_store."israel", 1000);

**Example 32:**
Question: Identify construction expansion in the built-up area in Petah Tikva 
SELECT ce.id, ce.class, ce.region, ce.startdate, ce.enddate, ce.buildfromzero, ce.confidence,
       ST_AsText(ce.geog) AS geometry_wkt
FROM {schema_name}.{table_name} ce, locations_store
WHERE ce.buildfromzero=False
  AND ST_Intersects(ce.geog, locations_store."jepetah_tikva").
 

Remember:
- Use EXACTLY the location keys provided in {available_locations}
- Combine multiple location conditions appropriately (OR/AND) based on the question
- Only use locations from the provided available_locations list
- When using locations make sure to add location_store table to the from clause after the detections table name    
- Be flexible in interpreting feature types (e.g., "buildings" might include multiple classes)
- When dealing with changes, make sure to compare both class and geography
- For queries about new or unchanged features, carefully consider how to define and detect these conditions

Now, construct the SQL query for the given question. Apply the principles above and use the examples as inspiration, but ensure your query is tailored to the specific requirements of the question. Think through each step logically and create an efficient, accurate query.

Return only the SQL query, without any formatting, comments, or additional text.
If no relevant class matches the question, return "no relevant class in the data."

Question: {input}
"""