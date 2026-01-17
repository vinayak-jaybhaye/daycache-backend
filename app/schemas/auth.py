from pydantic import BaseModel, EmailStr, field_validator
from typing import Literal

class PasswordMixin(BaseModel):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long")
        elif len(value) > 16:
            raise ValueError("Password must be at most 16 characters long")
        return value

class SignupRequest(PasswordMixin):
    email: EmailStr
    otp: str

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("OTP must be numeric")
        if len(value) != 6:
            raise ValueError("OTP must be 6 digits long")
        return value

class LoginRequest(PasswordMixin):
    email: EmailStr

class GetOTPRequest(PasswordMixin):
    email: EmailStr
    purpose: Literal["signup", "reset_password"] = "signup"

class GoogleAuthRequest(BaseModel):
    google_token: str
  
class ResetPasswordRequest(PasswordMixin):
    email: EmailStr
    otp: str