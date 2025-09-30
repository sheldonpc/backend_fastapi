import logging
from asyncio import create_task
import asyncio
from typing import Optional

from app.routers.root import _build_homepage_data, CACHE_KEY, CACHE_TTL
from app.utils.redis_client import cache_set

_background_task: Optional[asyncio.Task] = None

logger = logging.getLogger(__name__)

async def _warm_homepage_cache():
    """后台定时刷新首页缓存"""
    while True:
        try:
            data = await _build_homepage_data()
            await cache_set(CACHE_KEY, data, ttl=CACHE_TTL + 5)
        except Exception as e:
            logger.error(f"首页缓存预热任务出错: {e}")

        await asyncio.sleep(CACHE_TTL)  # 每 30 秒刷新一次

async def start_cache_warmup():
    global _background_task
    if _background_task is None or _background_task.done():
        _background_task = asyncio.create_task(_warm_homepage_cache())
        logger.info("✅ 启动首页缓存预热任务")

def stop_cache_warmup():
    global _background_task
    if _background_task and not _background_task.done():
        _background_task.cancel()
        logger.info("🛑 停止首页缓存预热任务")