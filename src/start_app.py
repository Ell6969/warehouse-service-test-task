import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.kafka.consumer import consumer_service
from src.redis.service import redis_service

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Задачи при запуске приложения и остановке.
    """
    consumer_task = None
    try:
        await redis_service.init()

        consumer_task = asyncio.create_task(consumer_service.start())
        yield
    except Exception as e:
        logger.info(f"🟡 Ошибка при старте - {e}")
    finally:
        await consumer_service.stop()
        consumer_task.cancel()
        await consumer_task
