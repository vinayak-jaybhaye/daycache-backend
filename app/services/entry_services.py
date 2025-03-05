from sqlalchemy.orm import Session
from app.models.entry import Entry
from app.schemas.entry import EntryCreate, EntryUpdate

def create_entry(db: Session, entry_data: EntryCreate) -> Entry:
    entry = Entry(
        day_id=entry_data.day_id,
        location=entry_data.location,
        content=entry_data.content,
        tags=entry_data.tags
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def update_entry(db: Session, entry_id: int, entry_data: EntryUpdate) -> Entry:
    entry = db.query(Entry).filter(Entry.id == entry_id).first()
    if not entry:
        return None
    for key, value in entry_data.model_dump().items():
        setattr(entry, key, value)
    db.commit()
    db.refresh(entry)
    return entry

def get_entry(db: Session, entry_id: int, day_id: int) -> Entry:
    return db.query(Entry).filter((Entry.id == entry_id) & (Entry.day_id == day_id)).first()

def delete_entry(db: Session, entry_id: int):
    entry = db.query(Entry).filter(Entry.id == entry_id).first()
    if entry:
        db.delete(entry)
        db.commit()

def get_all_entries(db: Session, day_id: int):
    return db.query(Entry).filter(Entry.day_id == day_id).all()