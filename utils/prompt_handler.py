# utils/prompt_handler.py
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms.base import BaseLLM
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class PromptHandler:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, llm: Optional[BaseLLM] = None):
        if not self._initialized:
            if llm is None:
                raise ValueError("LLM must be provided for initial initialization")
            self.llm = llm
            self._initialized = True

    def run_chain(self, 
                  template: str, 
                  input_variables: List[str],
                  clean_output: bool = False,
                  **kwargs) -> str:
        """Run a chain with the given template and variables"""
        try:
            prompt = PromptTemplate(
                input_variables=input_variables,
                template=template
            )
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.run(**kwargs)
            
            if clean_output:
                result = result.replace("\\n", " ").replace("\n", " ").strip()
                
            return result
            
        except Exception as e:
            logger.error(f"Error running prompt: {e}")
            raise

    def format_prompt(self, template: str, **kwargs) -> str:
        """Simply format a prompt template with variables"""
        try:
            return template.format(**kwargs)
        except Exception as e:
            logger.error(f"Error formatting prompt: {e}")
            raise