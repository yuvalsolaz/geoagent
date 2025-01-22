CONSTRUCT_GEO_QUERY_PROMPT = """
You are a GIS expert. 
Your task is to construct a free text geographic query to fetch relevant data about change detections based 
on time and geographical features 
Follow these steps to construct the query, applying logical reasoning at each step:
Your query should include combination of geographic conditions, temporal conditions location classification and open 
area conditions. In the geographic conditions use distance relations and cardinal directions.

Below are examples of Geographic queries with various scenarios:

**Example 1:**
Question: What new residential areas have appeared in Tel Aviv in the last 4 months?

**Example 2:**
Question: Show me new airports appeared in Haifa in the last 10 months?

**Example 3:**
Question: What are the 3 largest industrial areas in Be'er Sheva? Show the area of each candidate in square kilometers

**Example 4:**
Question: Are there roads in Haifa?

**Example 5:**
Question: Are there new harbors in Haifa?

**Example 6:**
Question: What highways are within 50 km of Haifa?

**Example 6:**
Question: Give me all new roads in distance of at least 5 km from Nesher but no more than 10 km

**Example 7:**
Question: Give me all the new airports in Haifa and Tel Aviv

**Example 8:**
Question: Give me polygons where there are 2 adjacent polygons of road in Haifa.

**Example 9:**
Question: What airports are there in the northern part of tel aviv ?

**Example 10:**
Question: What airports are there in the southern part of tel aviv ?

**Example 11:**
Question: What airports are there in the eastern part of tel aviv ?

**Example 12:**
Question: What airports are there in the western part of tel aviv ?

*Example 13:**
Question: What airports are there within 8 kilometers north to tel aviv ?

*Example 14:**
Question: What airports are there within 6 kilometers south to tel aviv ?

*Example 15:**
Question: What airports are there within 7 kilometers east to tel aviv ?

*Example 16:**
Question: What airports are there within 12 kilometers west to tel aviv ?

**Example 17:**
Question: What are the 5 largest industrial areas in the eastern part of Be'er Sheva ?

*Example 18:**
Question: What airports are there within 1.5 kilometers from the center of tel aviv ?

*Example 19:**
Question: What airports are there within half kilometer from the center of haifa ?

*Example 20:**
Question:  Give me all roads in a distance of kilometer from the center of Raanana ?

*Example 21:**
Question: roads within one kilometer north west to haifa ?

*Example 22:**
Question: What airports are there within 2.5 miles from the center of haifa ?

**Example 23:**
Question: Show me construction activity in Jerusalem

**Example 24:**
Question: Show me new construction activity in open areas in Jerusalem

**Example 25:**
Question: Search for airport which built recently on an Industrial area in Jerusalem 

**Example 26:**
Question: Show me new construction activity in open areas within 5 km north of Jerusalem city center

**Example 27:**
Question: Show me infrastructure changes on the eastern part of Tel Aviv in the last three months

**Example 28:**
Question: Find open areas that have been developed or converted into new built-up areas in the northern Kfar Saba area

**Example 29:**
Question: Highlight all recent land use changes from parks or recreational areas to urban developments

**Example 30:**
Question: Identify changes in the road network extending east from the Petah Tikva 

**Example 31:**
Question: Find new buildings or facilities developed in undeveloped areas within 1 km of the Israel border

**Example 32:**
Question: Identify construction expansion in the built-up area in Petah Tikva 

Remember:
- Use EXACTLY the location name provided in {input}
- Combine multiple location conditions
- Include spatial qualifiers when relevant (near, around, etc.)
- Only use locations from the provided input

Now, construct the geographic query for the given location. 
Apply the principles above and use the examples as inspiration, 

Return only the geographic query, without any formatting, comments, or additional text.

Question: {input}
"""