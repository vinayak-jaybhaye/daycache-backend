from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class CacheChatCreate(BaseModel):
    content: str


class DiaryEntry(BaseModel):
    date: date
    location: Optional[str] = None
    tags: Optional[list[str]] = []
    content: str


class CacheChatResponse(BaseModel):
    content: str
    model_config = {"from_attributes": True}


class CacheChatRequest(BaseModel):
    content: str
