from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class DayCreate(BaseModel):
    date: date
    latest_summary: Optional[str] = None


class DayResponse(BaseModel):
    id: int
    date: date
    latest_summary: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}

class CacheMyDayRequest(BaseModel):
    myday : str
    DiaryAssistant : str
    User : str