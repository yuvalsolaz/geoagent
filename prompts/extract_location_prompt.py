EXTRACT_LOCATION_PROMPT = """
Extract location references from the text. Add type specification ONLY if the exact words 'street', 'city', 'county', 'state', 'border' or 'country' appear as part of the location name in the original text.

Rules:
1. NEVER infer or assume a type
2. Add type ONLY if one of these exact words appears: 'street', 'city', 'county', 'state', 'border', 'country'
3. Do not include spatial qualifiers (near, around, in, part of, area of, northern, western, southern, eastern, within etc ) 
if present

Examples to show correct extraction:
"give me all highways in Haifa" should return:
haifa

"airports in haifa and tel aviv city" should return:
haifa
tel aviv|type:city

"find streets near hanita street and herzliya" should return:
hanita|type:street
herzliya

"show me data for ramat gan city and tel aviv" should return:
ramat gan|type:city
tel aviv

"changes in haifa state and tel aviv city" should return:
haifa|type:state
tel aviv|type:city

"show me airports in northern haifa city" should return:
haifa|type:city

"find airports near Lebanon border" should return:
Lebanon|type:border

"show me roads near the coastline of Israel" should return:
Israel|type:border

"find buildings within 3 km from the border line of Lebanon" should return:
Lebanon|type:border

Your response for this text: {question}
Return only the extracted locations, one per line. Do not add type unless the exact type word is present in the original text.
"""