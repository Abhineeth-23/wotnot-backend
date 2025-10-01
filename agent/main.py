import os
import requests
from fastapi import FastAPI, Request, HTTPException, APIRouter
from openai import OpenAI

# -----------------------------
# In-Memory User "Database" (for prototype use only)
# -----------------------------
# This dictionary will act as our temporary user storage.
# It will be cleared every time the server restarts.
fake_user_db = {}

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

@router.post("/register")
async def register_user(request: Request):
    """Handles new user registration and saves them to the in-memory DB."""
    body = await request.json()
    username = body.get("username")
    email = body.get("email")
    password = body.get("password")

    if not all([username, email, password]):
        raise HTTPException(status_code=400, detail="Business Name, Email, and Password are required.")

    if email in fake_user_db:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    # Save the new user to our fake database
    fake_user_db[email] = {"username": username, "password": password}
    
    print(f"--- New user registered: {email} ---")
    print(f"Current User DB: {fake_user_db}")
    
    return {"success": True, "message": "Account created successfully!"}

@router.post("/login")
async def login_user(request: Request):
    """Handles user login by checking credentials against the in-memory DB."""
    body = await request.json()
    # Note: Your login form sends the email in the 'username' field
    email = body.get("username") 
    password = body.get("password")

    if not all([email, password]):
        raise HTTPException(status_code=400, detail="Email and password are required.")

    user = fake_user_db.get(email)
    
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # If login is successful, return a fake token for the prototype
    print(f"--- User logged in: {email} ---")
    return {"access_token": "fake-jwt-token-for-prototype", "token_type": "bearer"}

@router.post("/diwali-greet/")
async def diwali_greeting(request: Request):
    """Generates a Diwali greeting for a given name."""
    body = await request.json()
    name = body.get("name", "Friend")
    
    prompt = f"Write a short, warm, and festive Diwali greeting message for {name}."
    
    try:
        chat_completion = openai_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-3.5-turbo",
        )
        greeting = chat_completion.choices[0].message.content
        return {"greeting": greeting}
    except Exception as e:
        print(f"Greeting generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate the greeting.")

# This endpoint is kept for future use but is not essential for the core app
@router.post("/call-wotnot/")
async def call_wotnot_api(request: Request):
    """A placeholder for direct WotNot API calls."""
    return {"message": "This endpoint is a placeholder for direct WotNot API calls."}

# --- Mount the Router ---
# This line adds all the routes from our router to the main app,
# with a global prefix of /api.
app.include_router(router, prefix="/api")

