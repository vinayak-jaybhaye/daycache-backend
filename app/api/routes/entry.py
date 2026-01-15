from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.db.models import User
from app.schemas.entry import (
    EntryCreate,
    EntryUpdate,
    EntryResponse,
)

from app.services.entry_services import (
    create_entry,
    get_entry,
    search_entries,
    update_entry,
    delete_entry,
)

router = APIRouter()

# 
@router.post("/")
def create_entry_route(
    data: EntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not data.entry_date:
        data.entry_date = date.today()
    return create_entry(
        db = db,
        user = current_user,
        content = data.content,
        entry_date = data.entry_date
    )


@router.get("", response_model=List[EntryResponse])
def list_entries(
    q: Optional[str] = Query(default=None, description="Search text"),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return search_entries(
        db=db,
        user=current_user,
        q=q,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )


@router.get("/{entry_id}", response_model=EntryResponse)
def get_entry_route(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_entry(
        db=db,
        user=current_user,
        entry_id=entry_id,
    )

@router.patch("/{entry_id}", response_model=EntryResponse)
def update_entry_route(
    entry_id: int,
    data: EntryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_entry(
        db=db,
        user=current_user,
        entry_id=entry_id,
        content=data.content,
    )

@router.delete("/{entry_id}")
def delete_entry_route(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_entry(
        db=db,
        user=current_user,
        entry_id=entry_id,
    )
    return {"message": "Entry deleted"}
