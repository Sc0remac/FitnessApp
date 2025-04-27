# backend/core/clients.py
from supabase import create_client, Client as SupabaseClient # Use the main sync client type/creator
from openai import AsyncOpenAI                          # Use async OpenAI client
from functools import lru_cache                         # For singleton pattern/caching
from typing import Optional                             # For type hinting
import logging                                          # For logging

# Import the settings object AFTER it's defined and loaded in config.py
from .config import settings

logger = logging.getLogger(__name__)

# --- Supabase Client Initialization ---
_supabase_client: Optional[SupabaseClient] = None

@lru_cache() # Cache the client instance creation
def get_supabase_client() -> SupabaseClient:
    """
    Initializes and returns the Supabase client using Anon Key.
    The returned client object can be used for async operations with 'await'.
    """
    global _supabase_client
    if _supabase_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
            logger.error("Supabase URL or Anon Key not configured in .env!")
            raise ValueError("Supabase URL or Anon Key not configured!")
        try:
            # create_client returns a Client object that can handle both sync/async
            _supabase_client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_ANON_KEY # Anon key is public, no need for SecretStr
            )
            logger.info("Supabase client initialized (Anon Key).")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    return _supabase_client

# Optional: Function for Service Role Client (If needed later)
# You would typically call admin functions using the main client instance
# after authenticating it or using specific admin methods if available,
# rather than creating a whole separate client instance in many cases.

# --- OpenAI Client Initialization ---
_openai_async_client: Optional[AsyncOpenAI] = None

@lru_cache() # Cache this one too
def get_openai_client() -> AsyncOpenAI:
    """Initializes and returns the Async OpenAI client."""
    global _openai_async_client
    if _openai_async_client is None:
        if not settings.OPENAI_API_KEY:
            logger.error("OpenAI API Key not configured in .env!")
            raise ValueError("OpenAI API Key not configured!")
        try:
            # Pass the actual secret key string using .get_secret_value()
            _openai_async_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())
            logger.info("Async OpenAI client initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize async OpenAI client: {e}")
            raise
    return _openai_async_client

# --- Usage Note ---
# It's generally recommended to call these getter functions
# (e.g., `get_supabase_client()`, `get_openai_client()`)
# within your endpoint functions or services where needed,
# possibly via FastAPI's dependency injection system if desired,
# rather than creating global instances immediately when this module loads.
# The @lru_cache decorator ensures they act like singletons anyway.