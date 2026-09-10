import asyncio
import json
import logging
from asyncio import AbstractEventLoop
from typing import Any

import redis.asyncio as redis
from redis.exceptions import RedisError

from weatherender.config import Config

logger = logging.getLogger(__name__)


class AsyncCacheService:
    def __init__(self) -> None:
        """Initialize AsyncCacheService, keeping the connection client and loop uninitialized until first access."""
        self.client: redis.Redis | None = None
        self._loop: AbstractEventLoop | None = None

    def _get_client(self) -> redis.Redis:
        """Retrieve or create the asynchronous Redis client instance bound to the currently running asyncio event loop."""
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None
        if self.client is None or self._loop != current_loop:
            self._loop = current_loop
            self.client = redis.from_url(Config.REDIS_URL, decode_responses=True)
        return self.client

    async def close(self) -> None:
        """Asynchronously close the active Redis client connection if it is currently open."""
        if self.client is not None:
            try:
                await self.client.aclose()  # type: ignore[attr-defined]
            except RedisError:
                logger.warning("Error while closing cache client")

            self.client = None
            self._loop = None

    async def get(self, key: str) -> Any | None:
        """Asynchronously retrieve and JSON-decode the cached value associated with the specified key."""
        try:
            client = self._get_client()
            value = await client.get(key)
            if value is not None:
                return json.loads(value)
        except (RedisError, json.JSONDecodeError, RuntimeError) as err:
            logger.warning("Failed to get key '%s' from cache: %s", key, err)
        return None

    async def set(self, key: str, value: Any) -> None:
        """Asynchronously serialize the value to JSON and store it in cache with the default TTL."""
        try:
            client = self._get_client()
            json_value = json.dumps(value, default=str)
            await client.set(
                name=key,
                value=json_value,
                ex=Config.REDIS_TTL,
            )
        except (RedisError, TypeError, RuntimeError) as err:
            logger.warning("Failed to set key '%s' in cache: %s", key, err)


cache_service = AsyncCacheService()
