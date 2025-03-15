from pydantic import BaseModel, EmailStr


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    otp: str


class SendOTPRequest(BaseModel):
    email: EmailStr