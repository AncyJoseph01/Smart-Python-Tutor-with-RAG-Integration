from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import insert, select, func
from app.schemas.tutor import TutorRequest, TutorResponse, ChatHistory
from app.AI.llm import get_tutor_reply_with_rag
from app.db.database import database
from app.db.models import Chat, User
from typing import List

router = APIRouter()

async def validate_user(user_id: int):
    """Validate if user exists."""
    query = select(User).where(User.id == user_id)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_next_session_id(user_id: int) -> int:
    """Generate a new chat_session_id for the user."""
    query = select(func.max(Chat.chat_session_id)).where(Chat.user_id == user_id)
    max_session_id = await database.fetch_val(query)
    return (max_session_id or 0) + 1

@router.post("/ask", response_model=TutorResponse)
async def ask_tutor(request: TutorRequest):
    await validate_user(request.user_id)
    try:
        # Reject chat_session_id: 0 explicitly
        if request.chat_session_id == 0:
            raise HTTPException(status_code=400, detail="chat_session_id cannot be 0. Omit it to start a new session or use a valid session ID.")

        # Validate or generate chat_session_id
        if request.chat_session_id is None:
            request.chat_session_id = await get_next_session_id(request.user_id)
        else:
            # Verify chat_session_id belongs to user
            query = select(Chat).where(
                Chat.chat_session_id == request.chat_session_id,
                Chat.user_id == request.user_id
            )
            existing_chat = await database.fetch_one(query)
            if not existing_chat and request.chat_session_id != await get_next_session_id(request.user_id):
                raise HTTPException(status_code=400, detail=f"Invalid chat_session_id {request.chat_session_id} for user {request.user_id}")

        # Get AI answer (remove await if synchronous)
        answer = get_tutor_reply_with_rag(request.query)  # Changed from await

        # Insert into DB
        query_stmt = (
            insert(Chat)
            .values(
                chat_session_id=request.chat_session_id,
                user_id=request.user_id,
                query=request.query,
                answer=answer,
            )
            .returning(Chat.id, Chat.chat_session_id, Chat.user_id, Chat.query, Chat.answer, Chat.created_at)
        )

        new_chat = await database.fetch_one(query_stmt)
        if not new_chat:
            raise HTTPException(status_code=500, detail="Failed to save chat")

        return TutorResponse.model_validate(new_chat)

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Bad request: {str(ve)}")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/history/{user_id}/{chat_session_id}", response_model=ChatHistory)
async def get_chat_history(user_id: int, chat_session_id: int, _=Depends(validate_user)):
    try:
        query = (
            select(Chat)
            .where(Chat.user_id == user_id, Chat.chat_session_id == chat_session_id)
            .order_by(Chat.created_at)
        )
        chats = await database.fetch_all(query)
        if not chats:
            raise HTTPException(status_code=404, detail="Chat session not found")

        return ChatHistory(
            chat_session_id=chat_session_id,
            chats=[TutorResponse.model_validate(chat) for chat in chats]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/sessions/{user_id}", response_model=List[int])
async def get_user_sessions(user_id: int, _=Depends(validate_user)):
    try:
        query = select(Chat.chat_session_id).where(Chat.user_id == user_id).distinct()
        sessions = await database.fetch_all(query)
        return [session.chat_session_id for session in sessions]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")