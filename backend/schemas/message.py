# backend/schemas/message.py
from pydantic import BaseModel

class Message(BaseModel):
    """ A generic message response schema. """
    message: str