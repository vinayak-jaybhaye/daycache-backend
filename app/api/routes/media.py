from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from typing import List
from app.schemas.media import MediaResponse, MediaSchema
from app.services.media_services import add_media_to_entry, delete_media_from_entry, get_single_media, get_media_for_entry

router = APIRouter()

@router.post("/{entry_id}/media", response_model=MediaResponse)
def upload_media(entry_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    return add_media_to_entry(db, entry_id, file)

@router.delete("/entries/{entry_id}/media/{media_id}", status_code=204)
def delete_media(entry_id: int, media_id: int, db: Session = Depends(get_db)):
    delete_media_from_entry(db, entry_id, media_id)

@router.get("/entries/{entry_id}/media", response_model=List[MediaSchema])
def list_media(entry_id: int, db: Session = Depends(get_db)):
    return get_media_for_entry(db, entry_id)

@router.get("/entries/{entry_id}/media/{media_id}", response_model=MediaSchema)
def retrieve_media(entry_id: int, media_id: int, db: Session = Depends(get_db)):
    media = get_single_media(db, entry_id, media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return media


