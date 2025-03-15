from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserLogin
from app.schemas.auth import VerifyOTPRequest, SendOTPRequest
from app.db.session import get_db
from app.models.user import User
from app.core.security import create_access_token, verify_password
from app.services.user_services import create_user as service_create_user
from app.services.otp_service import get_otp, delete_otp, store_otp
from app.services.email_services import send_email
import random
from app.services.cloudinary_services import get_complete_file_url
router = APIRouter()


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, otp: str = None, db: Session = Depends(get_db)):
    if otp is not None:
        # Step 1: Validate OTP
        stored_otp = get_otp(user.email)

        if stored_otp is None or stored_otp != otp:
           raise HTTPException(
               status_code=status.HTTP_400_BAD_REQUEST,
               detail="Invalid or expired OTP",
           )


        # Step 2: OTP is valid → Create user
        created_user = service_create_user(db, user)
        access_token = create_access_token({"sub": created_user.email, "id": created_user.id})
        
        # Remove OTP from Redis after successful signup
        delete_otp(user.email)

        return {
            "message": "User created successfully",
            "user_id": created_user.id,
            "access_token": access_token,
            "token_type": "bearer",
        }

    # Step 3: OTP is not provided → Send OTP
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Generate OTP and store in Redis (5 minutes expiry)
    otp = str(random.randint(100000, 999999))
    store_otp(user.email, otp, 300)

    # TODO: Send OTP via email (use a mail service)
    send_email(
        user.email,
        "Verify your email for signup",
        f"Your OTP for DayCache verification is: {otp}",
    )

    return {
        "message": "OTP sent to your email. Please verify to complete signup.",
    }



# Login
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    access_token = create_access_token({"sub": db_user.email, "id": db_user.id})
    # Set cookie in response
    user_data = {
        "id": db_user.id,
        "email": db_user.email,
        "username": db_user.username,
        "profile_image": get_complete_file_url(db_user.profile_image),
        "created_at": db_user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    }
    print(db_user)
    response = JSONResponse(content={"message": "Cookie is set", "user": user_data})
    print(access_token)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,   # True if HTTPS
        samesite="Lax"  # None if frontend/backend are on different domains
    )
    print("Cookie set")

    return response


# Logout
@router.post("/logout")
async def logout():
    response = JSONResponse(content={"message": "Cookie is removed"})
    response.delete_cookie("access_token")
    return response



@router.post("/send-otp", status_code=status.HTTP_200_OK)
def send_otp(request: SendOTPRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    otp = str(random.randint(100000, 999999))
    store_otp(request.email, otp, 300)  # 5 minutes expiry
    
    # Send OTP using email service
    send_email(
        request.email,
        "Verify Your Email",
        f"Your OTP is: {otp}",
    )

    return {"message": "OTP sent to your email"}


@router.post("/verify-otp", status_code=status.HTTP_201_CREATED)
def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    stored_otp = get_otp(request.email)
    if not stored_otp or stored_otp != request.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

    # Create user (pass username, email, and password)
    user = UserCreate(username=request.username, email=request.email, password=request.password)
    created_user = service_create_user(db, user)
    access_token = create_access_token({"sub": created_user.email, "id": created_user.id})

    # Remove OTP after successful verification
    delete_otp(request.email)



    # Set token in cookie
    response = JSONResponse(
        content={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": created_user.id,
                "email": created_user.email,
                "username": created_user.username,
                "created_at": created_user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        }
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="Lax"
    )
    
    return response
