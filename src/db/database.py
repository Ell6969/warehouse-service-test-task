from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool

from src.db.config import settings

ASYNC_DATABASE_PARAMS = {
    "poolclass": AsyncAdaptedQueuePool,
    "pool_size": 20,
    "max_overflow": 20,
    "pool_timeout": 30,
}

_engine_async = create_async_engine(settings.DATABASE_URL, **ASYNC_DATABASE_PARAMS)
async_session_maker = sessionmaker(_engine_async, class_=AsyncSession, expire_on_commit=False)

AsyncSessionDep = Annotated[AsyncSession, Depends(async_sessionmaker)]


class Base(DeclarativeBase):
    pass
