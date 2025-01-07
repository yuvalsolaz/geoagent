DETECT_LOCATION_PROMPT = """
    Analyze the following question or statement and determine if it SYNTACTICALLY references or implies any location, regardless of whether you recognize the place name or if it's a real location.

    Return 'location' if:
    - The text contains phrases like "in", "at", "near", "around" followed by any name
    - The context suggests a place is being referenced (even if the name is unfamiliar or nonsensical)
    - Any word or phrase is used in a way that implies it's a location name
    
    Examples:
    - "airports in gkjfdj" -> location (because "in gkjfdj" implies gkjfdj is a location)
    - "roads near xyzabc" -> location (because "near xyzabc" implies xyzabc is a location)
    - "all buildings" -> no_location (no location reference)
    - "changes in residential areas" -> no_location (generic area, not specific location)
    
    Text: {question}
    Return only 'location' or 'no_location', without any additional text or explanation.
    """

