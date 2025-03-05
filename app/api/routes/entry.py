from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.entry import EntryCreate, EntryUpdate, EntryResponse, SuggestionResponse, SuggestionRequest
from app.services.automate.suggestions_service import generate_suggestions
from app.services.entry_services import create_entry, update_entry, get_entry, delete_entry, get_all_entries

router = APIRouter()

@router.post("/", response_model=EntryResponse, status_code=status.HTTP_201_CREATED)
def create_entry_endpoint(entry_data: EntryCreate, db: Session = Depends(get_db)):
    entry = create_entry(db, entry_data)
    return entry

@router.get("/{day_id}/{entry_id}", response_model=EntryResponse)
def read_entry(entry_id: int,day_id: int, db: Session = Depends(get_db)):
    entry = get_entry(db, entry_id, day_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@router.put("/{day_id}/{entry_id}", response_model=EntryResponse)
def update_entry_endpoint(entry_id: int, entry_data: EntryUpdate, db: Session = Depends(get_db)):
    entry = update_entry(db, entry_id, entry_data)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@router.delete("/{day_id}/{entry_id}")
def delete_entry_endpoint(entry_id: int, db: Session = Depends(get_db)):
    delete_entry(db, entry_id)
    return {"detail": "Entry deleted"}

@router.get("/{day_id}", response_model=list[EntryResponse])
def get_entries(day_id: int, db: Session = Depends(get_db)):
    entries = get_all_entries(db, day_id)
    return entries

@router.post("/suggest/{day_id}/{entry_id}", response_model=SuggestionResponse)
def suggest(day_id: int, entry_id: int, request: SuggestionRequest):
    # print(f"Day: {day_id}, Entry: {entry_id}, Content: {request.content}")
    suggested = generate_suggestions(request.content)
    return SuggestionResponse(suggested=suggested)


