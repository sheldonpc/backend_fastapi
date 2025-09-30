import json
from decimal import Decimal
from typing import Any
from datetime import datetime, date

import redis.asyncio as redis
from app import config


def json_dumps(obj: Any) -> str:
    """
    安全地将 Python 对象转为 JSON 字符串，支持 Decimal、datetime、date。
    """
    def default(o):
        if isinstance(o, Decimal):
            return float(o)  # 或 str(o) 如果需要保留精度
        if isinstance(o, (datetime, date)):
            return o.isoformat()  # 转为 ISO 8601 字符串，如 "2025-09-30T14:38:02"
        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")
    return json.dumps(obj, default=default, ensure_ascii=False)


# 异步 Redis 客户端
redis_client = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=config.REDIS_DB,
    decode_responses=True  # 确保返回的是 str 而非 bytes
)


# === 验证码操作 ===
async def set_code(email: str, code: str, ttl: int = 300):
    """设置邮箱验证码，有效期默认 5 分钟"""
    key = f"code:{email}"
    await redis_client.set(key, code, ex=ttl)


async def get_code(email: str):
    """获取邮箱验证码"""
    key = f"code:{email}"
    return await redis_client.get(key)


async def delete_code(email: str):
    """删除邮箱验证码"""
    key = f"code:{email}"
    await redis_client.delete(key)


# === 通用缓存操作 ===
async def cache_set(key: str, value: Any, ttl: int = 300):
    """缓存任意 JSON 兼容数据，自动序列化，TTL 默认 5 分钟"""
    full_key = f"cache:{key}"
    await redis_client.set(full_key, json_dumps(value), ex=ttl)


async def cache_get(key: str):
    """从缓存获取数据，自动反序列化；未命中返回 None"""
    full_key = f"cache:{key}"
    data = await redis_client.get(full_key)
    if data is None:
        return None
    return json.loads(data)


async def cache_delete(key: str):
    """删除缓存项"""
    full_key = f"cache:{key}"
    await redis_client.delete(full_key)


# === 限流工具 ===
async def rate_limit(key: str, limit: int = 3, ttl: int = 60):
    """
    简单的计数限流：每 ttl 秒最多 limit 次。
    返回 True 表示允许，False 表示被限流。
    """
    full_key = f"rate:{key}"
    count = await redis_client.get(full_key)
    if count is None:
        await redis_client.set(full_key, 1, ex=ttl)
        return True
    elif int(count) < limit:
        await redis_client.incr(full_key)
        return True
    else:
        return False