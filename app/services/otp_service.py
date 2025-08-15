from app.db.redis import get_redis_client

redis_client = get_redis_client()

def store_otp(email: str, otp: str, expiry_seconds: int = 300):
    print(f"otp::store:{email}")
    redis_client.setex(f"otp:{email}", expiry_seconds, otp)

def get_otp(email: str) -> str:
    print(f"otp::get:{email}")
    return redis_client.get(f"otp:{email}")

def delete_otp(email: str):
    print(f"otp::delete :{email}")
    redis_client.delete(f"otp:{email}")
