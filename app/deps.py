import functools
from typing import Optional

from fastapi import HTTPException, status, Request, Depends
from fastapi.security import OAuth2PasswordBearer

from app.utils.redis_client import redis_client
from app.utils.security import decode_access_token
from app import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# 用户身份验证和获取当前登录用户信息，实现了基于 OAuth2 令牌的身份验证流程
async def get_current_user(token: str = Depends(oauth2_scheme)):
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = await models.User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

# 角色验证
async def get_current_admin(current_user = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user

def rate_limiter(key_prefix: str, limit: int = 5, ttl: int = 60):
    """
    防刷依赖装饰器，支持匿名用户(IP)和登录用户(user_id)
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(
            request: Request,
            current_user: Optional = Depends(get_current_user),
            *args, **kwargs
        ):
            if current_user:
                key = f"{key_prefix}:user:{current_user.id}"
            else:
                key = f"{key_prefix}:ip:{request.client.host}"

            count = await redis_client.get(key)
            if count is None:
                await redis_client.set(key, 1, ex=ttl)
            elif int(count) < limit:
                await redis_client.incr(key)
            else:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"操作过于频繁，请 {ttl} 秒后再试"
                )

            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
