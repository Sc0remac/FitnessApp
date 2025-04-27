# backend/schemas/token.py
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """ Schema for returning JWT access token (if generating custom tokens) """
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """ Schema for data encoded within a JWT """
    user_id: Optional[str] = None # Or use UUID if parsing JWT sub claim directly
    # Add other claims like roles, scopes etc. if needed