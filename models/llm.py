from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from config import OPENAI_API_KEY, GOOGLE_API_KEY, LLM_MODEL, LLM_TEMPERATURE

if GOOGLE_API_KEY:
    llm = ChatGoogleGenerativeAI(
                 model="gemini-1.5-pro",
                 temperature=LLM_TEMPERATURE,)
elif OPENAI_API_KEY:
    llm = ChatOpenAI(model=LLM_MODEL,
                 temperature=LLM_TEMPERATURE,
                 openai_api_key=OPENAI_API_KEY)
else:
    raise Exception("Error: API KEY missing. define API_KEY environment variable")