import functools

# app/deps/auth.py
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.utils.redis_client import redis_client
from app.utils.security import decode_access_token
from app import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def _get_user_by_token(token: str):
    """统一的根据token获取用户的核心函数"""
    if not token:
        return None

    try:
        user_id_str = decode_access_token(token)  # 明确变量名，表示它是字符串
        if not user_id_str:
            return None

        # 关键修复：将字符串ID转换为整数
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            # 如果转换失败（比如token被篡改，sub不是数字），则视为无效
            return None

        # 使用整数ID进行查询
        user = await models.User.get_or_none(id=user_id)
        return user
    except Exception:
        return None


# Header Token 认证 (用于API)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """API使用的必须认证依赖"""
    user = await _get_user_by_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return user


# Cookie 认证 (用于页面)
async def get_current_user_from_cookie(request: Request):
    """从Cookie中获取用户"""
    token = request.cookies.get("access_token")
    return await _get_user_by_token(token)


async def require_auth_cookie(current_user=Depends(get_current_user_from_cookie)):
    """页面使用的必须认证依赖"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要登录"
        )
    return current_user


async def optional_auth_cookie(current_user=Depends(get_current_user_from_cookie)):
    """页面使用的可选认证依赖"""
    return current_user

# 角色验证 (兼容两种认证方式)
async def get_current_admin(current_user=Depends(get_current_user)):
    """API管理员验证"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def get_current_registered_user(current_user=Depends(get_current_user)):
    """API注册用户验证"""
    if current_user.role == "admin" or current_user.role == "registered":
        return current_user
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

async def require_admin_cookie(current_user=Depends(require_auth_cookie)):
    """页面管理员验证"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    return current_user

def rate_limiter(key_prefix: str, limit: int = 5, ttl: int = 60):
    """
    防刷依赖装饰器，支持匿名用户(IP)和登录用户(user_id)
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 从参数中提取 request 和 current_user
            request = None
            current_user = None

            # 查找 request 参数
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            # 从关键字参数中查找
            if not request and 'request' in kwargs:
                request = kwargs['request']

            # 查找 current_user 参数
            if 'current_user' in kwargs:
                current_user = kwargs['current_user']
            else:
                # 也可以从 args 中查找，但需要知道位置
                pass

            # 生成限流键
            if current_user:
                key = f"{key_prefix}:user:{current_user.id}"
            elif request:
                key = f"{key_prefix}:ip:{request.client.host}"
            else:
                # 如果既没有用户也没有请求，使用默认键
                key = f"{key_prefix}:anonymous"

            count = await redis_client.get(key)
            if count is None:
                await redis_client.set(key, 1, ex=ttl)
            elif int(count) <= limit:
                await redis_client.incr(key)
            else:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"操作过于频繁，请 {ttl} 秒后再试"
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
