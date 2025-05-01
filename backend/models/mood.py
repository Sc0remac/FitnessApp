# backend/models/mood.py
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.orm import relationship
from db.session import Base

class MoodEntry(Base):
    __tablename__ = "mood_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    mood_score = Column(Integer, nullable=False)
    journal_text = Column(Text, nullable=True)
    sentiment_label = Column(String, nullable=True)
    sentiment_intensity = Column(Integer, nullable=True)
    sentiment_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default='now()', nullable=False)

    def __repr__(self):
        # --- SAFER REPR ---
        # Only access attributes guaranteed after creation/refresh (usually PK)
        # Avoid accessing potentially unloaded fields like created_at here
        # to prevent DetachedInstanceError during complex error handling.
        return f"<MoodEntry(id={self.id}, score={self.mood_score})>"
        # --- END SAFER REPR ---