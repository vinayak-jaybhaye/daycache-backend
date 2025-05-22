from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from typing import List
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.media import MediaResponse, MediaSchema
from app.services.media_services import add_media_to_entry, delete_media_from_entry

router = APIRouter()

@router.delete("/media/{media_id}/delete")
def delete_media(
    media_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return delete_media_from_entry(media_id, db)

@router.put("/users/{user_id}/days/{day_id}/entries/{entry_id}/media/add")
def add_media(
    user_id: int,
    day_id: int,
    entry_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    return add_media_to_entry(entry_id, file, db)