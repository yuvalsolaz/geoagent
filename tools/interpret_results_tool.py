from utils.prompt_handler import PromptHandler
from prompts.interpret_results_prompt import INTERPRET_RESULTS_PROMPT

def interpret_results(combined_input: str) -> str:
    prompt_handler = PromptHandler()
    result = prompt_handler.run_chain(
        template=INTERPRET_RESULTS_PROMPT,
        input_variables=["combined_input"],
        combined_input=combined_input
    )
    return result


