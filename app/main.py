import time

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.models import GlobalIndexLatest, ForeignCommodityRealTimeData2, RealTimeForeignCurrencyData
from app.routers.root import _build_homepage_data
from app.services.scheduler_market_data import NewMarketScheduler
from app.utils.logger import init_logger, logger
from app.database import init_db, close_db
from app.routers import users, auth, articles, comments, likes, admin, api_users, roles, api_articles, api_config, \
    financial, market, api_fetch_data, api_index, root, board
from app.middlewares.error_handler import http_exception_handler, validation_exception_handler, all_exception_handler
from app.utils.redis_client import cache_set
from app.utils.warm_up_tasks import start_cache_warmup, stop_cache_warmup

# 缓存配置
HOMEPAGE_CACHE_KEY = "homepage_data"
HOMEPAGE_CACHE_TTL = 60  # 5分钟


@asynccontextmanager
async def lifespan(app: FastAPI):
    market_scheduler = NewMarketScheduler()
    init_logger()
    await init_db()

    try:
        await market_scheduler.start_scheduler()
        logger.info("启动市场数据调度器")
    except Exception as e:
        logger.error(f"启动市场数据调度器出错: {e}")

    await start_cache_warmup()

    yield

    try:
        await market_scheduler.stop_scheduler()
        logger.info("停止市场数据调度器")
    except Exception as e:
        logger.error(f"停止市场数据调度器出错: {e}")

    await stop_cache_warmup()

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
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(root.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(articles.router)
app.include_router(comments.router)
app.include_router(likes.router)
app.include_router(admin.router)
app.include_router(api_users.router)
app.include_router(roles.router)
app.include_router(api_articles.router)
# app.include_router(financial.router)
app.include_router(market.router)
app.include_router(api_config.router)
app.include_router(api_fetch_data.router)
app.include_router(api_index.router)
app.include_router(board.router)
# deprecated
# @app.on_event("startup")
# async def startup():
#     await init_db()

# templates = Jinja2Templates(directory="app/templates")

