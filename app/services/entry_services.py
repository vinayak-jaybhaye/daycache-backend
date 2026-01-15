from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional
from datetime import date
from app.db.models import Entry
from app.schemas.entry import EntryCreate, EntryUpdate, EntryResponse
from app.db.models import User

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

# Delete an entry
def delete_entry(
    db: Session,
    user: User,
    entry_id: int,
) -> None:
    entry = get_entry(db, user, entry_id)

    db.delete(entry)
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
        query = query.filter(Entry.created_at >= start_dt)
    
    if end_date:
        end_dt = datetime.combine(end_date, time.max),
        query = query.filter(Entry.created_at <= end_dt)

    return (
        query
        .order_by(Entry.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )