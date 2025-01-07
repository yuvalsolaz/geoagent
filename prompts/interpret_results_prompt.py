INTERPRET_RESULTS_PROMPT = """
Analyze the following user query, SQL query, and SQL query results:

{combined_input}

Consider the following:
1. The SQL query was constructed based on the user's request, so it may reflect new entries, historical data, or other filtered information based on the query.
2. The 'id' field is a unique identifier for each polygon in the area of interest.
3. The 'class' field indicates the classification of the polygon in that particular run.
4. The 'run_date' shows when the classification was performed.
5. Each row represents data relevant to the user's request (e.g., new entries, historical changes, etc.).

Provide a clear, concise answer based on these results. Focus on:
- The classification and state of polygons.
- The most recent or relevant data (based on the user's query).
- The date range of changes or classifications.
"""