import json
import logging
from typing import Any

import redis
from redis.exceptions import RedisError

from weatherender.config import Config

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self) -> None:
        """Initialize the CacheService with a Redis client constructed from Config.REDIS_URL."""
        self.client: Any = redis.from_url(
            Config.REDIS_URL,
            decode_responses=True,
        )

    def get(self, key: str) -> Any | None:
        """Retrieve and JSON-decode the cached value associated with the specified key."""
        try:
            value = self.client.get(key)
            if value is not None:
                return json.loads(value)
        except (RedisError, json.JSONDecodeError) as err:
            logger.warning("Failed to get key '%s' from cache: %s", key, err)
            return None
        return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """JSON-serialize and save the value in the cache with the given key and optional TTL."""
        try:
            json_value = json.dumps(value)
            self.client.set(
                name=key,
                value=json_value,
                ex=ttl if ttl is not None else Config.REDIS_TTL,
            )
        except (RedisError, TypeError) as err:
            logger.warning("Failed to set key '%s' in cache: %s", key, err)
