from utils.prompt_handler import PromptHandler
from prompts.extract_location_prompt import EXTRACT_LOCATION_PROMPT

def extract_location(question: str) -> str:
    prompt_handler = PromptHandler()
    result = prompt_handler.run_chain(
        template=EXTRACT_LOCATION_PROMPT,
        input_variables=["question"],
        question=question
    )
    return result

