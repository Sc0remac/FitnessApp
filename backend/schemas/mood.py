# backend/schemas/mood.py
import uuid
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List # Added List

# --- Sentiment Analysis Result (from OpenAI service) ---
class SentimentAnalysisResult(BaseModel):
    sentiment: str = Field(..., examples=["Positive", "Negative", "Neutral"])
    intensity: int = Field(..., ge=1, le=10, examples=[7])
    summary: str = Field(..., examples=["User felt optimistic about the day."])

# --- Mood API Schemas ---
class MoodBase(BaseModel):
    mood_score: int = Field(..., ge=1, le=10, description="User's mood rating (1=Worst, 10=Best)")
    journal_text: Optional[str] = Field(None, description="Optional free-text journal entry")

class MoodCreate(MoodBase):
    # Timestamp/created_at will be added server-side on creation
    pass

class MoodRead(MoodBase): # Inherits mood_score and journal_text
    id: uuid.UUID
    user_id: uuid.UUID
    # --- *** CHANGE IS HERE *** ---
    # Remove 'timestamp' field as it's not in the DB model anymore
    # timestamp: datetime
    # Rely on 'created_at' which IS in the DB model and returned
    created_at: datetime
    # --- *** END CHANGE *** ---

    # Include analysis results - mark Optional
    sentiment_label: Optional[str] = Field(None, examples=["Positive"])
    sentiment_intensity: Optional[int] = Field(None, ge=1, le=10, examples=[7])
    sentiment_summary: Optional[str] = Field(None, examples=["User felt optimistic."])

    class Config:
        from_attributes = True # Pydantic v2