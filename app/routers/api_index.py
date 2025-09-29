from fastapi import APIRouter

from app.models import GlobalIndexLatest, ForeignCommodityRealTimeData2, RealTimeForeignCurrencyData, MarketIndexData, \
    MarketUpDownStats, VIXRealTimeData
from app.utils.ai_market import calculate_market_temperature

router = APIRouter(prefix="/index", tags=["index"])

@router.get("/main_market")
async def index():
    results = await GlobalIndexLatest.filter(code__in=["000001","399001", "399006", "HSI",  "DJIA", "SPX", "NDX"]).all()
    index_data = {}
    for item in results:
        index_data[item.code] = {"name": item.name, "price": item.price, "change_percent": item.change_percent, "change": item.change}

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

    return {"message": "首页", "data": response_data}

@router.get("/risedown")
async def risedown():
    results = await MarketUpDownStats.all().order_by("-update_time").limit(1)
    risedown_data = {}
    for item in results:
        risedown_data = {
            "up_num": item.up_num,
            "down_num": item.down_num,
            "flat_num": item.flat_num,
            "rise_num": item.rise_num,
            "fall_num": item.fall_num,
            "average_rise": item.average_rise,
            "up_2": item.up_2,
            "up_4": item.up_4,
            "up_6": item.up_6,
            "up_8": item.up_8,
            "up_10": item.up_10,
            "down_2": item.down_2,
            "down_4": item.down_4,
        }

    market_temperature = calculate_market_temperature(risedown_data)
    if market_temperature >= 80:
        market_heat_text = "过热"
    elif market_temperature >= 60:
        market_heat_text = "火热"
    elif market_temperature >= 40:
        market_heat_text = "温和"
    else:
        market_heat_text = "冷清"

    return {"message": "涨跌统计", "data": risedown_data, "market_temperature": market_temperature, "market_heat_text": market_heat_text}

@router.get("/vix")
async def vix():
    results = await VIXRealTimeData.all().order_by("-update_time").limit(1)
    vix_data = {}
    for item in results:
        vix_data = {
            "name": item.name,
            "current_price": item.current_price,
            "change_amount": item.change_amount,
            "change_percent": item.change_percent,
            "open_price": item.open_price,
            "high_price": item.high_price,
            "prev_close": item.prev_close,
            "low_price": item.low_price,
            "update_time": item.update_time.strftime("%H:%M:%S"),
            "api_date": item.api_date.strftime("%Y-%m-%d")
        }
    return {"message": "VIX恐慌指数", "data": vix_data}