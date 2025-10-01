import os
import requests
from fastapi import FastAPI, Request, HTTPException, APIRouter
from openai import OpenAI

# -----------------------------
# Environment Variable Checks
# -----------------------------
if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError("The OPENAI_API_KEY environment variable is not set. Please add it in Render.")

# -----------------------------
# Initialize OpenAI Client
# -----------------------------
try:
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except Exception as e:
    raise RuntimeError(f"Failed to initialize OpenAI client: {e}") from e

# -----------------------------
# FastAPI App & API Router Setup
# -----------------------------
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

# --- NEW: User Registration Endpoint ---
@router.post("/register")
async def register_user(request: Request):
    """Handles new user registration without CAPTCHA."""
    body = await request.json()
    username = body.get("username")
    email = body.get("email")
    password = body.get("password")

    if not all([username, email, password]):
        raise HTTPException(status_code=400, detail="Username, email, and password are required.")

    # --- In a real application, you would do the following: ---
    # 1. Validate the email format.
    # 2. Check if the username or email already exists in your database.
    # 3. Securely hash the password (e.g., using passlib).
    # 4. Save the new user to your database.
    
    # For this prototype, we'll just print the info and return success.
    print(f"--- New User Registration ---")
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Password: [HIDDEN]")
    print(f"-----------------------------")

    return {"success": True, "message": "Account created successfully!"}


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
    """A direct proxy to the WotNot API."""
    body = await request.json()
    endpoint = body.get("endpoint")
    payload = body.get("payload", {})
    wotnot_api_key = os.environ.get("WOTNOT_API_KEY") 

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
        response = requests.post(full_url, headers=headers, json=payload, timeout=15)
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"WotNot API HTTP error: {http_err} - {response.text}")
        raise HTTPException(status_code=response.status_code, detail=response.json())
    except Exception as e:
        print(f"WotNot API call failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to communicate with the WotNot API.")


# --- Mount the Router ---
# This adds all routes with a global /api prefix.
app.include_router(router, prefix="/api")

