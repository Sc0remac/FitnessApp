# backend/core/dependencies.py
from fastapi import Depends, Cookie, HTTPException, status, Header # Import Header
from typing import Annotated, Optional
from jose import JWTError, jwt
import logging
import uuid # Import uuid

# Import settings FOR JWT secret and algorithm
from .config import settings

# Imports for DB lookups (Uncomment if/when needed)
# from sqlalchemy.orm import Session
# from db.session import get_db
# from models.user import User # If fetching User model instance
# from services import user_service # If using a user service

logger = logging.getLogger(__name__)

# --- Define Scheme for Swagger UI Auth (Optional but Recommended) ---
# from fastapi.security import OAuth2PasswordBearer
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login") # Adjust tokenUrl if needed

# --- Dependency to Extract Token ---
# Tries Header first (standard for APIs), then falls back to Cookie
async def get_token_data_optional(
    # Look for 'Authorization: Bearer <token>' header
    authorization: Annotated[Optional[str], Header()] = None,
    # Fallback: Look for Supabase cookie (adjust key name if needed)
    access_token_cookie: Annotated[Optional[str], Cookie(alias="sb-access-token")] = None
) -> Optional[dict]: # Returns the verified payload dict or None
    """
    Dependency to extract and VERIFY JWT from Authorization header or cookie.
    """
    token = None
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
            logger.debug("Token extracted from Authorization header.")
        else:
            logger.warning("Invalid Authorization header format.")
            # Don't raise exception yet, maybe cookie has it
            # raise credentials_exception # Or raise immediately if header is expected format

    if not token and access_token_cookie:
        token = access_token_cookie
        logger.debug("Token extracted from cookie.")

    if not token:
        logger.debug("No token found in header or cookie.")
        return None # No token provided

    # --- *** VERIFY THE TOKEN *** ---
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET.get_secret_value(), # Use the secret from settings
            algorithms=[settings.ALGORITHM], # Use the algorithm from settings (HS256)
            # Optionally add audience check if Supabase sets it:
            audience="authenticated",
        )
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            logger.warning("Token verification successful, but 'sub' (user ID) claim missing.")
            raise credentials_exception # Treat missing sub as invalid credentials

        # Convert sub to UUID to ensure it's valid format early on
        try:
            _ = uuid.UUID(user_id)
        except ValueError:
             logger.warning(f"Token 'sub' claim '{user_id}' is not a valid UUID.")
             raise credentials_exception

        logger.debug(f"Token successfully verified for user ID: {user_id}")
        return payload # Return the verified payload

    except JWTError as e:
        logger.warning(f"JWTError during token verification: {e}")
        # This catches invalid signature, expired token, etc.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        # Catch potential errors during secret retrieval or decoding logic
        logger.error(f"Unexpected error during token verification: {e}", exc_info=True)
        raise credentials_exception

# --- Dependency to get REQUIRED active user ---
async def get_current_active_user(
    # This now depends on get_token_data_optional which performs verification
    user_payload: Annotated[Optional[dict], Depends(get_token_data_optional)]
) -> dict:
    """
    Dependency that ensures a valid, verified token exists and returns its payload.
    Raises HTTP 401 if no valid token is found.
    Placeholder for checking if user is active in the DB.
    """
    if user_payload is None:
        # This case should technically be handled by JWTError in get_token_data_optional
        # if a token was present but invalid. If no token was present, this will trigger.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = user_payload.get("sub") # Already validated as present in previous step
    logger.info(f"Authenticated user ID via dependency: {user_id}")

    # --- Placeholder for Database Active Check ---
    # This requires injecting db session and potentially user service
    # db: Session = Depends(get_db)
    # try:
    #    is_active = await user_service.is_user_active(db=db, user_id=uuid.UUID(user_id))
    #    if not is_active:
    #        logger.warning(f"User {user_id} is inactive.")
    #        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    # except Exception as e:
    #     logger.error(f"Failed to check user active status for {user_id}: {e}")
    #     raise HTTPException(status_code=500, detail="Error checking user status.")
    # --- End Placeholder ---

    return user_payload # Return the verified payload