import time

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.utils.logger import init_logger, logger
from app.database import init_db, close_db
from app.routers import users, auth, articles, comments, likes, admin, api_users, roles, api_articles, api_config, \
    financial
from app.middlewares.error_handler import http_exception_handler, validation_exception_handler, all_exception_handler
from app.core.templates import templates

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_logger()
    await init_db()

    # try:
    #     from app.services.scheduler import market_scheduler
    #     await market_scheduler.start_scheduler()
    #     logger.info("启动市场数据调度器")
    # except Exception as e:
    #     logger.error(f"启动市场数据调度器出错: {e}")

    yield

    # try:
    #     from app.services.scheduler import market_scheduler
    #     await market_scheduler.stop_scheduler()
    #     logger.info("停止市场数据调度器")
    # except Exception as e:
    #     logger.error(f"停止市场数据调度器出错: {e}")

    await close_db()
app = FastAPI(
    lifespan=lifespan,
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
    openapi_tags=[
        {"name": "auth", "description": "用户认证相关接口"},
        {"name": "users", "description": "用户管理接口"}
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
    except Exception as e:
        # 捕获异常，交给统一异常处理器
        raise e
    process_time = time.time() - start
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(
        f"{request.method} {request.url} completed in {round(process_time, 4)}s"
    )
    return response

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, all_exception_handler)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(articles.router)
app.include_router(comments.router)
app.include_router(likes.router)
app.include_router(admin.router)
app.include_router(api_users.router)
app.include_router(roles.router)
app.include_router(api_articles.router)
app.include_router(financial.router)

app.include_router(api_config.router)
# deprecated
# @app.on_event("startup")
# async def startup():
#     await init_db()

# templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def root():
    return {"msg": "Hello FastAPI + Tortoise + MySQL"}

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
