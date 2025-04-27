# backend/schemas/spotify.py
import uuid
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional, List

# --- Schemas for Data Fetched from Spotify API ---

class SpotifyArtistSimple(BaseModel):
    id: str
    name: str

class SpotifyAlbumSimple(BaseModel):
    id: str
    name: str
    images: Optional[List[dict]] = None # List of image objects with url, height, width

class SpotifyTrack(BaseModel):
    id: str # Spotify track ID
    name: str
    artists: List[SpotifyArtistSimple]
    album: SpotifyAlbumSimple
    duration_ms: int
    explicit: bool
    popularity: Optional[int] = None
    preview_url: Optional[HttpUrl] = None # Make sure HttpUrl is imported if using strict URL validation
    uri: str # Spotify track URI

class SpotifyPlayHistoryObject(BaseModel):
    """ Represents an item in the 'recently played' list """
    track: SpotifyTrack
    played_at: datetime # Timestamp when the track finished playing (or was played)
    context: Optional[dict] = None # Context like playlist or album if available

# --- Schemas for API Responses from *Our* Backend ---

class SpotifyTrackRead(BaseModel):
    """ Schema for returning track info stored in our DB """
    id: uuid.UUID # Our DB primary key
    user_id: uuid.UUID
    spotify_track_id: str
    played_at: datetime
    track_name: str
    artist_name: str # Simple string representation for now
    album_name: str # Simple string
    # Add other fields if stored (e.g., spotify_uri, duration_ms)

    class Config:
        from_attributes = True

class SpotifyConnectResponse(BaseModel):
    """ Response for the /spotify/connect endpoint """
    authorization_url: str

# Optional: Schema for storing token info if needed (though usually handled internally)
class SpotifyTokenData(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None