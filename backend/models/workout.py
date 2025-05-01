# backend/models/workout.py
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB # Use JSONB for exercises
from sqlalchemy.orm import relationship
from db.session import Base

class Workout(Base):
    __tablename__ = "workouts" # Match table name in Supabase

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # user_id column is FK to auth.users table managed by Supabase Auth
    # We link it via the RLS policies and by inserting the correct ID
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True) # Link to auth.uid()
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    createdAt = Column(DateTime(timezone=True), server_default='now()', nullable=False) # Use server_default

    # Store the list of exercises and their sets as JSONB
    exercises = Column(JSONB, nullable=True)

    # --- Relationship (Optional but good practice if querying from User) ---
    # If you modify models/user.py, ensure the back_populates matches
    # user = relationship("User", back_populates="workouts")

    # Define __repr__ for easier debugging (optional)
    def __repr__(self):
        return f"<Workout(id={self.id}, user_id={self.user_id}, timestamp='{self.timestamp}')>"