from functools import wraps
from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from app.core.templates import templates
from app.deps import optional_auth_cookie


def api_route():
    def decorator(route_func):
        @wraps(route_func)
        async def wrapper(
                request: Request,
                current_user=Depends(optional_auth_cookie),  # 添加用户依赖
                *args, **kwargs
        ):
            # 调用原始路由函数
            result = await route_func(request, *args, **kwargs)

            # 如果是字典结果，可以添加用户信息（可选）
            if isinstance(result, dict):
                result["current_user"] = current_user

            return result

        return wrapper

    return decorator


def template_route(template_name: str):
    def decorator(route_func):
        @wraps(route_func)
        async def wrapper(
                request: Request,
                current_user=Depends(optional_auth_cookie),
                *args, **kwargs
        ):
            # 调用原始路由函数获取页面数据
            page_data = await route_func(request, *args, **kwargs)

            # 确保返回的是字典
            if not isinstance(page_data, dict):
                page_data = {}

            # 合并模板数据
            template_data = {
                "request": request,
                "current_user": current_user,
                **page_data
            }
            return templates.TemplateResponse(template_name, template_data)

        return wrapper

    return decorator