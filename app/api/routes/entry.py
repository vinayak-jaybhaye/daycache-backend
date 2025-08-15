from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_current_user
from datetime import datetime
from app.db.session import get_db
from app.services.automate.recommendations import recommendations
from app.services.entry_services import create_entry_in_db, update_entry_in_db, delete_entry_in_db, get_all_entries

router = APIRouter()

@router.patch("/entries/{entry_id}/update")  
async def update_entry(
    entry_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):  
    data = await request.json()  
    content = data.get("content")  

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content cannot be empty"
        )
    
    updated_entry = update_entry_in_db(entry_id, content, db)
    if not updated_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )

    return {"message": "Entry updated successfully", "entry": updated_entry}

@router.delete("/days/{day_id}/entries/{entry_id}/delete")
def delete_entry(
    day_id: int,
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return delete_entry_in_db(day_id, entry_id, db)

@router.post("/users/{user_id}/days/{date}/entries/create")
async def create_new_entry(
    user_id: int,
    date: str,  # Use date instead of day_id
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = await request.json()  

    if not data.get("content"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content cannot be empty"
        )

    # Convert date string to datetime.date object
    try:
        day_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format (use YYYY-MM-DD)"
        )

    # Pass the converted date to the function
    entry = create_entry_in_db(user_id, day_date, data, db)
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create entry"
        )
    
    return {"message": "Entry created successfully", "entry": entry}

@router.post("/autocomplete")
async def autocomplete_entry(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Parse the JSON content
    try:
        body = await request.json()
        content = body.get("content")
        if not content:
            return {"error": "Content is required for autocomplete."}
    except Exception as e:
        return {"error": f"Invalid JSON: {str(e)}"}

    suggestions = recommendations(content, 1)

    return {"suggestions": suggestions}

