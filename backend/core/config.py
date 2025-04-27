# backend/core/config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional, List # Added List for potential future use
from pydantic import field_validator, SecretStr # Need SecretStr

# Determine the base directory for the project to reliably find .env
# Assumes config.py is in backend/core/
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CORE_DIR)
BASE_DIR = os.path.dirname(BACKEND_DIR)
ENV_FILE_PATH = os.path.join(BACKEND_DIR, '.env') # Path to backend/.env

class Settings(BaseSettings):
    # Load .env file from the calculated path
    # `extra='ignore'` prevents errors if .env has vars not defined in Settings
    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH, extra='ignore', env_file_encoding='utf-8')

    # Application Meta
    APP_NAME: str = "FMMT Backend API"

    # Database (Using SecretStr for sensitive values)
    DATABASE_URL: SecretStr # Keep the raw URL secret

    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: SecretStr # Keep secret
    SUPABASE_JWT_SECRET: SecretStr       # Keep secret

    # OpenAI
    OPENAI_API_KEY: SecretStr # Keep secret

    # Spotify
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: SecretStr # Keep secret
    SPOTIFY_REDIRECT_URI: str

    # Application Secrets / Tokens
    APP_SECRET_KEY: SecretStr # Used for state in OAuth etc., keep secret
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # Example: for any custom JWTs if needed
    ALGORITHM: str = "HS256" # Example algorithm for custom JWTs

    # CORS - Store as a simple string, parse later if needed
    CLIENT_ORIGIN_URL: Optional[str] = None # e.g., "http://localhost:5173,https://your.domain.com"

    # Optional Monitoring
    SENTRY_DSN: Optional[str] = None
    LOGFLARE_API_KEY: Optional[str] = None
    LOGFLARE_SOURCE_ID: Optional[str] = None

    # Method to get parsed CORS origins (example)
    @property
    def cors_origins(self) -> List[str]:
        if not self.CLIENT_ORIGIN_URL:
            # Default if not set (adjust as needed for security)
            return ["http://localhost:5173", "http://127.0.0.1:5173"]
        return [origin.strip() for origin in self.CLIENT_ORIGIN_URL.split(",") if origin.strip()]

# Use lru_cache to load settings only once (singleton pattern)
@lru_cache()
def get_settings() -> Settings:
    print(f"Loading settings from: {ENV_FILE_PATH}") # Log path for debugging
    if not os.path.exists(ENV_FILE_PATH):
        print(f"WARNING: .env file not found at {ENV_FILE_PATH}. Settings will rely on environment variables.")
    try:
        loaded_settings = Settings()
        # Optionally print loaded (non-secret) settings for verification
        # print("Loaded settings (non-secret):")
        # print(f"  APP_NAME: {loaded_settings.APP_NAME}")
        # print(f"  SUPABASE_URL: {loaded_settings.SUPABASE_URL}")
        # print(f"  CLIENT_ORIGIN_URL: {loaded_settings.CLIENT_ORIGIN_URL}")
        return loaded_settings
    except Exception as e:
        print(f"ERROR: Failed to load settings: {e}")
        # Depending on severity, you might re-raise or exit
        raise ValueError(f"Configuration error: {e}") from e


# Create the settings instance immediately when the module is loaded
settings = get_settings()