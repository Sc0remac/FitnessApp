# backend/schemas/workout.py
import uuid
from pydantic import BaseModel, Field, field_validator # Use field_validator in Pydantic v2
from datetime import datetime
from typing import List, Optional

# --- Schemas mirroring Flutter Models ---

class SetLogBase(BaseModel):
    reps: int = Field(..., gt=0) # Reps must be positive
    weight: float = Field(..., ge=0) # Weight can be 0 or positive

class SetLogRead(SetLogBase): # Read schema might be same as base here
    pass

class ExerciseLogBase(BaseModel):
    name: str = Field(..., min_length=1)
    sets: List[SetLogBase] # List of set logs

class ExerciseLogRead(ExerciseLogBase):
    sets: List[SetLogRead] # Ensure nested models use Read schemas if needed

# --- Schemas for Workout API Operations ---

class WorkoutBase(BaseModel):
    # Timestamp will be set by server on creation
    exercises: List[ExerciseLogBase] = Field(..., min_length=1) # Workout needs at least one exercise

    # Add a validator to ensure sets within exercises are not empty
    @field_validator('exercises')
    @classmethod
    def check_exercise_sets_not_empty(cls, exercises: List[ExerciseLogBase]):
        for ex in exercises:
            if not ex.sets:
                raise ValueError(f"Exercise '{ex.name}' must contain at least one set.")
        return exercises

class WorkoutCreate(WorkoutBase):
    # user_id comes from the token
    # timestamp is set on the server
    pass

class WorkoutRead(WorkoutBase):
    id: uuid.UUID
    user_id: uuid.UUID
    timestamp: datetime
    created_at: datetime # Added created_at from model
    exercises: List[ExerciseLogRead] # Use read schema for nested models

    class Config:
        from_attributes = True # Pydantic v2 replacement for orm_mode

# Optional: Schema for listing workouts (maybe less detail)
class WorkoutList(BaseModel):
    id: uuid.UUID
    timestamp: datetime
    exercise_count: int # Example: just show count instead of full detail
    total_sets: int # Example calculation

    class Config:
        from_attributes = True