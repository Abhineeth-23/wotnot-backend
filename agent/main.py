import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.llms import Bedrock
from langchain.agents import initialize_agent, AgentType
from langchain_community.agent_toolkits.openapi.toolkit import RequestsToolkit
from langchain_community.utilities.openapi import OpenAPISpec
from langchain.chat_models import ChatOpenAI

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Existing OpenAPI agent (WotNot)
# -----------------------------
with open("wotnot_openapi.json", "r") as f:
    openapi_raw = f.read()

spec = OpenAPISpec.from_text(openapi_raw)
spec.base_url = "https://api.wotnot.io"

toolkit = RequestsToolkit(spec=spec)
tools = toolkit.get_tools()

llm_agent = Bedrock(
    model_id="anthropic.claude-v2",
    region_name="us-east-1",
    model_kwargs={"temperature": 0.2}
)

agent = initialize_agent(
    tools=tools,
    llm=llm_agent,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

@app.post("/run-agent/")
async def run_agent(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "Find content for template, create it, and send to today's contacts.")
    try:
        result = agent.run(prompt)
        return {"response": result}
    except Exception as e:
        return {"error": str(e)}

# -----------------------------
# Diwali Greeting Endpoint (OpenAI GPT)
# -----------------------------
# Make sure to set your OpenAI API key here or in an .env file
llm_greeting = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.7,
    openai_api_key=os.environ.get("OPENAI_API_KEY")
)

@app.post("/diwali-greet/")
async def diwali_greeting(request: Request):
    """
    Input JSON: {"name": "Jay"}
    Returns a festive Diwali greeting message.
    """
    body = await request.json()
    name = body.get("name", "Friend")

    prompt = f"Write a short, warm, festive Diwali greeting message for {name}."

    try:
        greeting = llm_greeting(prompt)
        return {"greeting": greeting}
    except Exception as e:
        return {"error": str(e)}
