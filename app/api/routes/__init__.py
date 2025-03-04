from fastapi import APIRouter
from app.api.routes import day, users, auth

router = APIRouter()

router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(day.router, prefix="/day", tags=["day"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])