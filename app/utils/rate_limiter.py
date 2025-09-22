from fastapi import Request, HTTPException, status, Depends
from app.utils.redis_client import rate_limit

def rate_limiter(action: str, limit: int = 3, ttl: int = 60):
    """
    返回一个依赖函数，用于接口限流。
    """
    async def dependency(request: Request):
        client_ip = request.client.host
        key = f"{action}:{client_ip}"
        allowed = await rate_limit(key, limit=limit, ttl=ttl)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="请求过于频繁，请稍后再试"
            )
    return dependency
