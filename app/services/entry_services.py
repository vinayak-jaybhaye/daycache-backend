from sqlalchemy.orm import Session
from app.models.entry import Entry
from app.schemas.entry import EntryCreate, EntryUpdate
from app.models.day import Day
from datetime import datetime


def create_entry_in_db(user_id: int, date: datetime.date, entry_data: dict, db: Session):
    # Check if the day exists
    day = db.query(Day).filter(Day.date == date, Day.user_id == user_id).first()

    # If day doesn't exist, create it
    if not day:
        day = Day(
            date=date,
            user_id=user_id,
            latest_summary=""
        )
        db.add(day)
        db.commit()
        db.refresh(day)

    # Create the entry linked to the day
    entry = Entry(
        day_id=day.id,  # Link entry to the created/found day
        location=entry_data.get("location"),
        content=entry_data.get("content"),
        tags=entry_data.get("tags"),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    
    return entry


def update_entry_in_db(entry_id: int, content: str, db: Session):
    print(entry_id, content)
    entry = db.query(Entry).filter(Entry.id == entry_id).first()
    if entry:
        entry.content = content
        db.commit()
        db.refresh(entry)
        return entry
    return None

def delete_entry_in_db(day_id: int, entry_id: int, db: Session):
    entry = db.query(Entry).filter(Entry.id == entry_id and Entry.day_id == day_id).first()
    if entry:
        db.delete(entry)
        db.commit()
        return True
    return False

def get_all_entries(user_id: int,day_id: int, db: Session):
    # add logic to prevent users from accessing other users' entries
    return db.query(Entry).filter(Entry.day_id == day_id).all()