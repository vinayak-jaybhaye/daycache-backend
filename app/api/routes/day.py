from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.day import Day
from app.models.user import User
from app.schemas.day import DayCreate, DayResponse
from app.core.security import get_current_user

router = APIRouter()

@router.post("/create-day", response_model=DayResponse)
def create_day(
    day: DayCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_day = db.query(Day).filter(Day.user_id == current_user.id, Day.date == day.date).first()
    if existing_day:
        raise HTTPException(status_code=400, detail="Day already exists for this date")

    new_day = Day(user_id=current_user.id, date=day.date, latest_summary=day.latest_summary)
    db.add(new_day)
    db.commit()
    db.refresh(new_day)
    return new_day



@router.get("/get-days", response_model=list[DayResponse])
def get_days(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):  
    days = db.query(Day).filter(Day.user_id == current_user.id).all()
    print(days)
    return days
