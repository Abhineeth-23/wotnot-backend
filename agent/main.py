import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain.agents import create_openapi_agent
from langchain_community.agent_toolkits.openapi.spec import OpenAPISpec
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

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
# File Path Setup
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OPENAPI_PATH = os.path.join(BASE_DIR, "wotnot_openapi.json")

if not os.path.exists(OPENAPI_PATH):
    raise FileNotFoundError(f"The 'wotnot_openapi.json' file was not found at {OPENAPI_PATH}")

# -----------------------------
# Environment Variable Checks
# -----------------------------
if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError("Missing required environment variable: OPENAI_API_KEY")

# -----------------------------
# Agent 1: OpenAPI agent (WotNot with OpenAI GPT) - NEW METHOD
# -----------------------------
try:
    with open(OPENAPI_PATH, "r") as f:
        openapi_raw = f.read()

    spec = OpenAPISpec.from_text(openapi_raw)

    llm_agent = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0.2,
        openai_api_key=os.environ.get("OPENAI_API_KEY")
    )

    # This is the new, more robust way to create the agent
    agent = create_openapi_agent(
        llm=llm_agent,
        spec=spec,
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
        # Note: The input format for invoke might differ slightly with the new agent.
        # We start with the standard way.
        result = agent.invoke({"input": prompt})
        return {"response": result.get("output")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

# -----------------------------
# Agent 2: Diwali Greeting (OpenAI GPT) - No changes needed here
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

@app.get("/")
def read_root():
    return {"status": "AI backend is running"}
