import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Response
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


# JWT helpers


def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = data.copy()
    payload["exp"] = expire

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        return None


# Cookie helpers


def set_auth_cookie(response: Response, user) -> None:
    token = create_access_token({"sub": user.email, "id": user.id})

    ### DEV
    # response.set_cookie(
    #     key="access_token",
    #     value=token,
    #     httponly=True,
    #     secure=False,
    #     samesite="lax",
    #     path="/",
    #     max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    # )

    ### PROD
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def delete_auth_cookie(response: Response) -> None:
    ## DEV
    # response.delete_cookie(
    #     key="access_token",
    #     path="/",
    #     httponly=True,
    #     samesite="lax",
    # )

    ## PROD
    response.delete_cookie(
        key="access_token",
        path="/",
        samesite="none",
        secure=True,
    )
