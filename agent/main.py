import os
import requests
from fastapi import FastAPI, Request, HTTPException, APIRouter
from openai import OpenAI

# -----------------------------
# Environment Variable Checks
# -----------------------------
# This runs when the app starts to ensure everything is configured.
if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError("The OPENAI_API_KEY environment variable is not set. Please add it in Render.")

# -----------------------------
# Initialize OpenAI Client
# -----------------------------
# This is created once when the application starts.
try:
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except Exception as e:
    raise RuntimeError(f"Failed to initialize OpenAI client: {e}") from e

# -----------------------------
# FastAPI App & API Router Setup
# -----------------------------
# All our endpoints will be defined on the `router` object.
# This makes it easy to add a global prefix.
app = FastAPI(
    title="AI Agent Backend",
    description="A simple backend for the AI Agent Hub.",
    version="1.0.0"
)
router = APIRouter()

# --- API Endpoints ---

@router.get("/")
def read_root():
    """A simple root endpoint to confirm the API is running."""
    return {"status": "AI backend is running"}

@router.post("/diwali-greet/")
async def diwali_greeting(request: Request):
    """Generates a Diwali greeting for a given name using the OpenAI client."""
    body = await request.json()
    name = body.get("name", "Friend")
    
    prompt = f"Write a short, warm, and festive Diwali greeting message for {name}."
    
    try:
        chat_completion = openai_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-3.5-turbo",
        )
        greeting = chat_completion.choices[0].message.content
        return {"greeting": greeting}
    except Exception as e:
        print(f"Greeting generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate the greeting.")

@router.post("/call-wotnot/")
async def call_wotnot_api(request: Request):
    """
    A direct proxy to the WotNot API. The frontend specifies the endpoint and payload.
    This is more reliable than an AI agent for direct, known tasks.
    """
    body = await request.json()
    endpoint = body.get("endpoint")
    payload = body.get("payload", {})
    wotnot_api_key = os.environ.get("WOTNOT_API_KEY") # You would need to add this for real calls

    if not endpoint:
        raise HTTPException(status_code=400, detail="An 'endpoint' is required in the request body.")
    if not wotnot_api_key:
        raise HTTPException(status_code=500, detail="WOTNOT_API_KEY is not configured on the server.")

    wotnot_base_url = "https://api.wotnot.io"
    full_url = f"{wotnot_base_url}{endpoint}"
    headers = {
        "Authorization": f"Bearer {wotnot_api_key}",
        "Content-Type": "application/json"
    }

    try:
        # For simplicity, this example only handles POST requests.
        # A real implementation would check the method (GET, POST, etc.).
        response = requests.post(full_url, headers=headers, json=payload, timeout=15)
        
        # Raise an exception if the call failed
        response.raise_for_status() 
        
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        # The API returned an error status code (4xx or 5xx)
        print(f"WotNot API HTTP error: {http_err} - {response.text}")
        raise HTTPException(status_code=response.status_code, detail=response.json())
    except Exception as e:
        # Other errors like network issues
        print(f"WotNot API call failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to communicate with the WotNot API.")


# --- Mount the Router ---
# This line adds all the routes from our router to the main app,
# with a global prefix of /api.
# Now, your endpoints will be available at /api/diwali-greet/, /api/call-wotnot/, etc.
app.include_router(router, prefix="/api")

