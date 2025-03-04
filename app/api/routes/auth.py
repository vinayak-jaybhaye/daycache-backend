from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserLogin
from app.db.session import get_db
from app.models.user import User
from app.core.security import create_access_token, verify_password
from app.services.user_service import create_user as service_create_user

router = APIRouter()


# Signup
@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    created_user = service_create_user(db, user)
    access_token = create_access_token({"sub": created_user.email})

    return {
        "message": "User created successfully",
        "user_id": created_user.id,
        "access_token": access_token,
        "token_type": "bearer"
    }
    

# Login
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    access_token = create_access_token({"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}


#Logout
@router.post("/logout")
async def logout():
    fake_token = "logged_out_token"  # Can also generate a random string
    return {
        "message": "Logged out successfully",
        "access_token": fake_token,
        "token_type": "bearer"
    }
