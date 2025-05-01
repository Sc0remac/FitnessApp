# backend/routers/moods.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime
from pydantic import BaseModel # Keep for safety, though not used by placeholders now

from db.session import get_db
from core.dependencies import get_current_active_user
from schemas import mood as mood_schemas # Use the actual schemas
from models import mood as mood_models # Use the actual model
# from services import openai_service # Temporarily commented out if service not ready
# from core.clients import get_openai_client
# from openai import AsyncOpenAI
import logging

logger = logging.getLogger(__name__)

# --- *** FIX IS HERE: Ensure router instance is created *** ---
router = APIRouter()
# --- *** END FIX *** ---


# --- POST Endpoint to Create Mood Entry ---
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Log Mood Entry",
    response_model=mood_schemas.MoodRead
)
async def create_mood_entry(
    mood_in: mood_schemas.MoodCreate,
    db: Session = Depends(get_db),
    current_user_payload: dict = Depends(get_current_active_user),
    # openai_client: AsyncOpenAI = Depends(get_openai_client) # Keep commented if not using yet
):
    # ... (rest of the create_mood_entry function remains the same) ...
    user_id_str = current_user_payload.get("sub")
    if not user_id_str: raise HTTPException(401, "Could not validate credentials")
    try: user_id = uuid.UUID(user_id_str)
    except ValueError: raise HTTPException(401, "Invalid user identifier")

    sentiment_label = None; sentiment_intensity = None; sentiment_summary = None
    # if mood_in.journal_text and mood_in.journal_text.strip(): # Keep commented
    #    ... (openai analysis logic) ...

    try:
        db_mood = mood_models.MoodEntry(
            user_id=user_id, mood_score=mood_in.mood_score,
            journal_text=mood_in.journal_text,
            sentiment_label=sentiment_label, sentiment_intensity=sentiment_intensity,
            sentiment_summary=sentiment_summary,
        )
    except Exception as model_error:
        logger.error(f"Error creating MoodEntry model instance: {model_error}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error preparing mood data.")

    try:
        db.add(db_mood); db.commit(); db.refresh(db_mood)
        logger.info(f"Mood entry saved successfully for user {user_id}, ID: {db_mood.id}")
        return db_mood
    except Exception as db_error:
        db.rollback()
        logger.error(f"Database error saving mood entry: {db_error}", exc_info=True)
        raise HTTPException(500, detail="Could not save mood entry.")


# --- GET Endpoint for Mood History ---
@router.get("/", summary="Get Mood History", response_model=List[mood_schemas.MoodRead])
async def read_mood_history(
    db: Session = Depends(get_db),
    current_user_payload: dict = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    # ... (rest of the read_mood_history function remains the same) ...
     user_id_str = current_user_payload.get("sub")
     if not user_id_str: raise HTTPException(401, "Could not validate credentials")
     try: user_id = uuid.UUID(user_id_str)
     except ValueError: raise HTTPException(401, "Invalid user identifier")

     logger.info(f"Fetching mood history for user {user_id}, skip={skip}, limit={limit}")
     try:
        query = db.query(mood_models.MoodEntry).filter(mood_models.MoodEntry.user_id == user_id)
        moods = query.order_by(mood_models.MoodEntry.created_at.desc()).offset(skip).limit(limit).all()
        logger.info(f"Found {len(moods)} mood entries for user {user_id}")
        return moods
     except Exception as db_error:
         logger.error(f"Database error fetching mood history: {db_error}", exc_info=True)
         raise HTTPException(status_code=500, detail="Could not retrieve mood history.")