from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional
from datetime import date
from app.schemas.entry import EntryCreate, EntryUpdate, EntryResponse
from app.db.models import User, Day, Entry
from datetime import datetime, time

# Create a new entry
def create_entry(
    db: Session,
    user: User,
    content: str,
    entry_date: date,
) -> Entry:
    entry = Entry(
        user_id=user.id,
        content=content,
        entry_date=entry_date,
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

# Get a specific entry by ID
def get_entry(
    db: Session,
    user: User,
    entry_id: int,
) -> Entry:
    entry = (
        db.query(Entry)
        .filter(
            Entry.id == entry_id,
            Entry.user_id == user.id,
        )
        .first()
    )

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    return entry


# Update an existing entry
def update_entry(
    db: Session,
    user: User,
    entry_id: int,
    content: str,
) -> Entry:
    entry = get_entry(db, user, entry_id)

    entry.content = content

    db.commit()
    db.refresh(entry)
    return entry

# Delete an entry and its associated day metadata if no entries remain for that day
def delete_entry(
    db: Session,
    user: User,
    entry_id: int,
) -> None:
    entry = get_entry(db, user, entry_id)
    entry_date = entry.entry_date

    # Delete the entry
    db.delete(entry)
    db.flush()  # ensures the delete is reflected in the session

    # Check if any entries remain for this user on the same day
    remaining_entries = (
      db.query(Entry)
      .filter(
          Entry.user_id == user.id,
          Entry.entry_date == entry_date,
      )
      .count()
    )

    # If no entries left for that day, delete the day record
    if remaining_entries == 0:
      db.query(Day).filter(
        Day.user_id == user.id,
        Day.date == entry_date,
      ).delete(synchronize_session=False)

    db.commit()


# Search entries with optional text and date filters
def search_entries(
    db: Session,
    user: User,
    q: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 20,
    offset: int = 0,
):
    query = db.query(Entry).filter(Entry.user_id == user.id)

    # text search
    if q:
        query = query.filter(
            Entry.content.ilike(f"%{q}%")
        )
    
    # date filters
    if start_date:
        start_dt = datetime.combine(start_date, time.min)
        query = query.filter(Entry.entry_date >= start_dt)
    
    if end_date:
        end_dt = datetime.combine(end_date, time.max)
        query = query.filter(Entry.entry_date <= end_dt)

    return (
        query
        .order_by(Entry.entry_date.desc())

        .offset(offset)
        .limit(limit)
        .all()
    )