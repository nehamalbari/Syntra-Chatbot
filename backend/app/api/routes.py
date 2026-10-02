from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.llm_service import LLMService
from app.memory.database import get_db
from app.memory.memory_service import (
    create_session,
    save_message,
    get_messages,
    save_summary,
    get_summary,
    get_all_sessions,
    update_session_title,
    update_missing_session_titles,
)
from app.middleware.summarization import (
    SummarizationService,
)


router = APIRouter(
    prefix="/api",
    tags=["Question Answering"],
)


llm_service = LLMService()
summarization_service = SummarizationService()


class QuestionRequest(BaseModel):
    session_id: str
    question: str


class AnswerResponse(BaseModel):
    session_id: str
    answer: str


@router.post(
    "/ask",
    response_model=AnswerResponse,
)
async def ask_question(
    request: QuestionRequest,
    db: AsyncSession = Depends(get_db),
):
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    if not request.session_id.strip():
        raise HTTPException(
            status_code=400,
            detail="Session ID cannot be empty.",
        )

    # Create session if it does not already exist
    await create_session(
        db=db,
        session_id=request.session_id,
        title=request.question[:200],
    )

    # Retrieve previous conversation
    history = await get_messages(
        db,
        request.session_id,
    )

    # Retrieve existing summary
    existing_summary = await get_summary(
        db,
        request.session_id,
    )

    # Save current user message
    await save_message(
        db=db,
        session_id=request.session_id,
        role="user",
        content=request.question,
    )

    # Select context for the LLM
    if existing_summary:
        context_history = history[-6:]
    else:
        context_history = history

    # Generate answer
    answer = await llm_service.generate_response(
        question=request.question,
        history=context_history,
        summary=(
            existing_summary.summary
            if existing_summary
            else None
        ),
    )

    # Save assistant response
    await save_message(
        db=db,
        session_id=request.session_id,
        role="assistant",
        content=answer,
    )

    # Retrieve updated conversation
    updated_history = await get_messages(
        db,
        request.session_id,
    )

    # Generate summary when conversation becomes long
    if len(updated_history) > 10:

        older_messages = updated_history[:-6]

        try:

            summary = await summarization_service.summarize(
                older_messages
            )

            await save_summary(
                db=db,
                session_id=request.session_id,
                summary_text=summary,
            )

        except Exception as exc:

            print(
                f"Summarization skipped: {exc}"
            )

    return AnswerResponse(
        session_id=request.session_id,
        answer=answer,
    )

@router.get("/sessions")
async def get_sessions(
    db: AsyncSession = Depends(get_db),
):
    sessions = await get_all_sessions(db)

    return [
        {
            "session_id": session.id,
            "title": session.title,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
        }
        for session in sessions
    ]

@router.post("/sessions/update-titles")
async def update_session_titles(
    db: AsyncSession = Depends(get_db),
):
    sessions = await update_missing_session_titles(db)

    return {
        "message": "Session titles updated.",
        "updated_sessions": len(sessions),
    }

@router.get("/sessions/{session_id}")
async def get_session_messages(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    messages = await get_messages(
        db,
        session_id,
    )

    return {
        "session_id": session_id,
        "messages": [
            {
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at,
            }
            for message in messages
        ],
    }