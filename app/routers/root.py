from fastapi import APIRouter
from fastapi import Request
# from starlette.staticfiles import StaticFiles
from app.models import GlobalIndexLatest, ForeignCommodityRealTimeData2, RealTimeForeignCurrencyData
from app.core.templates import templates
from app.services.scheduler import market_scheduler
# from app.main import app

# app.mount("/static", StaticFiles(directory="app/static"), name="static")

router = APIRouter(prefix="")

@router.get("/")
async def index(request: Request):
    results = await GlobalIndexLatest.filter(code__in=["000001", "399001", "399006", "HSI", "DJIA", "SPX", "NDX"]).all()
    index_data = {}
    for item in results:
        index_data[item.code] = {"name": item.name, "price": item.price, "change_percent": item.change_percent,
                                 "change": item.change}

    # USD / CNY
    # 黄金 白银 原油
    results_metal = await ForeignCommodityRealTimeData2.filter(symbol__in=["OIL", "XAU", "LHC", "XPT"])
    commodity_data = {}
    for item in results_metal:
        commodity_data[item.symbol] = {
            "name": item.name,
            "symbol": item.symbol,
            "price": item.current_price,
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

    response_data = {
        "sh000001": index_data.get("000001"),
        "sz399001": index_data.get("399001"),
        "sz399006": index_data.get("399006"),
        "hsi": index_data.get("HSI"),
        "djia": index_data.get("DJIA"),
        "spx": index_data.get("SPX"),
        "ndx": index_data.get("NDX"),
        "oil": commodity_data.get("OIL"),
        "xau": commodity_data.get("XAU"),
        "lhc": commodity_data.get("LHC"),
        "xpt": commodity_data.get("XPT"),
        "fx_uc": fx_data
    }

    return templates.TemplateResponse("public/index.html", {
        "request": request,
        "date": response_data
    })

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})

@router.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}