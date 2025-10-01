import os
import json
import requests
from openai import OpenAI
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# --- 1. FastAPI App Initialization ---
app = FastAPI(
    title="AI Backend (Direct Method)",
    description="A stable backend using direct library calls instead of LangChain.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. Configuration and Sanity Checks ---
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("CRITICAL ERROR: OPENAI_API_KEY environment variable is not set.")

# Initialize the OpenAI client
try:
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except Exception as e:
    raise RuntimeError(f"Failed to initialize OpenAI client: {e}") from e

# Define the base URL for the WotNot API
WOTNOT_API_BASE_URL = "https://api.wotnot.io"

# --- 3. API Endpoints ---
@app.get("/")
def read_root():
    """A simple endpoint to confirm the server is running."""
    return {"status": "AI backend is running successfully!"}

@app.post("/call-wotnot/")
async def call_wotnot_api(request: Request):
    """
    Directly calls a WotNot API endpoint. This is a replacement for the agent.
    
    Expected JSON body:
    {
        "endpoint": "/templates",
        "method": "GET",
        "payload": null,
        "params": {},
        "headers": {
            "Authorization": "Bearer YOUR_WOTNOT_TOKEN" 
        }
    }
    """
    body = await request.json()
    
    endpoint = body.get("endpoint")
    method = body.get("method", "GET").upper()
    payload = body.get("payload")
    params = body.get("params")
    headers = body.get("headers", {})

    if not endpoint:
        raise HTTPException(status_code=400, detail="The 'endpoint' field is required.")

    full_url = f"{WOTNOT_API_BASE_URL}{endpoint}"

    try:
        response = requests.request(
            method=method,
            url=full_url,
            headers=headers,
            params=params,
            json=payload,
            timeout=30 # 30-second timeout
        )
        
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
        
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        # Try to return the API's error message if possible
        try:
            error_details = http_err.response.json()
        except json.JSONDecodeError:
            error_details = http_err.response.text
        raise HTTPException(status_code=http_err.response.status_code, detail=error_details)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to call WotNot API: {str(e)}")


@app.post("/diwali-greet/")
async def diwali_greeting_endpoint(request: Request):
    """Generates a Diwali greeting for a given name using the OpenAI API directly."""
    body = await request.json()
    name = body.get("name", "Friend")
    
    prompt = f"Write a short, warm, and festive Diwali greeting message for {name}."
    
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes greeting messages."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        greeting = completion.choices[0].message.content
        return {"greeting": greeting}
    except Exception as e:
        print(f"OpenAI API error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate greeting: {str(e)}")

