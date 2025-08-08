import asyncio
import json
import logging
from typing import Awaitable, Callable

from aiokafka import AIOKafkaConsumer

from src.kafka.config import kafka_settings
from src.kafka.constants import KafkaConstant
from src.kafka.handlers import limited_handle_message

logger = logging.getLogger(__name__)


def safe_json_deserializer(m):
    try:
        return json.loads(m.decode("utf-8"))
    except Exception as e:
        logger.error(f"❌ Ошибка при десериализации JSON: {e}. Raw: {m}")
        return None


class KafkaConsumerService:
    def __init__(
        self,
        topic: str,
        bootstrap_servers: str,
        group_id: str,
        value_deserializer: Callable,
        handler: Callable[[dict], Awaitable[None]],
        rerun_delay: int = KafkaConstant.RERUN_KAFKA_SLEEP,
    ):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.value_deserializer = value_deserializer
        self.handler = handler
        self.rerun_delay = rerun_delay
        self.stop_event = asyncio.Event()
        self.consumer: AIOKafkaConsumer | None = None

    async def start(self):
        """Запуск consumer с автоматическим перезапуском при сбоях"""
        while not self.stop_event.is_set():
            try:
                logger.info("🟢 Запуск Kafka consumer...")
                await self._consume()
            except Exception as e:
                logger.exception(f"🔴 Ошибка Kafka consumer, перезапуск через {self.rerun_delay} сек: %s", e)
                await asyncio.sleep(self.rerun_delay)

    async def _consume(self):
        """Подключение и чтение сообщений"""
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=self.value_deserializer,
            enable_auto_commit=True,
            auto_offset_reset="earliest",
        )
        await self.consumer.start()
        logger.info(f"Kafka consumer listening to topic: {self.topic}")

        try:
            async for msg in self.consumer:
                asyncio.create_task(self.handler(msg.value))
        finally:
            await self.consumer.stop()

    async def stop(self):
        """Остановка consumer"""
        self.stop_event.set()
        if self.consumer:
            await self.consumer.stop()
        logger.info("🛑 Kafka consumer остановлен")


consumer_service = KafkaConsumerService(
    topic=kafka_settings.KAFKA_TOPIC,
    bootstrap_servers=kafka_settings.KAFKA_BOOTSTRAP_SERVERS,
    group_id=kafka_settings.KAFKA_CONSUMER_GROUP,
    value_deserializer=safe_json_deserializer,
    handler=limited_handle_message,
)

if __name__ == "__main__":
    # запуск как воркера, отдельно
    try:
        asyncio.run(consumer_service.start())
    finally:
        asyncio.run(consumer_service.stop())
