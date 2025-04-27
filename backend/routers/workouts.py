# backend/routers/workouts.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid # Import uuid

from db.session import get_db
from models.workout import Workout as WorkoutModel # Alias model to avoid name clash
from schemas import workout as workout_schemas # Use alias for schemas too
from core.dependencies import get_current_active_user
from pydantic import BaseModel

router = APIRouter()

@router.post(
    "/",
    response_model=workout_schemas.WorkoutRead,
    status_code=status.HTTP_201_CREATED,
    summary="Log a new workout session"
)
async def create_workout(
    workout_in: workout_schemas.WorkoutCreate,
    db: Session = Depends(get_db),
    current_user_payload: dict = Depends(get_current_active_user)
):
    """
    Creates a new workout log entry for the authenticated user.
    - **workout_in**: Workout details including list of exercises and sets.
    """
    user_id_str = current_user_payload.get("sub") # User ID from JWT payload
    if not user_id_str:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    try:
        user_id = uuid.UUID(user_id_str) # Convert string UUID to UUID object
    except ValueError:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user identifier")

    # Convert Pydantic exercises list to a list of dicts suitable for JSONB
    exercises_data = [ex.model_dump() for ex in workout_in.exercises]

    db_workout = WorkoutModel(
        user_id=user_id,
        timestamp=datetime.utcnow(), # Set timestamp on server using UTC
        exercises=exercises_data
    )

    try:
        db.add(db_workout)
        db.commit()
        db.refresh(db_workout)
        return db_workout
    except Exception as e:
        db.rollback()
        print(f"Error saving workout: {e}") # Log the error server-side
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save workout.",
        )


@router.get(
    "/",
    response_model=List[workout_schemas.WorkoutRead], # Use WorkoutRead for detail now
    summary="Retrieve workout sessions"
)
async def read_workouts(
    db: Session = Depends(get_db),
    current_user_payload: dict = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = Query(None, description="Filter workouts after this date (ISO 8601 format)"),
    end_date: Optional[datetime] = Query(None, description="Filter workouts before this date (ISO 8601 format)")
):
    """
    Retrieves a list of workout logs for the authenticated user, ordered by most recent first.
    Supports pagination and date range filtering.
    """
    user_id_str = current_user_payload.get("sub")
    if not user_id_str:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user identifier")

    query = db.query(WorkoutModel).filter(WorkoutModel.user_id == user_id)

    if start_date:
        query = query.filter(WorkoutModel.timestamp >= start_date)
    if end_date:
        query = query.filter(WorkoutModel.timestamp <= end_date)

    workouts = query.order_by(WorkoutModel.timestamp.desc()).offset(skip).limit(limit).all()

    return workouts

# --- Add GET /workouts/{id}, PUT /workouts/{id}, DELETE /workouts/{id} later ---