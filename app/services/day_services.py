from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import extract
from sqlalchemy import desc
from app.models.day import Day
from app.models.entry import Entry
from app.models.media import Media
from datetime import datetime, date
from typing import Optional
from app.services.automate.summary_service import generate_summary
from app.services.cloudinary_services import get_complete_file_url, get_resource_type

def get_day(user_id: int, date: str, db: Session):
    day = db.query(Day).filter(Day.date == date, Day.user_id == user_id).first()
    if not day:
        return None

    entries = (
        db.query(Entry)
        .filter(Entry.day_id == day.id)
        .options(joinedload(Entry.media))
        .all()
    )

    return {
        "date": day.date.strftime("%Y-%m-%d"),
        "id": day.id,
        "entries": [
            {
                "id": entry.id,
                "location": entry.location,
                "tags": entry.tags,
                "created_at": entry.created_at,
                "content": entry.content,
                "day_id": entry.day_id,
                "media": [{"id": media.id, "url": get_complete_file_url(media.file_url), "type" : get_resource_type(media.file_url)} for media in entry.media],
            }
            for entry in entries
        ],
        "latest_summary": day.latest_summary,
    }


def get_all_days(user_id: int, db: Session, last_date: Optional[date] = None, limit: int = 10):
    query = db.query(Day).filter(Day.user_id == user_id)

    if last_date:
        query = query.filter(Day.date < last_date)  # get days before last_date

    return query.order_by(desc(Day.date)).limit(limit).all()

def summarize_day(user_id: int, day_id: int, db: Session):
    day = db.query(Day).filter(Day.id == day_id, Day.user_id == user_id).first()
    if not day:
        return None
    
    entries = (
        db.query(Entry)
        .filter(Entry.day_id == day_id)
        # .options(joinedload(Entry.media))
        .all()
    )

    content = "\n".join(entry.content for entry in entries)
    summary = generate_summary(content)
    day.latest_summary = summary
    db.commit()
    db.refresh(day)
    return summary



def get_active_days(date: str, user_id: int, db: Session):
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    days = (
        db.query(Day)
        .filter(
            Day.user_id == user_id,
            extract('year', Day.date) == date_obj.year,
            extract('month', Day.date) == date_obj.month,
        )
        .all()
    )
    return [day.date.strftime("%Y-%m-%d") for day in days]