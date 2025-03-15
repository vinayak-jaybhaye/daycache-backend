from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class MediaCreate(BaseModel):
    file_type: str
    file_url: HttpUrl


class MediaResponse(BaseModel):
    id: int
    entry_id: int
    file_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class MediaSchema(BaseModel):
    id: int
    entry_id: int
    file_url: str

    class Config:
        orm_mode = True
