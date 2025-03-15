from sqlalchemy.orm import Session, joinedload
from app.models.day import Day
from app.models.entry import Entry
from app.models.media import Media
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


def get_all_days(user_id: int, db: Session):
    days = db.query(Day).filter(Day.user_id == user_id).all()
    return days

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
