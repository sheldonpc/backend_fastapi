from datetime import datetime, timedelta

from fastapi import APIRouter
from fastapi import Request
# from starlette.staticfiles import StaticFiles
from app.models import GlobalIndexLatest, ForeignCommodityRealTimeData2, RealTimeForeignCurrencyData, News2
from app.core.templates import templates
from app.services.scheduler import market_scheduler
# from app.main import app

# app.mount("/static", StaticFiles(directory="app/static"), name="static")

router = APIRouter(prefix="")

@router.get("/")
async def index(request: Request):
    results = await GlobalIndexLatest.filter(code__in=["000001", "399001", "399006", "HSI"]).all()
    index_data = {}
    for item in results:
        index_data[item.code] = {"name": item.name, "price": item.price, "change_percent": item.change_percent,
                                 "change": item.change, "timestamp": item.timestamp}

    update_time = index_data["000001"]["timestamp"].strftime("%Y-%m-%d %H:%M:%S")

    results2 = await GlobalIndexLatest.filter(code__in=["DJIA", "SPX", "NDX"]).all()
    index_data2 = {}
    for item in results2:
        index_data2[item.code] = {"name": item.name, "price": item.price, "change_percent": item.change_percent, "change": item.change, "timestamp": item.timestamp}

    # USD / CNY
    # 黄金 白银 原油
    results_metal = await ForeignCommodityRealTimeData2.filter(symbol__in=["OIL", "XAU", "LHC", "XAG"])
    commodity_data = {}
    for item in results_metal:
        commodity_data[item.symbol] = {
            "name": item.name,
            "symbol": item.symbol,
            "price": item.rmb_price,
            "change_percent": item.change_percent,
            "change": item.change_amount
        }

    # USD/CNY
    results_fx = await RealTimeForeignCurrencyData.filter(code="USD/CNY").first()
    fx_data = {
        "code": results_fx.code,
        "buying_price": results_fx.buying_price,
        "selling_price": results_fx.selling_price,
    } if results_fx else None

    yesterday = datetime.now() - timedelta(days=1)
    results_news = await News2.all().order_by("-publish_time").limit(10)
    news_data = []
    for news in results_news:
        news_data.append({
            "title": news.title,
            "content": news.content,
            "publish_time": news.publish_time.strftime("%H:%M:%S")
        })

    response_data = {
        "main_market": index_data,
        "foreign_market": index_data2,
        "commodity": commodity_data,
        "fx": fx_data,
        "update_time": update_time,
        "news_data": news_data
    }

    return templates.TemplateResponse("public/index.html", {
        "request": request,
        "data": response_data,
    })

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})

@router.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}