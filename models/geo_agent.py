from langchain.agents import initialize_agent, Tool, AgentType
from typing import List, Dict, Any
from tools import detect_location, extract_location, process_location_query, construct_sql_query, execute_sql_query
from utils.geo_state_manager import GeoStateManager
from prompts.agent_prompt import AGENT_PROMPT
from utils import PromptHandler
from .llm import llm


class GeoAgent:
    def __init__(self):
        self.geo_state = GeoStateManager()
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
                name="Detect Location",
                func=detect_location,
                description="Determines if a query syntactically references a location. Returns 'location' or 'no_location'. Use this first to decide workflow path."
            ),
            Tool(
                name="Extract Location",
                func=extract_location,
                description="Extracts location references, one per line for multiple locations. For 'airports in haifa and tel aviv' returns 'haifa' and 'tel aviv' on separate lines."
            ),
            Tool(
                name="Process Location Query",
                func=process_location_query,
                description="Geocodes a single location and stores its geometries. For multiple locations, use this tool separately for each location. Stop workflow if any location fails."
            ),
            Tool(
                name="Construct SQL Query",
                func=construct_sql_query,
                description="Creates SQL query for your request. Use only if: 1) No location was mentioned, or 2) Location was successfully geocoded. Never write queries manually."
            ),
            Tool(
                name="Execute SQL Query",
                func=lambda query: execute_sql_query(query),
                description="Runs the SQL query and returns results. Use EXACTLY the query string returned by Construct SQL Query, without any modifications."
            )
        ]

    def process_input(self, user_input: str) -> str:
        self.geo_state.reset()
        formatted_prompt = self.prompt_handler.format_prompt(
            template=AGENT_PROMPT,
            user_input=user_input
        )
        result = self.agent.invoke({"input": formatted_prompt})
        return result['output']
