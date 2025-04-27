# backend/schemas/mood.py
import uuid
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional

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
    # Timestamp will be added server-side on creation
    pass

class MoodRead(MoodBase):
    id: uuid.UUID
    user_id: uuid.UUID
    timestamp: datetime
    created_at: datetime # Add if you have this in your model
    # Include analysis results - mark Optional as they might not exist for every entry initially
    sentiment_label: Optional[str] = Field(None, examples=["Positive"])
    sentiment_intensity: Optional[int] = Field(None, ge=1, le=10, examples=[7])
    sentiment_summary: Optional[str] = Field(None, examples=["User felt optimistic."])

    class Config:
        from_attributes = True # Pydantic v2