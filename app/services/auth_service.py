from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models import User

from app.core.security import hash_password, verify_password
from app.services.email_services import send_signup_otp
from app.services.redis_otp_service import store_verification_data, verify_verification_data
from google.oauth2 import id_token
from google.auth.transport import requests
from app.core.config import settings

def authenticate_google_user(
    db: Session,
    google_token: str,
) -> User:
    try:
        payload = id_token.verify_oauth2_token(
            google_token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )
    
    email = payload.get("email")
    name = payload.get("name")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not available in Google token"
        )
    
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user
    
    new_user = User(
        email=email,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def verify_and_signup(
    db: Session,
    email: str,
    password: str,
    otp: str
) -> User:
    if not verify_verification_data(email, otp, password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )
    
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )

    new_user = User(
        email=email,
        password_hash=hash_password(password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def verify_and_login(
    db: Session,
    email: str,
    password: str
) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    return user

def verify_and_send_otp(
    db: Session,
    email: str,
    password: str,
    purpose: str,
) -> None:
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user and purpose == "signup":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    if not existing_user and purpose == "reset_password":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Generate, store (redis), and return OTP
    otp = store_verification_data(email, password)
    # Send the OTP via email
    send_signup_otp(email, otp)
    
  
def reset_password(
  db: Session,
  email: str,
  new_password: str,
  otp: str
) -> None:
    if not verify_verification_data(email, otp, new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.password_hash = hash_password(new_password)
    db.commit()