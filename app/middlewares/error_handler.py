from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from starlette.routing import NoMatchFound
from app.utils.logger import logger
from app.exceptions import PermissionDenied
import urllib.parse


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    处理HTTP异常，如404、403等
    """
    logger.error(f"HTTP异常: {exc.status_code} - {exc.detail}")

    # 检查是否是API请求或者是FastAPI内置路由
    is_api_request = request.url.path.startswith("/api/") or is_fastapi_builtin_route(request.url.path)

    if is_api_request:
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail, "status_code": exc.status_code}
        )

    # 对于页面请求，重定向到错误页面
    error_page = f"/error?status={exc.status_code}&message={urllib.parse.quote(exc.detail)}"
    return RedirectResponse(url=error_page, status_code=302)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理请求验证异常
    """
    logger.error(f"验证异常: {exc.errors()}")

    # 检查是否是API请求或者是FastAPI内置路由
    is_api_request = request.url.path.startswith("/api/") or is_fastapi_builtin_route(request.url.path)

    if is_api_request:
        return JSONResponse(
            status_code=422,
            content={"message": "验证失败", "details": exc.errors(), "status_code": 422}
        )

    # 对于页面请求，重定向到错误页面
    error_page = "/error?status=422&message=" + urllib.parse.quote("请求参数验证失败")
    return RedirectResponse(url=error_page, status_code=302)


async def all_exception_handler(request: Request, exc: Exception):
    """
    处理所有其他未捕获的异常，包括路由找不到的情况
    """
    logger.error(f"未处理的异常: {type(exc).__name__}: {str(exc)}")

    # 检查是否是API请求或者是FastAPI内置路由
    is_api_request = request.url.path.startswith("/api/") or is_fastapi_builtin_route(request.url.path)

    # 处理路由找不到的情况
    if isinstance(exc, NoMatchFound) or "No route found for" in str(exc):
        status_code = HTTP_404_NOT_FOUND
        message = "请求的资源不存在"
    else:
        status_code = HTTP_500_INTERNAL_SERVER_ERROR
        message = "服务器内部错误"

    if is_api_request:
        return JSONResponse(
            status_code=status_code,
            content={"message": message, "status_code": status_code}
        )

    # 对于页面请求，重定向到错误页面
    error_page = f"/error?status={status_code}&message=" + urllib.parse.quote(message)
    return RedirectResponse(url=error_page, status_code=302)


async def permission_denied_handler(request: Request, exc: PermissionDenied):
    """
    处理权限不足异常
    """
    logger.error(f"权限不足: {str(exc)}")

    # 检查是否是API请求或者是FastAPI内置路由
    is_api_request = request.url.path.startswith("/api/") or is_fastapi_builtin_route(request.url.path)

    if is_api_request:
        return JSONResponse(
            status_code=HTTP_403_FORBIDDEN,
            content={"message": exc.message, "status_code": 403}
        )

    # 对于页面请求，重定向到错误页面
    error_page = f"/error?status=403&message=" + urllib.parse.quote(exc.message)
    return RedirectResponse(url=error_page, status_code=302)


def is_fastapi_builtin_route(path: str) -> bool:
    """
    检查是否是FastAPI内置路由
    """
    builtin_routes = [
        "/docs", "/redoc", "/openapi.json",
        "/docs/oauth2-redirect", "/api/docs", "/api/redoc"
    ]

    # 检查完全匹配
    if path in builtin_routes:
        return True

    # 检查前缀匹配
    for route in builtin_routes:
        if path.startswith(route + "/"):
            return True

    return False
