from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, time
from typing import List, Optional

from app.db.models import Day, User, Entry
from fastapi import HTTPException
from app.services.ai_generation_service import ai_generate_summary_and_tags

# Get a list of active days + optional metadata

def list_active_days(
    db: Session,
    user: User,
    start_date: date | None,
    end_date: date | None,
    limit: int,
    offset: int,
    include_metadata: bool,
):
    # base query: active days from entries (explicit entry_date)
    days_query = (
        db.query(Entry.entry_date.label("day"))
        .filter(Entry.user_id == user.id)
    )

    if start_date:
        days_query = days_query.filter(Entry.entry_date >= start_date)
    if end_date:
        days_query = days_query.filter(Entry.entry_date <= end_date)

    days = (
        days_query
        .distinct()
        .order_by(Entry.entry_date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    day_dates = [row.day for row in days]

    # ---- dates only ----
    if not include_metadata:
        return day_dates

    # ---- fetch metadata in one query ----
    metadata = (
        db.query(Day)
        .filter(
            Day.user_id == user.id,
            Day.date.in_(day_dates),
        )
        .all()
    )

    metadata_map = {d.date: d for d in metadata}

    return [
        {
            "date": d,
            "summary": metadata_map.get(d).ai_summary if d in metadata_map else None,
            "tags": metadata_map.get(d).ai_tags if d in metadata_map else None,
        }
        for d in day_dates
    ]


# Get entries for a specific day
def get_day_entries(
    db: Session,
    user: User,
    day: date,
):
    return (
        db.query(Entry)
        .filter(
            Entry.user_id == user.id,
            Entry.entry_date == day,
        )
        .order_by(Entry.created_at.asc())
        .all()
    )

## Day Metadata Management ##

def delete_day_and_entries(
    db: Session,
    user: User,
    day: date,
):
    # Delete entries
    db.query(Entry).filter(
        Entry.user_id == user.id,
        Entry.entry_date == day,
    ).delete(synchronize_session=False)

    # Delete day metadata (if exists)
    db.query(Day).filter(
        Day.user_id == user.id,
        Day.date == day,
    ).delete()

    db.commit()

# Clear day summary and tags (keep entries)
def delete_day_metadata(
    db: Session,
    user: User,
    day: date,
):
    db.query(Day).filter(
        Day.user_id == user.id,
        Day.date == day,
    ).delete()
    db.commit()

# get day metadata
def get_day_metadata(
    db: Session,
    user: User,
    day: date,
    generate_summary: bool = False,
):
    if generate_summary:
        entries = get_day_entries(db, user, day)
        if(not entries):
            raise HTTPException(status_code=404, detail="No entries found for the day to generate summary")
        
        # extract only entry contents for summary generation
        entry_contents = [entry.content for entry in entries]
        entry_text = "\n".join(entry_contents)

        if(not entry_text.strip()):
            raise HTTPException(status_code=404, detail="No entry content found for the day to generate summary")

        [summary, tags] = ai_generate_summary_and_tags(entry_text)

        # Upsert Day metadata
        day_metadata = db.query(Day).filter(
            Day.user_id == user.id,
            Day.date == day,
        ).first()

        if day_metadata:
            day_metadata.summary = summary
            day_metadata.tags = tags
        else:
            day_metadata = Day(
                user_id=user.id,
                date=day,
                summary=summary,
                tags=tags,
            )
            db.add(day_metadata)
        db.commit()
        return day_metadata
    
    day_metadata = db.query(Day).filter(
        Day.user_id == user.id,
        Day.date == day,
    ).first()

    if not day_metadata:
        raise HTTPException(status_code=404, detail="Day metadata not found")

    return day_metadata