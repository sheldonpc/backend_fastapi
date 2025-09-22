import json
from typing import Any

import redis.asyncio as redis
from app import config

# 异步 Redis 客户端
redis_client = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=config.REDIS_DB,
    decode_responses=True
)

# 验证码操作
async def set_code(email: str, code: str, ttl: int = 300):
    key = f"code:{email}"
    await redis_client.set(key, code, ex=ttl)

async def get_code(email: str):
    key = f"code:{email}"
    return await redis_client.get(key)

async def delete_code(email: str):
    key = f"code:{email}"
    await redis_client.delete(key)

# 通用缓存操作
async def cache_set(key: str, value: Any, ttl: int = 300):
    key = f"cache:{key}"
    await redis_client.set(key, json.dumps(value), ex=ttl)

async def cache_get(key: str):
    key = f"cache:{key}"
    data = await redis_client.get(key)
    if data is None:
        return None
    return json.loads(data)

async def cache_delete(key: str):
    key = f"cache:{key}"
    await redis_client.delete(key)

# 限流工具
async def rate_limit(key: str, limit: int = 3, ttl: int = 60):
    key = f"rate:{key}"
    count = await redis_client.get(key)
    if count is None:
        await redis_client.set(key, 1, ex=ttl)
        return True
    elif int(count) < limit:
        await redis_client.incr(key)
        return True
    else:
        return False
