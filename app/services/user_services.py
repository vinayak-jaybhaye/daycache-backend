from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password
from app.services.cloudinary_services import upload_to_cloudinary, delete_from_cloudinary, get_complete_file_url


def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = hash_password(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_profile_image(user_id: int, file: UploadFile, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.profile_image:
        delete_from_cloudinary(user.profile_image)
    
    trimmed_url = upload_to_cloudinary(file)
    user.profile_image = trimmed_url
    db.commit()
    db.refresh(user)
    return user

def get_profile(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    user.profile_image = get_complete_file_url(user.profile_image) if user.profile_image else None
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user