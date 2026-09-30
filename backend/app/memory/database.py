from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    pass


database_url = settings.database_url

# Convert PostgreSQL URL to asyncpg format
if database_url.startswith("postgresql://"):
    database_url = database_url.replace(
        "postgresql://",
        "postgresql+asyncpg://",
        1,
    )

# Remove parameters that are not needed in the SQLAlchemy/asyncpg URL.
# SSL is configured explicitly below.
parts = urlsplit(database_url)

query_params = dict(parse_qsl(parts.query))

query_params.pop("sslmode", None)
query_params.pop("channel_binding", None)

database_url = urlunsplit(
    (
        parts.scheme,
        parts.netloc,
        parts.path,
        urlencode(query_params),
        parts.fragment,
    )
)


engine = create_async_engine(
    database_url,
    echo=False,
    pool_pre_ping=True,
    connect_args={
        "ssl": "require",
    },
)


AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session