import json
from typing import Any

import redis


class RedisCache:
    """
    Redis-backed cache implementing the same interface
    as MemoryCache.

    Methods:
        get()
        set()
        delete()
        clear()
        contains()
        size()
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        prefix: str = "raglink:",
        ttl: int | None = 3600,
    ):

        self.prefix = prefix
        self.ttl = ttl

        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True,
        )

    def _key(self, key: str) -> str:
        return f"{self.prefix}{key}"

    def get(self, key: str):

        if not key:
            return None

        value = self.client.get(self._key(key))

        if value is None:
            return None

        try:
            return json.loads(value)
        except Exception:
            return value

    def set(self, key: str, value: Any):

        if not key:
            return

        try:
            value = json.dumps(value)
        except Exception:
            value = str(value)

        if self.ttl is None:

            self.client.set(
                self._key(key),
                value,
            )

        else:

            self.client.setex(
                self._key(key),
                self.ttl,
                value,
            )

    def delete(self, key: str):

        if not key:
            return

        self.client.delete(
            self._key(key)
        )

    def clear(self):

        keys = self.client.keys(
            f"{self.prefix}*"
        )

        if keys:
            self.client.delete(*keys)

    def contains(self, key: str):

        if not key:
            return False

        return bool(
            self.client.exists(
                self._key(key)
            )
        )

    def size(self):

        return len(
            self.client.keys(
                f"{self.prefix}*"
            )
        )