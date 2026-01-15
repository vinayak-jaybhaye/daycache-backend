from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional, List

class ListDaysQuery(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    limit: int = 30
    offset: int = 0
    include_metadata: bool = False

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v):
        if v > 366:
            raise ValueError("limit cannot exceed 366")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, end_date, info):
        start_date = info.data.get("start_date")
        if start_date and end_date and start_date > end_date:
            raise ValueError("start_date cannot be after end_date")
        return end_date

class DayResponse(BaseModel):
    date: date
    summary: Optional[str] = None
    tags: Optional[list[str]] = None

    model_config = {
        "exclude_none": True,
    }

class DayMetadata(BaseModel):
    date: date
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    updated_at: Optional[datetime] = None