import asyncio
import logging

from src.kafka.constants import KafkaConstant
from src.kafka.schemas import SKafkaMessageAll
from src.services.stock_services import StockService

logger = logging.getLogger(__name__)

semaphore = asyncio.Semaphore(KafkaConstant.MAX_CONCURRENT_TASKS)


async def handle_message(message: dict):
    try:
        await StockService.processing_message(SKafkaMessageAll(**message))
    except Exception as e:
        logger.exception(f"Failed to process message: {message} — {e}")
        raise e


async def limited_handle_message(msg_value):
    async with semaphore:
        await handle_message(msg_value)
