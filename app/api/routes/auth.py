from fastapi import APIRouter, Depends, Response
from app.db.session import get_db
from sqlalchemy.orm import Session

# schemas
from app.schemas.auth import (
    SignupRequest,
    GetOTPRequest,
    LoginRequest,
    GoogleAuthRequest,
    ResetPasswordRequest,
)
from app.services.auth_service import (
    verify_and_signup,
    verify_and_login,
    verify_and_send_otp,
    authenticate_google_user,
    reset_password,
)

from app.core.security import set_auth_cookie, delete_auth_cookie

router = APIRouter()

# email, password, otp -> verify otp, create user, return token
@router.post("/signup")
def signup(
    data: SignupRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    user = verify_and_signup(
        db=db,
        email=data.email,
        password=data.password,
        otp=data.otp,
    )

    set_auth_cookie(response, user)
    return {"message": "Signup successful"}


# email password -> verify, return token
@router.post("/login")
def login(
    data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    user = verify_and_login(
        db=db,
        email=data.email,
        password=data.password,
    )
    set_auth_cookie(response, user)
    return {"message": "Login successful"}

# verify google token -> get/create user, return token
@router.post("/google-auth")
def google_auth(
    data: GoogleAuthRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    user = authenticate_google_user(
        db=db,
        google_token=data.google_token,
    )
    set_auth_cookie(response, user)
    return {"message": "Google authentication successful"}

# token -> invalidate token
@router.post("/logout")
def logout(response: Response):
    delete_auth_cookie(response)
    return {"message": "Logout successful"}

# email, password -> sends otp
@router.post("/get-otp")
def get_otp(
    data: GetOTPRequest,
    db: Session = Depends(get_db),
):
    verify_and_send_otp(
        db=db,
        email=data.email,
        password=data.password,
    )
    return {"message": "OTP sent successfully"}

@router.post("/reset-password")
def reset_password_route(
  data: ResetPasswordRequest,
  db: Session = Depends(get_db),
):
    reset_password(
      db=db,
      email=data.email,
      new_password=data.password,
      otp=data.otp,
    )
    return {"message": "Password reset successful"}
    