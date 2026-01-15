import random
from app.integrations.redis import get_redis_client
from app.core.security import verify_password, hash_password
import json

VERIFICATION_TTL = 300  # 5 minutes

def generate_otp() -> str:
    return str(random.randint(100000, 999999))


def store_verification_data(
    email: str,
    password: str,
) -> str:
    redis = get_redis_client()
    otp = generate_otp()

    redis.setex(
        name=f"signup:{email}",
        time=VERIFICATION_TTL,
        value=json.dumps(
        {
            "otp": otp,
            "password_hash": hash_password(password),
        }),
    )

    return otp


def verify_verification_data(
    email: str,
    otp: str,
    password: str,
) -> bool:
    redis = get_redis_client()
    key = f"signup:{email}"

    data = redis.get(key)
    if data:
        data = json.loads(data)
    if not data:
        return False

    if data["otp"] != otp:
        return False

    if not verify_password(password, data["password_hash"]):
        return False

    redis.delete(key)
    return True
