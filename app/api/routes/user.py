from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import (
    UserResponse,
    UpdateUserRequest,
    ChangePasswordRequest
)
from app.services.user_services import (
    update_user,
    change_user_password,
    delete_user_account
)
from app.core.security import delete_auth_cookie
from app.core.dependencies import get_current_user

router = APIRouter()

# token -> user data
@router.get("/me", response_model=UserResponse)
def get_user_details(
    current_user: User = Depends(get_current_user)
) -> User:
    return current_user

# token -> update user data
# @router.patch('/me', response_model=UserResponse)
# def update_user_details(
#     data: UpdateUserRequest,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     return update_user(
#         db=db,
#         user=current_user,
#         email=data.email,
#     )

# token, old_password, new_password -> change password
@router.post('/me/change-password')
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    change_user_password(
        db=db,
        user=current_user,
        old_password=data.old_password,
        new_password=data.new_password,
    )
    return {"detail": "Password changed successfully"}


# token -> delete account
@router.delete('/me')
def delete_account(
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_user_account(db=db, user=current_user)
    delete_auth_cookie(response)
    return {"detail": "User account deleted successfully"}