from fastapi import APIRouter, Depends, Query
from datetime import date
from sqlalchemy.orm import Session
from typing import Optional, List, Union
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.db.models.user import User
from app.services.day_service import (
    list_active_days,
    get_day_entries,
    delete_day_and_entries,
    delete_day_metadata,
    get_day_metadata,
)
from app.schemas.day import ListDaysQuery, DayResponse, DayMetadata

router = APIRouter()

# user, range -> active days list (derived from entries)
@router.get(
    "/",
    response_model=Union[List[date], List[DayResponse]],
    response_model_exclude_none=True
)
def list_days(
    query: ListDaysQuery = Depends(),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return list_active_days(
        db=db,
        user=user,
        start_date=query.start_date,
        end_date=query.end_date,
        limit=query.limit,
        offset=query.offset,
        include_metadata=query.include_metadata
    )

# user, date -> entry list
@router.get("/{date}")
def get_day(
    date: date,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
   return get_day_entries(db, user, date)     

# user, date -> delete day (and its entries)
@router.delete("/{date}")
def delete_day(
    date: date,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    delete_day_and_entries(db, user, date)
    return {"detail": "Day entries deleted"} 


#### day metadata routes ####

# user, date -> day with summary and tags
@router.get("/{date}/metadata", response_model=DayMetadata)
def get_day_metadata_route(
    date: date,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
   return  get_day_metadata(db, user, date)


# user, date -> clear day summary and tags 
@router.delete("/{date}/metadata")
def clear_day_metadata(
    date: date,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # This actually just deletes the Day entry, which removes summary and tags
    delete_day_metadata(db, user, date)
    return {"detail": "Day cleared"}


# user, date -> generate day summary and tags
@router.get("/{date}/generate-summary", response_model=DayMetadata)
def generate_day_summary_route(
    date: date,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return  get_day_metadata(db, user, date, generate_summary=True)