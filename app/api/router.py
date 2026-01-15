from fastapi import APIRouter

from app.api.routes import auth, user, day, entry

router = APIRouter()

# Include the authentication routes
router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)

# Include the user management routes
router.include_router(
    user.router,
    prefix="/users",
    tags=["users"],
)

# Include the day management routes
router.include_router(
    day.router,
    prefix="/days",
    tags=["days"],
)

# Include the entry management routes
router.include_router(
    entry.router,
    prefix="/entries",
    tags=["entries"],
)