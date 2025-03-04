from fastapi import FastAPI
from app.api.routes import router   

app = FastAPI()
   
app.include_router(router)


# from datetime import timedelta
# from app.core.security import hash_password, verify_password, create_access_token, decode_access_token

# # Test password hashing
# hashed_pw = hash_password("test123")
# print("Hashed Password:", hashed_pw)
# print("Password Verified:", verify_password("test123", hashed_pw))

# # Test token generation
# token = create_access_token({"sub": "user@example.com"}, timedelta(minutes=15))
# print("Access Token:", token)

# # Test token decoding
# decoded = decode_access_token(token)
# print("Decoded Token:", decoded)
