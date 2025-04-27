# backend/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Cookie
from fastapi.security import OAuth2PasswordRequestForm # For standard login form
from sqlalchemy.orm import Session
from typing import Annotated, Optional
import logging
import uuid # Import uuid
from datetime import datetime # Import datetime

# Import Schemas
from schemas.user import UserCreate, UserRead
from schemas.token import Token
from schemas.message import Message

# Import Core components
from core.config import settings
from core.clients import get_supabase_client # Use Supabase client helper
# --- ADD THIS IMPORT ---
from supabase import Client as SupabaseClient, AuthApiError # Import Client type and specific Exception
# --- END ADD ---

# Import DB session (Optional)
# from db.session import get_db

# Import security functions (Optional)
# from core import security

# Import dependency for protected routes
from core.dependencies import get_current_active_user


logger = logging.getLogger(__name__)
router = APIRouter()

# --- Signup Endpoint ---
@router.post(
    "/signup",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    tags=["Authentication"]
)
async def signup(
    user_in: UserCreate,
    response: Response,
    supabase: SupabaseClient = Depends(get_supabase_client) # Type hint is now recognized
):
    """
    Registers a new user via Supabase Auth.
    Sets HttpOnly session cookies upon successful signup or if confirmation is needed.
    """
    logger.info(f"Attempting signup for email: {user_in.email}")
    try:
        auth_response = await supabase.auth.sign_up({
            "email": user_in.email,
            "password": user_in.password,
            "options": {
                "data": {
                    "full_name": user_in.full_name
                }
            }
        })

        logger.debug(f"Supabase signup response: User={auth_response.user is not None}, Session={auth_response.session is not None}")

        if auth_response.user and auth_response.session:
            logger.info(f"Signup successful and session created for user {auth_response.user.id}")
            response.set_cookie(
                key="sb-access-token", value=auth_response.session.access_token,
                httponly=True, samesite="lax", max_age=auth_response.session.expires_in,
                secure=True, path="/" # Remember to adjust secure based on HTTPS
            )
            response.set_cookie(
                key="sb-refresh-token", value=auth_response.session.refresh_token,
                httponly=True, samesite="lax", max_age=60*60*24*30, # ~30 days
                secure=True, path="/"
            )
            return UserRead(
                id=auth_response.user.id,
                email=auth_response.user.email or "", # Handle potential None
                full_name=auth_response.user.user_metadata.get("full_name", ""),
                created_at=auth_response.user.created_at or datetime.utcnow(),
                updated_at=auth_response.user.updated_at or datetime.utcnow(),
            )

        elif auth_response.user and not auth_response.session:
            logger.info(f"Signup requires email confirmation for user {auth_response.user.id}")
            return UserRead(
                id=auth_response.user.id,
                email=auth_response.user.email or "",
                full_name=auth_response.user.user_metadata.get("full_name", ""),
                created_at=auth_response.user.created_at or datetime.utcnow(),
                updated_at=auth_response.user.updated_at or datetime.utcnow(),
            )
        else:
            logger.error("Supabase signup returned unexpected null user/session.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Signup failed due to an unexpected Supabase response.")

    except AuthApiError as e:
        logger.warning(f"Supabase Auth API Error during signup: {e.message} (Status: {e.status})")
        if "User already registered" in e.message or e.status == 422:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")
        elif e.status == 400:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Signup failed: {e.message}")
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An internal error occurred during signup: {e.message}")
    except Exception as e:
        logger.exception(f"Unexpected error during signup: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

# --- Login Endpoint ---
@router.post(
    "/login",
    response_model=Message,
    summary="Login User",
    tags=["Authentication"]
)
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    supabase: SupabaseClient = Depends(get_supabase_client) # Type hint recognized
):
    """
    Logs in a user via Supabase Auth using email and password (from form data).
    Sets HttpOnly session cookies on success.
    """
    logger.info(f"Login attempt for user: {form_data.username}")
    try:
        auth_response = await supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })

        if auth_response.user and auth_response.session:
            logger.info(f"Login successful for user {auth_response.user.id}")
            response.set_cookie(
                 key="sb-access-token", value=auth_response.session.access_token,
                 httponly=True, samesite="lax", max_age=auth_response.session.expires_in,
                 secure=True, path="/"
            )
            response.set_cookie(
                 key="sb-refresh-token", value=auth_response.session.refresh_token,
                 httponly=True, samesite="lax", max_age=60*60*24*30, secure=True, path="/"
             )
            return Message(message="Login successful")
        else:
            logger.error("Supabase sign_in_with_password returned unexpected null user/session.")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login failed unexpectedly after Supabase call.")

    except AuthApiError as e:
        logger.warning(f"Supabase Auth API Error during login: {e.message} (Status: {e.status})")
        if "Invalid login credentials" in e.message or e.status == 400:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        elif "Email not confirmed" in e.message:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not confirmed. Please check your email.",
             )
        else:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Login failed: {e.message}",
             )
    except Exception as e:
        logger.exception(f"Unexpected error during login: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login.",
        )


# --- Logout Endpoint ---
@router.post("/logout", response_model=Message, summary="Logout User", tags=["Authentication"])
async def logout(
    response: Response,
    supabase: SupabaseClient = Depends(get_supabase_client) # Type hint recognized
):
    """
    Logs out the user server-side (invalidates Supabase session if possible)
    and instructs client to clear cookies.
    """
    logger.info("Logout attempt.")
    try:
        await supabase.auth.sign_out()
        logger.info("Supabase sign_out called successfully.")
    except Exception as e:
        logger.warning(f"Error calling Supabase sign_out (proceeding with cookie clear): {e}")

    response.delete_cookie("sb-access-token", path="/", secure=True, httponly=True, samesite="lax")
    response.delete_cookie("sb-refresh-token", path="/", secure=True, httponly=True, samesite="lax")
    return Message(message="Logout successful")


# --- Refresh Token Endpoint ---
@router.post("/refresh", response_model=Message, summary="Refresh Session Token", tags=["Authentication"])
async def refresh_token(
    request: Request,
    response: Response,
    supabase: SupabaseClient = Depends(get_supabase_client) # Type hint recognized
):
    """
    Refreshes the access token using the refresh token stored in HttpOnly cookie.
    """
    logger.info("Refresh token attempt.")
    refresh_token_value = request.cookies.get("sb-refresh-token")

    if not refresh_token_value:
        logger.warning("Refresh attempt failed: Refresh token cookie not found.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found")

    try:
        auth_response = await supabase.auth.refresh_session(refresh_token_value)

        if auth_response.session:
            logger.info("Token refresh successful.")
            response.set_cookie(
                 key="sb-access-token", value=auth_response.session.access_token,
                 httponly=True, samesite="lax", max_age=auth_response.session.expires_in,
                 secure=True, path="/"
            )
            if auth_response.session.refresh_token and auth_response.session.refresh_token != refresh_token_value:
                logger.info("New refresh token issued by Supabase.")
                response.set_cookie(
                     key="sb-refresh-token", value=auth_response.session.refresh_token,
                     httponly=True, samesite="lax", max_age=60*60*24*30, secure=True, path="/"
                 )
            return Message(message="Token refreshed successfully")
        else:
            logger.error("Supabase refresh_session returned unexpected null session.")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to refresh session unexpectedly.")

    except AuthApiError as e:
        logger.warning(f"Supabase Auth API Error during token refresh: {e.message} (Status: {e.status})")
        response.delete_cookie("sb-access-token", path="/", secure=True, httponly=True, samesite="lax")
        response.delete_cookie("sb-refresh-token", path="/", secure=True, httponly=True, samesite="lax")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not refresh token: {e.message}")
    except Exception as e:
        logger.exception(f"Unexpected error during token refresh: {e}", exc_info=True)
        response.delete_cookie("sb-access-token", path="/", secure=True, httponly=True, samesite="lax")
        response.delete_cookie("sb-refresh-token", path="/", secure=True, httponly=True, samesite="lax")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="An unexpected error occurred during token refresh.")


# --- Get Current User Profile Endpoint ---
@router.get(
    "/users/me",
    response_model=UserRead,
    summary="Get Current User Profile",
    tags=["Users", "Authentication"]
)
async def read_users_me(
    supabase: SupabaseClient = Depends(get_supabase_client), # Type hint recognized
    current_user_payload: dict = Depends(get_current_active_user)
):
    """
    Fetches the profile information of the currently authenticated user
    based on the validated JWT payload.
    """
    user_id = current_user_payload.get("sub")
    logger.info(f"Fetching profile for user ID: {user_id}")

    try:
        email = current_user_payload.get("email")
        user_metadata = current_user_payload.get("user_metadata", {})
        full_name = user_metadata.get("full_name", "")
        # Timestamps from JWT might represent token issuance/expiry, not user creation/update.
        # Fetching might be needed for accurate timestamps, but let's rely on payload for now.
        # Fallback to current time if timestamps aren't reliably in payload or parsable.
        created_at_ts = current_user_payload.get("created_at") # Placeholder, might not be in standard JWT
        updated_at_ts = current_user_payload.get("updated_at") # Placeholder

        if not email or not user_id:
             logger.error("Missing email or user ID in validated JWT payload.")
             raise HTTPException(status_code=500, detail="Incomplete user data in token.")

        # Placeholder timestamps - Ideally fetch from DB if needed
        created_at_dt = datetime.utcnow()
        updated_at_dt = datetime.utcnow()

        return UserRead(
            id=uuid.UUID(user_id),
            email=email,
            full_name=full_name,
            created_at=created_at_dt, # Use fetched/parsed if available
            updated_at=updated_at_dt, # Use fetched/parsed if available
        )

    except Exception as e:
         logger.exception(f"Error retrieving user profile data for {user_id}: {e}", exc_info=True)
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not retrieve user profile.")