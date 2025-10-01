import os
import requests
from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

# -----------------------------
# In-Memory User "Database"
# -----------------------------
fake_user_db = {
    "test@example.com": {"username": "Test User", "password": "password"}
}

# -----------------------------
# Environment Variable Checks
# -----------------------------
if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError("The OPENAI_API_KEY environment variable is not set.")

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

# --- CORS MIDDLEWARE CONFIGURATION (THE FIX) ---
# This block tells the backend to trust your frontend.
origins = [
    "https://wotnot-frontend.onrender.com",  # Your live frontend URL
    "http://localhost:8080",               # For local development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

# --- API Endpoints ---
# (Your /register, /login, and other endpoints remain the same)
@router.post("/login")
async def login_user(request: Request):
    """Handles user login by checking credentials against the in-memory DB."""
    # NOTE: Your login.vue sends 'x-www-form-urlencoded', so we use request.form()
    form_data = await request.form()
    email = form_data.get("username")
    password = form_data.get("password")

    if not all([email, password]):
        raise HTTPException(status_code=400, detail="Email and password are required.")

    user = fake_user_db.get(email)
    
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    print(f"--- User logged in: {email} ---")
    return {"access_token": "fake-jwt-token-for-prototype", "token_type": "bearer"}

@router.post("/register")
async def register_user(request: Request):
    """Handles new user registration and saves them to the in-memory DB."""
    body = await request.json()
    username = body.get("username")
    email = body.get("email")
    password = body.get("password")

    if not all([username, email, password]):
        raise HTTPException(status_code=400, detail="Username, email, and password are required.")

    if email in fake_user_db:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    fake_user_db[email] = {"username": username, "password": password}
    
    print(f"--- New user registered: {email} ---")
    print(f"Current DB: {fake_user_db}")
    
    return {"success": True, "message": "Account created successfully!"}

@router.post("/diwali-greet/")
async def diwali_greeting(request: Request):
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

# --- Mount the Router ---
app.include_router(router, prefix="/api")

