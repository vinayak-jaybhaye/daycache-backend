from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.db.session import get_db
from app.models.day import Day
from app.models.user import User
from app.schemas.day import DayCreate, DayResponse
from app.core.security import get_current_user
from app.services.day_services import get_day, get_all_days, summarize_day, get_active_days
from app.services.automate.cache_my_day import cache_my_day
from app.schemas.day import CacheMyDayRequest

router = APIRouter()

@router.post("/create-day")
def create_day(
    day: DayCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_day = (
        db.query(Day)
        .filter(Day.user_id == current_user.id, Day.date == day.date)
        .first()
    )
    if existing_day:
        raise HTTPException(status_code=400, detail="Day already exists for this date")

    new_day = Day(
        user_id=current_user.id, date=day.date, latest_summary=day.latest_summary
    )
    db.add(new_day)
    db.commit()
    db.refresh(new_day)
    return new_day

@router.get("/get-days", response_model=list[DayResponse])
def get_days(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    days = db.query(Day).filter(Day.user_id == current_user.id).all()
    return days

@router.post("/users/{user_id}/days/{day_id}/summarize")
def summarize(
    user_id: int,
    day_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user),
):
    summary = summarize_day(user_id,day_id, db)
    return summary

@router.get("/users/{user_id}/days/{date}")
def get_user_day(
    user_id: int,
    date: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    day = get_day(user_id, date, db)
    if not day:
        raise HTTPException(status_code=404, detail="Day not found")
    return day

@router.get("/users/{user_id}/days")
def get_user_days(
    user_id: int,
    last_date: Optional[date] = None,  # format: YYYY-MM-DD
    limit: int = 10,
    db: Session = Depends(get_db),
):
    days = get_all_days(user_id, db, last_date=last_date, limit=limit)
    return days

@router.post("/users/{user_id}/days/{day_id}/cache-my-day")
def cache_today(
    user_id: int,
    day_id: int,
    request: CacheMyDayRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
   response = cache_my_day(request.User, request.myday,request.DiaryAssistant)
   return response

@router.get("/days/get-active-days/{date}")
def get_active_days_route(
    date: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    days = get_active_days(date, current_user.id, db)
    return days
