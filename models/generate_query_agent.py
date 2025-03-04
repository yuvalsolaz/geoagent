from langchain.agents import initialize_agent, Tool, AgentType
from typing import List
from tools import reverse_geocoding, construct_geo_query
from utils import PromptHandler
from .llm import llm

AGENT_PROMPT = """
You are a GIS expert with access to multiple tools designed to help answer geographical questions. 
Your task is to create free text geographic query based on location coordinates and date: '{user_input}' 
and respond to it using the tools appropriately.

You have access to the following tools:
    def _initialize_tools(self) -> List[Tool]:
        return [
            Tool(
                name="Reverse Geocoding Location",
                func=lambda query: reverse_geocoding(query),
                description="Extracts one location name from location coordinates. For 34.551 32.335 return haifa."
            ),
            Tool(
                name="Construct Geo Query",
                func=construct_geo_query,
                description="Creates geographic query for your locations. Use only if: Location was successfully reversed geocoded."
            )
        ]
1. **Reverse Geocoding Location**: Use this tool to find relevant location name for the input location coordinates 
2. **Construct Geo Query**: Create geographic query using input location name and date. 

Workflow:
1. Validates coordinate locations 
   If 'valid location coordinates':
    - Reverse Geocoding location (using Reverse Geocoding Location)
    - Construct geographic query based on the return location name (using Construct Geo Query):
    - Provide the geographic query as Final Answer
   Else
    - Return "Invalid location coordinates' as Final Answer  

Critical Rules:

1. Results Handling:
   - Include all returned information and the last thought
   - In case of no results founds or in reverse geocoding errors include all information in the last thought
   - Keep formatting simple and clear
   - Prefix the results with "Final Answer"

2. Tool Usage:
   - Execute one tool at a time
   - Wait for each tool's response
   - Use exact outputs as inputs for next tool
   - Do not modify tool outputs

When Providing Final Answer:
   - Include all information from Generate Geo Query
   - Format response clearly and simply
   - Show complete information for lists and details
"""


class GenerateQueryAgent:
    def __init__(self):
        self.prompt_handler = PromptHandler(llm)
        self.tools = self._initialize_tools()
        self.agent = initialize_agent(
            tools=self.tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            handle_parsing_errors=True,
            verbose=True
        )

    def _initialize_tools(self) -> List[Tool]:
        return [
            Tool(
                name="Reverse Geocoding Location",
                func=lambda query: reverse_geocoding(query),
                description="Extracts one location name from location coordinates. For 34.551 32.335 return haifa."
            ),
            Tool(
                name="Construct Geo Query",
                func=construct_geo_query,
                description="Creates geographic query for your locations. Use only if: Location was successfully reversed geocoded."
            )
        ]

    def process_input(self, user_input: str) -> str:
        formatted_prompt = self.prompt_handler.format_prompt(
            template=AGENT_PROMPT,
            user_input=user_input
        )
        result = self.agent.invoke({"input": formatted_prompt})
        return result['output']
