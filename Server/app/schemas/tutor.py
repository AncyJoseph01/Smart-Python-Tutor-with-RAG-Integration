from pydantic import BaseModel
from datetime import datetime
from typing import List


# Request when asking a question
class TutorRequest(BaseModel):
    query: str
    user_id: int
    chat_session_id: int | None = None  # optional, if not provided → start new session


# Response for a single chat entry
class TutorResponse(BaseModel):
    id: int
    chat_session_id: int
    user_id: int
    query: str
    answer: str
    created_at: datetime

    class Config:
        from_attributes = True


# History of one chat session
class ChatHistory(BaseModel):
    chat_session_id: int
    chats: List[TutorResponse]
