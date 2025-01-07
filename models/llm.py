from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY, LLM_MODEL, LLM_TEMPERATURE


llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE, openai_api_key=OPENAI_API_KEY)
