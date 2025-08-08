from typing import Annotated

from aioredis import Redis
from fastapi import Depends

from src.redis.service import redis_service

RedisDep = Annotated[Redis, Depends(redis_service.get_redis)]
