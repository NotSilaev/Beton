from config import project_settings

import redis


redis_pool = redis.ConnectionPool(
    host=project_settings.CACHE_HOST,
    port=project_settings.CACHE_PORT,
    db=project_settings.CACHE_DB,
    max_connections=project_settings.CACHE_MAX_CONNECTIONS,
)


MINUTE_SECONDS = 60
HOUR_SECONDS = MINUTE_SECONDS ** 2
DAY_SECONDS = HOUR_SECONDS * 24


class Cache:
    def __init__(self) -> None:
        self.redis_client = redis.Redis(connection_pool=redis_pool)

    def setValue(self, key: str, value: str, expire: int = DAY_SECONDS) -> None:
        self.redis_client.set(key, value, ex=expire)
 
    def getValue(self, key: str) -> str | None:
        value: bytes | None = self.redis_client.get(key)
        if value:
            return value.decode('utf-8')

    def deleteKey(self, key: str) -> None:
        self.redis_client.delete(key)

    def getKeyTTL(self, key: str) -> int | None:
        ttl = self.redis_client.ttl(key)
        if ttl not in [-2, -1]:
            return ttl
