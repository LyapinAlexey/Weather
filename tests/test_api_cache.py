import json
from unittest.mock import AsyncMock, patch

import pytest
from redis.exceptions import RedisError

from weatherender.API.async_cache import AsyncCacheService


@pytest.mark.asyncio
class TestAsyncCacheService:
    @patch("weatherender.API.async_cache.redis.from_url")
    async def test_cache_get_success(self, mock_redis_from_url):
        mock_client = AsyncMock()
        mock_client.get.return_value = json.dumps({"test": "data"})
        mock_redis_from_url.return_value = mock_client

        cache = AsyncCacheService()
        result = await cache.get("my_key")

        assert result == {"test": "data"}
        mock_client.get.assert_called_once_with("my_key")

    @patch("weatherender.API.async_cache.redis.from_url")
    async def test_cache_get_redis_error_returns_none(self, mock_redis_from_url):
        mock_client = AsyncMock()
        mock_client.get.side_effect = RedisError("Connection lost")
        mock_redis_from_url.return_value = mock_client

        cache = AsyncCacheService()
        result = await cache.get("my_key")

        assert result is None

    @patch("weatherender.API.async_cache.redis.from_url")
    async def test_cache_set_success(self, mock_redis_from_url):
        mock_client = AsyncMock()
        mock_redis_from_url.return_value = mock_client

        cache = AsyncCacheService()
        await cache.set("my_key", {"data": 123})

        mock_client.set.assert_called_once()

    @patch("weatherender.API.async_cache.redis.from_url")
    async def test_cache_set_redis_error_handled(self, mock_redis_from_url):
        mock_client = AsyncMock()
        mock_client.set.side_effect = RedisError("Write error")
        mock_redis_from_url.return_value = mock_client

        cache = AsyncCacheService()
        await cache.set("my_key", {"data": 123})

    @patch("weatherender.API.async_cache.redis.from_url")
    async def test_cache_close_client(self, mock_redis_from_url):
        mock_client = AsyncMock()
        mock_redis_from_url.return_value = mock_client

        cache = AsyncCacheService()
        cache.client = mock_client
        await cache.close()

        mock_client.aclose.assert_awaited_once()

    @patch(
        "weatherender.API.async_cache.asyncio.get_running_loop",
        side_effect=RuntimeError,
    )
    @patch("weatherender.API.async_cache.redis.from_url")
    async def test_get_client_no_running_loop(self, mock_redis_from_url, mock_get_loop):
        cache = AsyncCacheService()
        client = cache._get_client()
        assert client is mock_redis_from_url.return_value
        assert cache._loop is None
        mock_redis_from_url.assert_called_once()

    @patch("weatherender.API.async_cache.redis.from_url")
    async def test_cache_close_redis_error(self, mock_redis_from_url):
        mock_client = AsyncMock()
        mock_client.aclose.side_effect = RedisError("Close error")
        mock_redis_from_url.return_value = mock_client

        cache = AsyncCacheService()
        cache.client = mock_client
        cache._loop = AsyncMock()
        await cache.close()

        assert cache.client is None
        assert cache._loop is None
