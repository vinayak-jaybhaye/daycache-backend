from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.core.security import hash_password, verify_password

def update_user(
    db: Session,
    user: User,
    email: str,
) -> User:
    user.email = email
    db.commit()
    db.refresh(user)
    return user

def change_user_password(
    db: Session,
    user: User,
    old_password: str,
    new_password: str,
) -> None:
    if not verify_password(old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect",
        )

    user.password_hash = hash_password(new_password)
    db.commit()

def delete_user_account(
    db: Session,
    user: User,
) -> None:
    db.delete(user)
    db.commit()