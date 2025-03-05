from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.day import Day
from app.models.user import User
from app.schemas.day import DayCreate, DayResponse
from app.core.security import get_current_user
from app.services.entry_services import get_all_entries
from app.services.automate.summary_service import generate_summary

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

@router.get("/summary/{day_id}", response_model=DayResponse)
def get_summary(
    day_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Step 1: Fetch all entries for the day
    entries = get_all_entries(db, day_id)

    # Step 2: Combine all content into one string
    content = "\n".join(entry.content for entry in entries)

    # Step 3: Generate summary using Hugging Face API
    summary = generate_summary(content)

    # Step 4: Update the `latest_summary` column in the Day table
    day = db.query(Day).filter(Day.id == day_id).first()
    if not day:
        raise HTTPException(status_code=404, detail="Day not found")
    
    day.latest_summary = summary
    db.commit()

    # Step 5: Return the updated day (with summary included)
    return day
