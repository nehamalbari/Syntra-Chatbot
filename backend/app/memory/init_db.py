from app.memory.database import Base, engine
from app.memory import models


async def init_db():
    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.create_all
        )