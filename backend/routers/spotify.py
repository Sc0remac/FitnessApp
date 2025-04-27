# backend/routers/spotify.py
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Query # Added Query
from sqlalchemy.orm import Session
# --- ADD THESE IMPORTS ---
from typing import List, Optional
from pydantic import BaseModel, HttpUrl # Import BaseModel and HttpUrl
from datetime import datetime # Import datetime
# --- END ADD IMPORTS ---

# Import necessary dependencies, schemas, models, services when implemented
from db.session import get_db
from core.dependencies import get_current_active_user
from core.config import settings
from services import spotify_service # Needs implementation
# from schemas import spotify as spotify_schemas # Use actual schemas later
# from models import user as user_models # To store/retrieve tokens

router = APIRouter()

# Placeholder response models
# These now inherit correctly from the imported BaseModel
class SpotifyTrackPlaceholder(BaseModel):
    id: str
    name: str
    artist: str
    played_at: datetime # Uses imported datetime type

class SpotifyConnectResponse(BaseModel):
    authorization_url: str

# --- Endpoint to initiate Spotify OAuth flow ---
@router.get("/connect", summary="Connect Spotify Account", response_model=SpotifyConnectResponse)
async def connect_spotify(
    request: Request,
    current_user_payload: dict = Depends(get_current_active_user)
):
    """
    (Placeholder) Initiates the Spotify OAuth2 flow.
    Redirects the user to Spotify's authorization page.
    Requires spotify_service implementation.
    """
    user_id = current_user_payload.get("sub")
    print(f"Placeholder: Generate Spotify auth URL for user {user_id}")
    # Replace with actual call to spotify_service.create_authorization_url(request, user_id)
    return SpotifyConnectResponse(authorization_url="https://accounts.spotify.com/authorize?client_id=DUMMY&response_type=code&redirect_uri=DUMMY&scope=user-read-recently-played&state=DUMMYSTATE")

# --- Endpoint for Spotify OAuth Callback ---
@router.get("/callback", summary="Spotify OAuth Callback Handler")
async def spotify_callback(
    request: Request,
    response: Response,
    code: Optional[str] = None,
    error: Optional[str] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    (Placeholder) Handles the redirect from Spotify after user authorization.
    Exchanges the authorization code for tokens and stores them securely.
    Requires spotify_service implementation.
    """
    if error:
        print(f"Spotify OAuth Error: {error}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Spotify authorization failed: {error}")
    if not code:
         print("Spotify OAuth Error: No authorization code received.")
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing authorization code from Spotify.")

    print(f"Placeholder: Received Spotify callback code: {code[:10]}... State: {state}")
    # TODO: Implement state verification, token exchange, token storage in spotify_service
    response.status_code = status.HTTP_307_TEMPORARY_REDIRECT
    # Redirect to a frontend page indicating success/failure (use deeplink for mobile)
    response.headers["Location"] = "/?spotify_callback=success" # Placeholder redirect
    return response


# --- Endpoint to fetch recent tracks ---
@router.get("/tracks", summary="Get Recent Spotify Tracks", response_model=List[SpotifyTrackPlaceholder])
async def get_recent_tracks(
    db: Session = Depends(get_db),
    current_user_payload: dict = Depends(get_current_active_user),
    limit: int = Query(20, ge=1, le=50)
):
    """
    (Placeholder) Fetches recently played tracks from Spotify for the authenticated user.
    Requires spotify_service and token retrieval logic.
    """
    user_id = current_user_payload.get("sub")
    print(f"Placeholder: Fetch Spotify tracks for user {user_id}")
    # TODO: Implement token retrieval, refresh check, API call via spotify_service
    # Return actual data using schemas.spotify.SpotifyTrackRead later
    return [] # Return empty list placeholder