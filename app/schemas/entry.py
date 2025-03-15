from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class EntryCreate(BaseModel):
    day_id: Optional[int] = None
    location: Optional[str] = None
    content: str
    tags: Optional[list[str]] = None


class EntryUpdate(BaseModel):
    location: Optional[str]
    content: Optional[str]
    tags: List[str] = []


class EntryResponse(BaseModel):
    id: int
    day_id: int
    location: Optional[str]
    content: Optional[str]
    tags: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


class SuggestionResponse(BaseModel):
    suggested: List[str]


class SuggestionRequest(BaseModel):
    content: str
