from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.cache_chat import CacheChatResponse, CacheChatRequest
from app.services.automate.cache_chat_service import ask_cache_chat
from app.services.cache_chat_services import add_context
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter()

@router.post("/users/{user_id}/cachechat")
def ask(user_id: int, request: CacheChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    message = add_context(user_id, request.content, db)
    reply = ask_cache_chat(message)
    return reply