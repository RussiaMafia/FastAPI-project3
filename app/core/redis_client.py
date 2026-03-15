import redis
import json
from app.core.config import settings
from typing import Optional, Any

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


class RedisCache:
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None
    
    @staticmethod
    def set(key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache"""
        try:
            if ttl is None:
                ttl = settings.CACHE_TTL
            redis_client.setex(key, ttl, json.dumps(value))
            return True
        except Exception:
            return False
    
    @staticmethod
    def delete(key: str) -> bool:
        """Delete value from cache"""
        try:
            redis_client.delete(key)
            return True
        except Exception:
            return False
    
    @staticmethod
    def delete_pattern(pattern: str) -> bool:
        """Delete keys by pattern"""
        try:
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
            return True
        except Exception:
            return False


cache = RedisCache()