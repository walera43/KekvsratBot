from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeMeta, declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URI = ("sqlite+aiosqlite:///mem.db" + "?check_same_thread=False")

Base: DeclarativeMeta = declarative_base()


engine = create_async_engine(SQLALCHEMY_DATABASE_URI)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)