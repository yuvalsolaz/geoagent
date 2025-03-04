from prompts.construct_geo_query_prompt import CONSTRUCT_GEO_QUERY_PROMPT
from utils.prompt_handler import PromptHandler

def construct_geo_query(input_location: str) -> str:
    context = {
        "input": input_location,
    }

    prompt_handler = PromptHandler()
    result = prompt_handler.run_chain(
        template=CONSTRUCT_GEO_QUERY_PROMPT,
        input_variables=context,
        clean_output=True,
        **context
    )
    return result
