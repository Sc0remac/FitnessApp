# backend/db/base.py
# Import all the models, so that Base has them before being
# imported by Alembic or used by create_all
from db.session import Base # noqa
from models.user import User # noqa
from models.workout import Workout # noqa
from models.mood import MoodEntry # <-- ENSURE THIS IS UNCOMMENTED/PRESENT noqa
from models.spotify import SpotifyTrack # noqa (Ensure spotify.py model exists if using)
# from models.profile import Profile # Uncomment if you create a Profile model