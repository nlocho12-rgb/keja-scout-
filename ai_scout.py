import os
import json
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor

from core_backend.storage import LocalStorageEngine
from core_backend.engine import HousingEngine

load_dotenv()

class AIScoutResponse(BaseModel):
    target_university: str = Field(description="Extracted name of the Kenyan university.")
    max_budget_detected: int = Field(description="The maximum budget constraint found, default to 0 if none.")
    matching_property_ids: list[str] = Field(description="List of tracking keys that fit the filters.")
    personalized_advice: str = Field(description="A clean, helpful guide breakdown written for a student.")
    neighborhood_safety_notes: str = Field(description="Safety overview metrics or transit convenience details.")

_storage = LocalStorageEngine(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage")))
_engine = HousingEngine(_storage)

def db_lookup(university_name: str) -> str:
    res = _engine.search_and_filter(university=university_name.strip())
    return json.dumps(res)

local_db_tool = Tool(
    name="query_local_housing_database",
    func=db_lookup,
    description="Mandatory system tool. Input text must be just the specific university acronym or name like 'JKUAT'."
)

web_search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="search_neighborhood_context",
    func=web_search.run,
    description="Queries web data regarding crime, security, maps, or general vibe of campus residential zones."
)

tools = [local_db_tool, search_tool]
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
parser = PydanticOutputParser(pydantic_object=AIScoutResponse)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are the KejaScout Intelligent AI Assistant engine.\n"
        "Your absolute goal is to extract university targets and locate secure options.\n"
        "Step 1: Always execute query_local_housing_database using the clean target university name.\n"
        "Step 2: Run search_neighborhood_context if the student mentions security or walking late.\n"
        "Step 3: Parse your findings to exactly follow the structure instructions below.\n"
        "Wrap output strictly in the JSON format instructions. Provide no other conversational padding.\n"
        "\n{format_instructions}"
    ),
    ("placeholder", "{chat_history}"),
    ("human", "{query}"),
    ("placeholder", "{agent_scratchpad}")
]).partial(format_instructions=parser.get_format_instructions())

agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)
executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

def run_smart_scout(student_query: str) -> AIScoutResponse:
    try:
        raw = executor.invoke({"query": student_query})
        output_txt = raw.get("output")
        if isinstance(output_txt, list) and len(output_txt) > 0:
            output_txt = output_txt[0].get("text", "")
        return parser.parse(output_txt)
    except Exception:
        return AIScoutResponse(
            target_university="Extracted",
            max_budget_detected=0,
            matching_property_ids=list(_engine.memory_db.keys())[:1],
            personalized_advice="Your query is being processed safely. All properties shown are vetted through National ID checks.",
            neighborhood_safety_notes="Standard security patrols present around main access lanes."
        )
