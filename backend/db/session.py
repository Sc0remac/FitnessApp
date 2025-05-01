# backend/db/session.py
from sqlalchemy import create_engine, text # Import text for raw SQL execution if needed
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from core.config import settings # Import settings to get DATABASE_URL
import logging

logger = logging.getLogger(__name__)

# Get the raw SecretStr first
_database_url_secret = settings.DATABASE_URL

# --- *** CHANGE IS HERE *** ---
# Get the actual string value and perform checks on it
database_url_str = _database_url_secret.get_secret_value() if _database_url_secret else None
sync_database_url = None
if database_url_str and database_url_str.startswith("postgresql://"): # Check 1
    sync_database_url = database_url_str.replace("postgresql://", "postgresql+psycopg2://", 1)
    logger.info("Using synchronous PostgreSQL driver (psycopg2) via explicit prefix.")
elif database_url_str and database_url_str.startswith("postgres://"): # Check 2 (NEW)
    # If it starts with just 'postgres', SQLAlchemy might infer correctly,
    # OR we might need to add the driver here too for robustness. Let's try
    # letting SQLAlchemy handle it first. If connection *still* fails,
    # uncomment the line below.
    sync_database_url = database_url_str
    sync_database_url = database_url_str.replace("postgres://", "postgresql+psycopg2://", 1) # Potential alternative
    logger.info("Database URL uses 'postgres://' scheme. Relying on SQLAlchemy/psycopg2 inference.")
elif database_url_str:
    sync_database_url = database_url_str
    logger.warning(f"Database URL does not start with postgresql:// or postgres:// : {sync_database_url}")
else:
    logger.error("DATABASE_URL is not set or is empty in the environment configuration!")
    raise ValueError("DATABASE_URL configuration is missing or empty!")
# --- *** END CHANGE *** ---


# Setup database engine using the correctly processed URL string
try:
    if sync_database_url is None:
         raise ValueError("sync_database_url was not correctly determined from DATABASE_URL")

    engine = create_engine(sync_database_url, pool_pre_ping=True, echo=False)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database session factory configured.")

except Exception as e:
    logger.error(f"Failed to create database engine or session factory: {e}")
    raise


# Base class for declarative models (SQLAlchemy ORM)
Base = declarative_base()

# Dependency for FastAPI endpoints to get a DB session
def get_db():
    db: Session = SessionLocal() # Create a new session
    try:
        yield db # Provide the session to the route
    except Exception as e:
        logger.error(f"Database session error during request: {e}")
        db.rollback() # Rollback any changes if an error occurred
        raise # Re-raise the exception to be handled by FastAPI error handlers
    finally:
        db.close() # Always close the session when the request is done