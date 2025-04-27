# backend/routers/moods.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# --- ADD IMPORTS HERE ---
from typing import List, Optional
import uuid
from datetime import datetime
from pydantic import BaseModel # Import BaseModel
# --- END ADD IMPORTS ---

from db.session import get_db
from core.dependencies import get_current_active_user
# Import actual schemas and models later when implementing logic
from schemas import mood as mood_schemas # Use the real schemas now
from models import mood as mood_models # Use the real models now
from services import openai_service # Import the service
from core.clients import get_openai_client # Import the client getter
from openai import AsyncOpenAI # Import the AsyncOpenAI type hint

router = APIRouter()

# Use actual schemas now that they are defined
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Log Mood Entry",
    response_model=mood_schemas.MoodRead # Use actual response schema
)
async def create_mood_entry(
    mood_in: mood_schemas.MoodCreate, # Use actual input schema
    db: Session = Depends(get_db),
    current_user_payload: dict = Depends(get_current_active_user),
    openai_client: AsyncOpenAI = Depends(get_openai_client) # Inject OpenAI client
):
    """
    Logs a mood entry for the authenticated user.
    If journal text is provided, performs sentiment analysis via OpenAI
    and saves the results along with the mood entry.
    """
    user_id_str = current_user_payload.get("sub")
    if not user_id_str: # Should be caught by dependency, but defense-in-depth
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user identifier")

    sentiment_label = None
    sentiment_intensity = None
    sentiment_summary = None

    # --- Perform Sentiment Analysis (if text provided) ---
    if mood_in.journal_text and mood_in.journal_text.strip():
        try:
            print(f"Analyzing journal for user {user_id}: {mood_in.journal_text[:50]}...") # Log analysis start
            analysis_result = await openai_service.analyze_journal_entry(
                openai_client=openai_client, # Pass the client instance
                text=mood_in.journal_text
            )
            if analysis_result:
                sentiment_label = analysis_result.sentiment
                sentiment_intensity = analysis_result.intensity
                sentiment_summary = analysis_result.summary
                print(f"Analysis Result: {sentiment_label}, Intensity: {sentiment_intensity}") # Log result
            else:
                 print(f"Sentiment analysis returned None for user {user_id}.")
        except Exception as analysis_error:
            # Log the error but don't fail the whole mood entry saving
            print(f"WARNING: Sentiment analysis failed for user {user_id}: {analysis_error}")
            # Optionally store a marker indicating analysis failure?

    # --- Create MoodEntry model instance ---
    db_mood = mood_models.MoodEntry(
        user_id=user_id,
        mood_score=mood_in.mood_score,
        journal_text=mood_in.journal_text,
        timestamp=datetime.utcnow(), # Use UTC for DB storage
        sentiment_label=sentiment_label,
        sentiment_intensity=sentiment_intensity,
        sentiment_summary=sentiment_summary,
    )

    # --- Save to Database ---
    try:
        db.add(db_mood)
        db.commit()
        db.refresh(db_mood)
        print(f"Mood entry saved successfully for user {user_id}, ID: {db_mood.id}")
        return db_mood
    except Exception as db_error:
        db.rollback()
        print(f"ERROR: Database error saving mood entry for user {user_id}: {db_error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save mood entry.",
        )

# --- Get Mood History Endpoint ---
@router.get("/", summary="Get Mood History", response_model=List[mood_schemas.MoodRead]) # Use actual schema
async def read_mood_history(
    db: Session = Depends(get_db),
    current_user_payload: dict = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100 # Default limit
):
    """
    Retrieves mood history for the authenticated user, ordered by most recent first.
    """
    user_id_str = current_user_payload.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user identifier")

    print(f"Fetching mood history for user {user_id}, skip={skip}, limit={limit}")
    try:
        query = db.query(mood_models.MoodEntry).filter(mood_models.MoodEntry.user_id == user_id)
        moods = query.order_by(mood_models.MoodEntry.timestamp.desc()).offset(skip).limit(limit).all()
        print(f"Found {len(moods)} mood entries for user {user_id}")
        return moods
    except Exception as db_error:
         print(f"ERROR: Database error fetching mood history for user {user_id}: {db_error}")
         # Don't expose internal error details usually
         raise HTTPException(status_code=500, detail="Could not retrieve mood history.")