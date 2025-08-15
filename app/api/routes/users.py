from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.core.security import get_current_user
from app.services.user_services import update_profile_image, get_profile

router = APIRouter()

@router.get("/users/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):  
    return get_profile(current_user.id, db)


@router.put("/users/me/update-image")
def update_profile_img(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_profile_image(current_user.id, file, db)