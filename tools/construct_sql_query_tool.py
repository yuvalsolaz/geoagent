from models.llm import llm
from config import SCHEMA_NAME, TABLE_NAME
from prompts.construct_sql_query_prompt import CONSTRUCT_SQL_QUERY_PROMPT
from utils.prompt_handler import PromptHandler
from utils.geo_state_manager import GeoStateManager 

def construct_sql_query(input_question: str) -> str:

    geo_state = GeoStateManager()
    locations = geo_state.get_location_keys()
    
    context = {
        "input": input_question,
        "schema_name": SCHEMA_NAME,
        "table_name": TABLE_NAME,
        "available_locations": locations 
    }
    
    prompt_handler = PromptHandler()
    result = prompt_handler.run_chain(
        template=CONSTRUCT_SQL_QUERY_PROMPT,
        input_variables=list(context.keys()),
        clean_output=True,
        **context
    )
    return result
