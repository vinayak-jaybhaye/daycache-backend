from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime, date

class EntryCreate(BaseModel):
    content: str
    entry_date: Optional[date] = None

    @field_validator('entry_date')
    @classmethod
    def validate_entry_date(cls, v: Optional[date]):
        if v is not None and v > date.today():
            raise ValueError("entry_date cannot be in the future")
        return v
    

class EntryUpdate(BaseModel):
    content: Optional[str] = None

class EntryResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    updated_at: Optional[datetime]
    entry_date: date
    class Config:
        from_attributes = True

