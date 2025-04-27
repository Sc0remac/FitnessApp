# backend/schemas/user.py
import uuid
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# --- Base User Properties ---
# Shared properties, not directly used for request/response usually
class UserBase(BaseModel):
    email: EmailStr = Field(..., examples=["user@example.com"])
    full_name: Optional[str] = Field(None, examples=["Jane Doe"])

# --- User Creation (Sign Up) ---
# Properties required when creating a new user account
class UserCreate(UserBase):
    # Inherits email and full_name from UserBase
    password: str = Field(..., min_length=6, examples=["securepassword"]) # Min length based on Supabase default

# --- User Update (Profile Editing - Future) ---
# Properties allowed when updating a user profile
class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, examples=["Jane D. Updated"])
    # Add other fields that can be updated by the user later
    # Avoid allowing email/password updates directly here without specific checks

# --- User Read (API Response) ---
# Properties returned when reading user data (e.g., from /users/me or signup)
# Excludes sensitive information like password hash
class UserRead(UserBase):
    id: uuid.UUID = Field(..., examples=["a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"])
    # email: EmailStr # Inherited from UserBase
    # full_name: Optional[str] # Inherited from UserBase
    created_at: datetime
    updated_at: datetime
    # Add other non-sensitive fields stored in Supabase user_metadata or a local profiles table

    class Config:
        from_attributes = True # Pydantic v2 replaces orm_mode

# --- User in Database (Internal Representation) ---
# Represents all data including potentially sensitive fields (used carefully on backend)
# Not typically returned directly by API endpoints
class UserInDB(UserRead):
    # If you were storing hashed passwords yourself (not recommended with Supabase)
    # hashed_password: str
    pass # Since Supabase handles auth.users, this might just be same as UserRead or UserBase