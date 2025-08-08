import logging

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from redis import Redis
from redis import asyncio as aioredis
from src.db.config import settings
from src.redis.constant import RedisConstant

logger = logging.getLogger(__name__)


class RedisService:
    """
    Класс для работы с Redis.
    Асинхронно инициализируется, предоставляет Redis клиент.
    """

    def __init__(self):
        self._redis_db: Redis | None = None

    async def init(self) -> None:
        """
        Асинхронная инициализация Redis клиента и FastAPICache.
        Вызывать один раз при старте приложения.
        """
        if self._redis_db is None:
            self._redis_db = await aioredis.from_url(settings.REDIS_CACHE_URL, encoding="utf8", decode_responses=True)
            FastAPICache.init(RedisBackend(self._redis_db), prefix=RedisConstant.CACHE_PREFIX)
            logger.info("Redis инициализирован и FastAPICache настроен")

    def get_redis(self) -> Redis:
        """
        Получить инициализированный Redis клиент.
        Если не инициализирован — выбрасывает ошибку.
        """
        if self._redis_db is None:
            logger.warning("Redis не инициализирован")
            raise RuntimeError("Redis не инициализирован. Вызовите init() при старте.")
        return self._redis_db

    async def clear_cache_by_path_params(self, namespace: str = RedisConstant.CACHE_PREFIX, **path_params) -> None:
        """
        Очистить кэш по namespace и path параметрам.

        Пример вызова:
        await clear_cache_by_path_params("cache", warehouse_id=..., product_id=...)
        """
        if self._redis_db is None:
            logger.warning("Redis не инициализирован")
            raise RuntimeError("Redis не инициализирован. Вызовите init() при старте.")

        if not path_params:
            raise ValueError("Не указаны path параметры для очистки кэша")

        key_parts = [namespace] + [str(value) for value in path_params.values()]
        cache_key = ":".join(key_parts)

        deleted = await self._redis_db.delete(cache_key)
        if deleted:
            logger.info(f"Кэш очищен для ключа {cache_key}")
        else:
            logger.info(f"Ключ {cache_key} не найден в кэше")


redis_service = RedisService()
