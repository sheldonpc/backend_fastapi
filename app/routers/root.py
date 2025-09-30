from datetime import datetime, timedelta
from fastapi import APIRouter
from fastapi import Request
from app.models import GlobalIndexLatest, ForeignCommodityRealTimeData2, RealTimeForeignCurrencyData, News2, \
    StockMarketActivity, CNMarket, VIXRealTimeData, News4, News3, DifyTemplate
from app.core.templates import templates
import markdown
from app.utils.redis_client import cache_get, cache_set

CACHE_KEY = "homepage_data"
CACHE_TTL = 30  # 秒
router = APIRouter(prefix="")


async def _build_homepage_data():
    from datetime import datetime, timedelta

    results = await GlobalIndexLatest.filter(code__in=["000001", "399001", "399006", "HSI"]).all()
    index_data = {}
    for item in results:
        index_data[item.code] = {
            "name": item.name,
            "price": item.price,
            "change_percent": item.change_percent,
            "change": item.change,
            "timestamp": item.timestamp,
        }

    update_time = index_data["000001"]["timestamp"].strftime("%Y-%m-%d %H:%M:%S")

    results2 = await GlobalIndexLatest.filter(code__in=["DJIA", "SPX", "NDX"]).all()
    index_data2 = {}
    for item in results2:
        index_data2[item.code] = {
            "name": item.name,
            "price": item.price,
            "change_percent": item.change_percent,
            "change": item.change,
            "timestamp": item.timestamp,
        }

    results_metal = await ForeignCommodityRealTimeData2.filter(symbol__in=["OIL", "XAU", "LHC", "XAG"]).all()
    commodity_data = {}
    for item in results_metal:
        commodity_data[item.symbol] = {
            "name": item.name,
            "symbol": item.symbol,
            "price": item.rmb_price,
            "change_percent": item.change_percent,
            "change": item.change_amount,
        }

    results_fx = await RealTimeForeignCurrencyData.filter(code="USD/CNY").first()
    fx_data = {
        "code": results_fx.code,
        "buying_price": results_fx.buying_price,
        "selling_price": results_fx.selling_price,
    } if results_fx else None

    results_news = await News2.all().order_by("-publish_time").limit(10)
    news_data = []
    for news in results_news:
        news_data.append({
            "title": news.title,
            "content": news.content,
            "publish_time": news.publish_time.strftime("%H:%M:%S"),
        })

    latest_market_activity = await StockMarketActivity.all().order_by("-update_time").first()
    market_data = {
        'rise': int(latest_market_activity.rise),
        'fall': int(latest_market_activity.fall),
        'limit_up': int(latest_market_activity.limit_up),
        'limit_down': int(latest_market_activity.limit_down),
        'stop': int(latest_market_activity.stop),
        'activity': latest_market_activity.activity,
    }
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    market_notice = (
        f"{current_time} 最新市场动态：\n"
        f"市场活跃度：{market_data['activity']}%。\n"
        f"上涨：{market_data['rise']}家，下跌：{market_data['fall']}家{' ' * 10}。\n"
        f"涨停：{market_data['limit_up']}家，跌停：{market_data['limit_down']}家。\n"
        f"停牌：{market_data['stop']}家。"
    )

    results_ai_insight = await CNMarket.all().order_by("-id").limit(3).prefetch_related("key_points")
    ai_insight_data = []
    general_confidance = 0
    for item in results_ai_insight:
        general_confidance += item.confidence
        ai_insight_data.append({
            "market_region": item.market_region,
            "data_type": item.data_type,
            "confidence": item.confidence,
            "sentiment": item.sentiment,
            "sentiment_level": item.sentiment_level,
            "focus_sectors": item.focus_sectors,
            "support_level": item.support_level,
            "resistance_level": item.resistance_level,
            "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "key_points": [{"type": point.type, "content": point.text} for point in item.key_points],
        })
    average_confidence = general_confidance / len(results_ai_insight)

    ai_time = datetime.strptime(ai_insight_data[0]["created_at"], "%Y-%m-%d %H:%M:%S")
    ai_update_time = ai_time + timedelta(hours=8)

    vix_result = await VIXRealTimeData.all().order_by("-update_time").first()
    vix_data = vix_result.current_price if vix_result else None

    return {
        "main_market": index_data,
        "foreign_market": index_data2,
        "commodity": commodity_data,
        "fx": fx_data,
        "update_time": update_time,
        "news_data": news_data,
        "notice": market_notice,
        "ai_insight": ai_insight_data,
        "average_confidence": average_confidence,
        "market_data_activity": latest_market_activity.activity,
        "vix": vix_data,
        "ai_update_time": ai_update_time.strftime("%Y-%m-%d %H:%M:%S"),
    }


@router.get("/")
async def index(request: Request):
    # 尝试从缓存读取
    cached = await cache_get(CACHE_KEY)
    if cached is not None:
        return templates.TemplateResponse("public/index.html", {
            "request": request,
            "data": cached,
        })

    # 缓存未命中，构建数据
    response_data = await _build_homepage_data()

    # 写入缓存
    await cache_set(CACHE_KEY, response_data, ttl=CACHE_TTL)

    return templates.TemplateResponse("public/index.html", {
        "request": request,
        "data": response_data,
    })


# @router.get("/")
# async def index(request: Request):
#     results = await GlobalIndexLatest.filter(code__in=["000001", "399001", "399006", "HSI"]).all()
#     index_data = {}
#     for item in results:
#         index_data[item.code] = {"name": item.name, "price": item.price, "change_percent": item.change_percent,
#                                  "change": item.change, "timestamp": item.timestamp}
#
#     update_time = index_data["000001"]["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
#
#     results2 = await GlobalIndexLatest.filter(code__in=["DJIA", "SPX", "NDX"]).all()
#     index_data2 = {}
#     for item in results2:
#         index_data2[item.code] = {"name": item.name, "price": item.price, "change_percent": item.change_percent,
#                                   "change": item.change, "timestamp": item.timestamp}
#
#     # USD / CNY
#     # 黄金 白银 原油
#     results_metal = await ForeignCommodityRealTimeData2.filter(symbol__in=["OIL", "XAU", "LHC", "XAG"])
#     commodity_data = {}
#     for item in results_metal:
#         commodity_data[item.symbol] = {
#             "name": item.name,
#             "symbol": item.symbol,
#             "price": item.rmb_price,
#             "change_percent": item.change_percent,
#             "change": item.change_amount
#         }
#
#     # USD/CNY
#     results_fx = await RealTimeForeignCurrencyData.filter(code="USD/CNY").first()
#     fx_data = {
#         "code": results_fx.code,
#         "buying_price": results_fx.buying_price,
#         "selling_price": results_fx.selling_price,
#     } if results_fx else None
#
#     results_news = await News2.all().order_by("-publish_time").limit(10)
#     news_data = []
#     for news in results_news:
#         news_data.append({
#             "title": news.title,
#             "content": news.content,
#             "publish_time": news.publish_time.strftime("%H:%M:%S")
#         })
#
#     latest_market_activity = await StockMarketActivity.all().order_by("-update_time").first()
#     market_data = {
#         'rise': int(latest_market_activity.rise),  # 上涨股票数量
#         'fall': int(latest_market_activity.fall),  # 下跌股票数量
#         'limit_up': int(latest_market_activity.limit_up),  # 涨停股票数量
#         'limit_down': int(latest_market_activity.limit_down),  # 跌停股票数量
#         'stop': int(latest_market_activity.stop),  # 停牌股票数量
#         'activity': latest_market_activity.activity  # 市场活跃度百分比
#     }
#     current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#
#     market_notice = (
#         f"{current_time} 最新市场动态：\n"
#         f"市场活跃度：{market_data['activity']}%。\n"
#         f"上涨：{market_data['rise']}家，下跌：{market_data['fall']}家{' ' * 10}。\n"
#         f"涨停：{market_data['limit_up']}家，跌停：{market_data['limit_down']}家。\n"
#         f"停牌：{market_data['stop']}家。"
#     )
#
#     results_ai_insight = await CNMarket.all().order_by("-id").limit(3).prefetch_related("key_points")
#     ai_insight_data = []
#     general_confidance = 0
#     for item in results_ai_insight:
#         general_confidance += item.confidence
#         ai_insight_data.append({
#             "market_region": item.market_region,
#             "data_type": item.data_type,
#             "confidence": item.confidence,
#             "sentiment": item.sentiment,
#             "sentiment_level": item.sentiment_level,
#             "focus_sectors": item.focus_sectors,
#             "support_level": item.support_level,
#             "resistance_level": item.resistance_level,
#             "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
#             "key_points": [{"type": point.type, "content": point.text} for point in item.key_points]
#         })
#     average_confidence = general_confidance / len(results_ai_insight)
#
#     ai_time = datetime.strptime(ai_insight_data[0]["created_at"], "%Y-%m-%d %H:%M:%S")
#     ai_update_time = ai_time + timedelta(hours=8)
#
#     vix_result = await VIXRealTimeData.all().order_by("-update_time").first()
#     vix_data = vix_result.current_price
#
#     response_data = {
#         "main_market": index_data,
#         "foreign_market": index_data2,
#         "commodity": commodity_data,
#         "fx": fx_data,
#         "update_time": update_time,
#         "news_data": news_data,
#         "notice": market_notice,
#         "ai_insight": ai_insight_data,
#         "average_confidence": average_confidence,
#         "market_data_activity": latest_market_activity.activity,
#         "vix": vix_data,
#         "ai_update_time": ai_update_time.strftime("%Y-%m-%d %H:%M:%S"),
#     }
#
#     return templates.TemplateResponse("public/index.html", {
#         "request": request,
#         "data": response_data,
#     })

# class News2(models.Model):
#     """新闻数据模型"""
#     id = fields.IntField(pk=True)
#     title = fields.CharField(max_length=200, description="新闻标题")
#     content = fields.TextField(description="新闻内容")
#     publish_time = fields.DatetimeField(description="发布时间")
#     source = fields.CharField(max_length=500, description="新闻来源", null=True)

@router.get("/news")
async def news(request: Request):
    results_news2 = await News2.all().order_by("-publish_time").limit(15)
    news_data = [{"title": news.title, "content": news.content, "publish_time": news.publish_time} for news in
                 results_news2]

    # global_news_list
    # class News3(models.Model):
    #     """新闻数据模型"""
    #     id = fields.IntField(pk=True)
    #     title = fields.CharField(max_length=200, description="新闻标题")
    #     content = fields.TextField(description="新闻内容")
    #     publish_time = fields.DatetimeField(description="发布时间")
    #     source = fields.CharField(max_length=500, description="新闻来源", null=True)

    results_news3 = await News3.all().order_by("-publish_time").limit(20)
    global_news_list = [{"publish_time": news.publish_time, "content": news.title} for news in results_news3]

    market_summary = await DifyTemplate().all().order_by("-created_at").first()

    if market_summary and market_summary.dify_answer:
        # 使用 python-markdown 库转换 Markdown 为 HTML
        market_summary.dify_answer_html = markdown.markdown(
            market_summary.dify_answer,
            extensions=['fenced_code', 'tables', 'nl2br']  # 添加常用扩展
        )
    else:
        # 创建默认对象或处理空值情况
        market_summary = type('Object', (), {})()  # 创建空对象
        market_summary.dify_answer_html = "今日市场数据正在分析中，请稍后查看..."

    return templates.TemplateResponse(
        "public/news.html",
        {"request": request,
         "news2_list": news_data,
         "global_news_list": global_news_list,
         "market_summary": market_summary,
         }
    )


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})


@router.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
