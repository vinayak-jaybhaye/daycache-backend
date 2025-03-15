from fastapi import APIRouter
from app.api.routes import cache_chat, day, users, auth, entry, media

router = APIRouter()

router.include_router(users.router)
router.include_router(day.router)
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(entry.router)
router.include_router(media.router)
router.include_router(cache_chat.router)

