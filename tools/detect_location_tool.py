from utils.prompt_handler import PromptHandler
from prompts.detect_location_prompt import DETECT_LOCATION_PROMPT

def detect_location(question: str) -> str:
    prompt_handler = PromptHandler()
    result = prompt_handler.run_chain(
        template=DETECT_LOCATION_PROMPT,
        input_variables=["question"],
        question=question
    )
    return result

