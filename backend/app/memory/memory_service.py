from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.models import Session, Message, Summary


async def create_session(
    db: AsyncSession,
    session_id: str,
):
    existing_session = await db.get(
        Session,
        session_id,
    )

    if existing_session:
        return existing_session

    new_session = Session(
        id=session_id,
    )

    db.add(new_session)

    await db.commit()
    await db.refresh(new_session)

    return new_session


async def save_message(
    db: AsyncSession,
    session_id: str,
    role: str,
    content: str,
):
    message = Message(
        session_id=session_id,
        role=role,
        content=content,
    )

    db.add(message)

    await db.commit()
    await db.refresh(message)

    return message


async def get_messages(
    db: AsyncSession,
    session_id: str,
):
    result = await db.execute(
        select(Message)
        .where(
            Message.session_id == session_id
        )
        .order_by(
            Message.created_at.asc()
        )
    )

    return result.scalars().all()


async def save_summary(
    db: AsyncSession,
    session_id: str,
    summary_text: str,
):
    result = await db.execute(
        select(Summary)
        .where(
            Summary.session_id == session_id
        )
    )

    existing_summary = result.scalar_one_or_none()

    if existing_summary:
        existing_summary.summary = summary_text

        await db.commit()
        await db.refresh(existing_summary)

        return existing_summary

    new_summary = Summary(
        session_id=session_id,
        summary=summary_text,
    )

    db.add(new_summary)

    await db.commit()
    await db.refresh(new_summary)

    return new_summary


async def get_summary(
    db: AsyncSession,
    session_id: str,
):
    result = await db.execute(
        select(Summary)
        .where(
            Summary.session_id == session_id
        )
    )

    return result.scalar_one_or_none()