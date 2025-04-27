# backend/db/base.py
# Import all the models, so that Base has them before being
# imported by Alembic or used by create_all
from db.session import Base # noqa
from models.user import User # noqa
from models.workout import Workout # <-- ADD THIS LINE noqa
from models.mood import MoodEntry # noqa
from models.spotify import SpotifyTrack # noqa