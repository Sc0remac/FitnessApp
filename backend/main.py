# backend/main.py
import os
from fastapi import FastAPI, Request, status, Depends # Ensure Depends is imported
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from jose import JWTError, jwt
from sqlalchemy import text # Import text for raw SQL query in lifespan
from contextlib import asynccontextmanager
import logging

# --- Core Components ---
from core.config import settings # Load settings first
from core.dependencies import get_current_active_user # Import the primary dependency

# --- Database ---
# Ensure engine is created in session.py; Base is needed if using create_all
from db.session import engine, SessionLocal, Base

# --- Routers ---
# Import all defined router modules
from routers import auth, workouts, moods, spotify, insights

# Configure logging (Ensure this runs before app creation if complex setup)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Optional: Database Table Creation (for dev only) ---
def create_db_tables():
    """ Creates tables based on models imported in db.base """
    logger.info("Attempting to create database tables if they don't exist...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables check/creation process completed.")
    except Exception as e:
        logger.error(f"Error during initial table creation/check: {e}")
        # Depending on the severity, you might want to exit or just log the error
        # raise # Re-raise if critical


# --- Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    logger.info(f"Starting up {settings.APP_NAME}...")
    # create_db_tables() # Uncomment to attempt table creation on startup (DEV ONLY)

    # Test DB connection
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1")) # Simple query to test connection
        logger.info("Database connection successful on startup.")
    except Exception as e:
        logger.error(f"Database connection failed on startup: {e}")
    yield
    # Code to run on shutdown
    logger.info(f"Shutting down {settings.APP_NAME}...")


# --- FastAPI App Initialization ---
app = FastAPI(
    title=settings.APP_NAME,
    description="API for tracking fitness activities, mood entries, and Spotify listening habits.",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    lifespan=lifespan # Use the lifespan context manager
)

# --- CORS Middleware ---
# Use the parsed origins from settings
origins = settings.cors_origins
if not origins:
    logger.error("FATAL: No origins configured for CORS. Frontend calls will be blocked.")
    # Consider exiting if origins are essential and missing
    # exit(1)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info(f"CORS configured for origins: {origins}")

# --- Exception Handlers ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation Error: Path={request.url.path}, Detail={exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation Error", "errors": exc.errors()},
    )

@app.exception_handler(JWTError)
async def jwt_exception_handler(request: Request, exc: JWTError):
    logger.warning(f"JWT Authentication Error: {exc}") # Downgrade log level
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": f"Invalid or expired token: {exc}"},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Catch-all for unexpected errors
    logger.exception(f"Unhandled Internal Exception: {exc}", exc_info=True) # Log full traceback
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )

# --- Root Endpoint ---
@app.get("/", tags=["Root"], summary="API Root / Docs Redirect", include_in_schema=False)
async def read_root():
    """Redirects to the API documentation."""
    return RedirectResponse(url='/api/v1/docs')

# --- Include Routers ---
api_prefix = "/api/v1"

# Authentication endpoints (might not need user dependency globally)
app.include_router(auth.router, prefix=f"{api_prefix}/auth", tags=["Authentication"])

# Protected endpoints using the dependency
app.include_router(workouts.router, prefix=f"{api_prefix}/workouts", tags=["Workouts"], dependencies=[Depends(get_current_active_user)])
app.include_router(moods.router, prefix=f"{api_prefix}/moods", tags=["Mood & Journal"], dependencies=[Depends(get_current_active_user)])
app.include_router(spotify.router, prefix=f"{api_prefix}/spotify", tags=["Spotify"]) # Add dependency if needed for specific spotify routes
app.include_router(insights.router, prefix=f"{api_prefix}/insights", tags=["Insights"], dependencies=[Depends(get_current_active_user)])


# --- Development Server Startup (for debugging) ---
if __name__ == "__main__":
    # This block is mainly for running the file directly (python main.py)
    # which is usually not how Uvicorn is run in production or with --reload.
    import uvicorn
    logger.info("Running Uvicorn directly from main.py (for debugging)")
    uvicorn.run(app, host="0.0.0.0", port=8000)