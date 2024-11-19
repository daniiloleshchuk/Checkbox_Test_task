from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
import os


SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://{user}:{password}@{hostname}/{database_name}".format(
    user=os.environ.get("POSTGRES_USER", "user"),
    password=os.environ.get("POSTGRES_PASSWORD", "password"),
    hostname=os.environ.get("DB_HOST", "host"),
    database_name=os.environ.get("POSTGRES_DB", "db")
)

print(SQLALCHEMY_DATABASE_URL)


engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
)

Base = declarative_base()


@asynccontextmanager
async def get_session() -> AsyncSession:
    session = AsyncSession(engine)
    try:
        yield session
    finally:
        await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
