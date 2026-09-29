from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.llm_service import LLMService

router = APIRouter(prefix="/api", tags=["Question Answering"])

llm_service = LLMService()


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    answer = await llm_service.generate_response(
        request.question
    )

    return AnswerResponse(answer=answer)