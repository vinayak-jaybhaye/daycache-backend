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


@router.get("/set-cookie")
async def set_cookie():
    response = JSONResponse(content={"message": "Cookie is set"})
    response.set_cookie(
        key="access_token",
        value="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiaWQiOjEsImV4cCI6MTc0MTc1MDIxOH0.pZ6JjQRa7d98N72rZjgPmSNJcL5A6Txu5Go1DFbnpcM",
        httponly=True,
        secure=True,   # True if HTTPS
        samesite="None"  # None if frontend/backend are on different domains
    )
    
    return response


@router.get("/get-cookie")
async def get_cookie(request: Request , current_user: User = Depends(get_current_user)):
    print("Incoming Cookies:", request.cookies)  # Debug
    return {"cookies": request.cookies}