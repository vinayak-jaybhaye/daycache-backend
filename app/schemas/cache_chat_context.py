from pydantic import BaseModel
from datetime import date as dt
from typing import Optional, List


# Schema for incoming chat message from user
class CacheChatCreate(BaseModel):
    content: str


# Schema for response to user
class CacheChatResponse(BaseModel):
    content: str

    model_config = {"from_attributes": True}


# Schema for extracting context from user question
class ContextQuery(BaseModel):
    tags: List[str] = []  # optional, can be empty for now
    content: Optional[str] = None  # original question
    location: Optional[str] = None  # extracted location (if present)
    date: Optional[dt] = None  # extracted date (if present)
    user_id: int  # current user's ID (mandatory)
