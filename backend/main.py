import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="FMMT Backend API")

# --- CORS Configuration ---
# Adjust origins as needed for frontend development and production
# For local dev, allow the Vite default port (5173)
# For production, add your Vercel domain
origins = [
    "http://localhost:5173", # Vite dev server
    "http://127.0.0.1:5173",
    # Add your deployed frontend URL here later
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specific origins
    allow_credentials=True, # Allows cookies
    allow_methods=["*"],    # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],    # Allows all headers
)

# --- Root Endpoint ---
@app.get("/")
async def root():
    return {"message": "Welcome to the FMMT API!"}

# --- Placeholder for future routers ---
# Example:
# from .routers import auth, workouts, mood, spotify
# app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# app.include_router(workouts.router, prefix="/workouts", tags=["Workouts"])
# app.include_router(mood.router, prefix="/moods", tags=["Mood & Journal"])
# app.include_router(spotify.router, prefix="/spotify", tags=["Spotify"])

# --- Add Supabase Client Setup (example) ---
# from supabase import create_client, Client
# supabase_url: str = os.environ.get("SUPABASE_URL")
# supabase_key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") # Use service role for backend operations
# supabase: Client = create_client(supabase_url, supabase_key)

if __name__ == "__main__":
    import uvicorn
    # Note: Running directly like this is for debugging.
    # Use `uvicorn main:app --reload` from the terminal for development.
    uvicorn.run(app, host="0.0.0.0", port=8000)