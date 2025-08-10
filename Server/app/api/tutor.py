from fastapi import APIRouter, HTTPException
from app.schemas.tutor import TutorRequest, TutorResponse  # Use TutorRequest, not TutorQuery
from app.AI.llm import get_tutor_reply_with_rag

router = APIRouter()

@router.post("/ask", response_model=TutorResponse)
async def ask_tutor(query: TutorRequest):   # use TutorRequest here
    try:
        answer = get_tutor_reply_with_rag(query.question)
        return TutorResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
