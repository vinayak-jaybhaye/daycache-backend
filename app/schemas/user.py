from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime


class UserResponse(BaseModel):
    id: int 
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateUserRequest(BaseModel):
    email: EmailStr

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        if len(value) < 6:
            raise ValueError("New password must be at least 6 characters long")
        if len(value) > 16:
            raise ValueError("New password must be at most 16 characters long")
        return value