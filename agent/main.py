import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain.agents import initialize_agent, AgentType
from langchain_community.agent_toolkits.openapi.toolkit import RequestsToolkit
from langchain_community.utilities.openapi import OpenAPISpec
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# -----------------------------
# Pydantic v2 Compatibility Patch
# -----------------------------
# This fixes the 'super' object has no attribute 'parse_obj' error
if not hasattr(OpenAPISpec, "parse_obj"):
    def parse_obj(cls, obj):
        return cls.model_validate(obj)
    OpenAPISpec.parse_obj = classmethod(parse_obj)

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Best practice: Change to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# File Path Setup (Fix for deployment)
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OPENAPI_PATH = os.path.join(BASE_DIR, "wotnot_openapi.json")

if not os.path.exists(OPENAPI_PATH):
    raise FileNotFoundError(f"The 'wotnot_openapi.json' file was not found at {OPENAPI_PATH}")

# -----------------------------
# Environment Variable Checks
# -----------------------------
required_env_vars = [
    "OPENAI_API_KEY"
]
missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# -----------------------------
# Agent 1: OpenAPI agent (WotNot with OpenAI GPT)
# -----------------------------
try:
    with open(OPENAPI_PATH, "r") as f:
        openapi_raw = f.read()

    spec = OpenAPISpec.from_text(openapi_raw)
    # The base URL is often specified in the spec, but can be overridden
    # spec.base_url = "https://api.wotnot.io" 

    requests_toolkit = RequestsToolkit(spec=spec)
    tools = requests_toolkit.get_tools()

    llm_agent = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0.2,
        openai_api_key=os.environ.get("OPENAI_API_KEY")
    )

    agent = initialize_agent(
        tools=tools,
        llm=llm_agent,
        agent=AgentType.OPENAI_FUNCTIONS, 
        verbose=True
    )
except Exception as e:
    raise RuntimeError(f"Failed to initialize the WotNot agent: {e}") from e


@app.post("/run-agent/")
async def run_agent(request: Request):
    body = await request.json()
    prompt = body.get("prompt")
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required.")
    
    try:
        result = agent.invoke({"input": prompt})
        return {"response": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

# -----------------------------
# Agent 2: Diwali Greeting (OpenAI GPT)
# -----------------------------
try:
    llm_greeting = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0.7,
        openai_api_key=os.environ.get("OPENAI_API_KEY")
    )
except Exception as e:
    raise RuntimeError(f"Failed to initialize the OpenAI model: {e}") from e

@app.post("/diwali-greet/")
async def diwali_greeting(request: Request):
    body = await request.json()
    name = body.get("name", "Friend")
    
    prompt = f"Write a short, warm, festive Diwali greeting message for {name}."
    
    try:
        message = HumanMessage(content=prompt)
        greeting_response = llm_greeting.invoke([message])
        return {"greeting": greeting_response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greeting generation failed: {str(e)}")
