from fastapi.exceptions import RequestValidationError
from flask import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from app.utils.logger import logger

# 定义三个异常处理函数
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(
        f"HTTPException: {exc.detail} at {request.method}-{request.url}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail, "code": exc.status_code, "data": None},
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(
        f"ValidationError: {exc.errors()} at {request.method}-{request.url}"
    )
    return JSONResponse(
        status_code=422,
        content={"message": "Validation error", "code": 422, "data": exc.errors()},
    )

async def all_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(
        f"Unhandled exception at {request.method}-{request.url}"
    )
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "code": 500, "data": None},
    )