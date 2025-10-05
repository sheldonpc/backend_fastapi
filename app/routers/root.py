import re
from datetime import datetime, timedelta
from math import ceil

from flask import url_for, request
from tortoise.expressions import Q
from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi import Request

from app.deps import optional_auth_cookie
from app.models import GlobalIndexLatest, ForeignCommodityRealTimeData2, RealTimeForeignCurrencyData, News2, \
    StockMarketActivity, CNMarket, VIXRealTimeData, News4, News3, DifyTemplate, BondYieldHistory, EventData, Article2, \
    Strategy
from app.core.templates import templates
import markdown

from app.utils.markdown_process import process_markdown
from app.utils.redis_client import cache_get, cache_set
from app.utils.status_decorator import template_route

CACHE_KEY = "homepage_data"
CACHE_TTL = 30  # 秒
router = APIRouter(prefix="", tags=["index"])


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
            "price": item.current_price,
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
async def index(
        request: Request,
        current_user=Depends(optional_auth_cookie),
):
    # 尝试从缓存读取
    cached = await cache_get(CACHE_KEY)
    if cached is not None:
        return templates.TemplateResponse("public/index.html", {
            "request": request,
            "data": cached,
            "current_user": current_user,
        })

    # 缓存未命中，构建数据
    response_data = await _build_homepage_data()

    # 写入缓存
    await cache_set(CACHE_KEY, response_data, ttl=CACHE_TTL)

    return templates.TemplateResponse("public/index.html", {
        "request": request,
        "data": response_data,
        "current_user": current_user,
    })


# 辅助函数：生成页码范围
def generate_page_range(current_page, total_pages, left_edge=2, left_current=2, right_current=3, right_edge=2):
    """简化版的页码范围生成器"""
    if total_pages <= 10:
        # 如果总页数少，显示所有页码
        return list(range(1, total_pages + 1))

    pages = []

    # 总是显示第1页
    # pages.append(1)
    if current_page == 1 or current_page == 2:
        pages.append(1)

    # 左省略号
    if current_page - left_current > 2:
        pages.append(None)

    # 当前页附近的页码
    start_page = max(2, current_page - left_current)
    end_page = min(total_pages - 1, current_page + right_current)

    for page in range(start_page, end_page + 1):
        pages.append(page)

    # 右省略号
    if end_page < total_pages - 1:
        pages.append(None)

    # 总是显示最后一页
    # if total_pages > 1:
    #     pages.append(total_pages)
    if current_page == total_pages or current_page == total_pages - 1:
        pages.append(total_pages)

    return pages


@router.get("/news")
async def news(
        request: Request,
        page: int = Query(1, ge=1),
        per_page: int = Query(15, ge=10, le=50, description="每页数量"),
        current_user=Depends(optional_auth_cookie),
):
    offset = (page - 1) * per_page
    total_news = await News2.all().count()
    results_news2 = await News2.all().order_by("-publish_time").offset(offset).limit(per_page)
    news_data = [{"title": news.title, "content": news.content, "publish_time": news.publish_time} for news in
                 results_news2]

    total_pages = ceil(total_news / per_page) if total_news > 0 else 1
    pagination_info = {
        "page": page,
        "per_page": per_page,  # 注意这里是 per_page，不是 size
        "total": total_news,
        "total_pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_num": page - 1 if page > 1 else None,
        "next_num": page + 1 if page < total_pages else None,
        "iter_pages": lambda left_edge=2, left_current=2, right_current=3, right_edge=2:
        generate_page_range(page, total_pages, left_edge, left_current, right_current, right_edge)
    }

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
         "pagination": pagination_info,
         "current_user": current_user
         }
    )


async def get_latest_bond_data():
    """
    获取最新的中国和美国国债数据
    如果最新日期的数据不完整，则继续查找后续日期的数据
    """
    try:
        # 先查找有完整中国国债数据的最新记录
        cn_bond = await BondYieldHistory.filter(
            cn_2y__isnull=False,
            cn_5y__isnull=False,
            cn_10y__isnull=False,
            cn_30y__isnull=False,
            cn_spread_10y_2y__isnull=False,
        ).order_by("-date").first()

        # 查找有完整美国国债数据的最新记录
        us_bond = await BondYieldHistory.filter(
            us_2y__isnull=False,
            us_5y__isnull=False,
            us_10y__isnull=False,
            us_30y__isnull=False,
            us_spread_10y_2y__isnull=False,
        ).order_by("-date").first()
        return cn_bond, us_bond

    except Exception as e:
        return None, None


@router.get("/overview")
async def overview(
        request: Request,
        current_user=Depends(optional_auth_cookie),
):
    all_indexes = await GlobalIndexLatest.all()

    # 定义地区的显示顺序
    region_order = ["中国", "北美", "亚洲其他", "欧洲", "大洋洲", "南美", "其他"]

    # 定义各地区内部的排序顺序
    region_internal_order = {
        "中国": ["000001", "399001", "399005", "399006", "000300", "HSCEI", "HSI", "HSCCI", "TWII"],
        "北美": ["DJIA", "SPX", "NDX", "TSX", "MXX"]
    }

    # 按地区分组
    grouped_indexes = {}
    for region in region_order:
        grouped_indexes[region] = []

    for index in all_indexes:
        region = index.region if index.region in region_order else "其他"
        grouped_indexes[region].append({
            "code": index.code,
            "name": index.name,
            "price": float(index.price),
            "change": float(index.change),
            "change_percent": float(index.change_percent),
            "timestamp": index.timestamp.strftime("%Y-%m-%d %H:%M")
        })

    # 对每个地区进行内部排序（如果定义了排序规则）
    for region, indexes in grouped_indexes.items():
        if region in region_internal_order and indexes:
            order_list = region_internal_order[region]
            # 创建代码到数据的映射
            index_dict = {item["code"]: item for item in indexes}

            # 按照指定顺序重新排列
            sorted_indexes = []
            for code in order_list:
                if code in index_dict:
                    sorted_indexes.append(index_dict[code])

            # 添加其他未在指定顺序中的指数
            for code, index_data in index_dict.items():
                if code not in order_list:
                    sorted_indexes.append(index_data)

            grouped_indexes[region] = sorted_indexes

    # 确保返回的数据按照 region_order 的顺序
    ordered_result = {}
    for region in region_order:
        ordered_result[region] = grouped_indexes.get(region, [])

    cn_bond, us_bond = await get_latest_bond_data()

    commodities = await ForeignCommodityRealTimeData2.all().only(
        'symbol', 'name', 'rmb_price', 'change_amount', 'change_percent'
    ).order_by('symbol')

    return templates.TemplateResponse("public/overview.html",
                                      {"request": request, "ordered_result": ordered_result, "cn_bond": cn_bond,
                                       "us_bond": us_bond, "commodities": commodities, "current_user": current_user})


@router.get("/board")
async def board(request: Request, current_user=Depends(optional_auth_cookie), ):
    return templates.TemplateResponse("public/board.html", {"request": request, "current_user": current_user})


@router.get("/calendar")
async def calendar_page(
        request: Request,
        date: str = Query(None, description="查询日期，格式: YYYY-MM-DD"),
        region: str = Query(None, description="地区筛选"),
        importance: str = Query(None, description="重要性筛选"),
        search: str = Query(None, description="搜索关键词"),
        current_user=Depends(optional_auth_cookie),
):
    """财经日历页面"""
    # 默认显示今天的数据
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    # 构建查询条件 - 使用 Q 对象进行复杂查询
    query = Q()

    # 日期范围查询 (当天的00:00:00到23:59:59)
    start_date = datetime.strptime(date, "%Y-%m-%d")
    end_date = start_date + timedelta(days=8) - timedelta(seconds=1)

    query &= Q(datetime__gte=start_date) & Q(datetime__lte=end_date)

    # 地区筛选 - 使用包含关系
    if region:
        query &= Q(region__contains=region)

    # 重要性筛选 - 完全匹配
    if importance:
        query &= Q(importance=importance)

    # 查询事件数据
    events = await EventData.filter(query).order_by("datetime")

    # 如果有搜索关键词，进行筛选（名称包含关键词）
    if search:
        events = [event for event in events if search.lower() in event.name.lower()]

    # 获取最新数据更新时间
    latest_event = await EventData.all().order_by("-scraped_at").first()
    last_updated = latest_event.scraped_at if latest_event else None

    return templates.TemplateResponse("public/eco_calendar.html", {
        "request": request,
        "events": events,
        "current_date": date,
        "selected_region": region,
        "selected_importance": importance,
        "search_keyword": search or "",
        "last_updated": last_updated,
        "current_user": current_user,
    })


@router.get("/api/calendar/events")
async def get_calendar_events_api(
        date: str = Query(..., description="查询日期，格式: YYYY-MM-DD"),
        region: str = Query(None, description="地区筛选"),
        importance: str = Query(None, description="重要性筛选"),
        search: str = Query(None, description="搜索关键词"),
        current_user=Depends(optional_auth_cookie),
):
    """财经日历API接口，供AJAX调用"""
    # 构建查询条件 - 使用 Q 对象
    query = Q()

    # 日期范围查询
    start_date = datetime.strptime(date, "%Y-%m-%d")
    end_date = start_date + timedelta(days=8) - timedelta(seconds=1)

    query &= Q(datetime__gte=start_date) & Q(datetime__lte=end_date)

    # 地区筛选 - 包含关系
    if region:
        query &= Q(region__contains=region)

    # 重要性筛选 - 完全匹配
    if importance:
        query &= Q(importance=importance)

    # 查询事件数据
    events = await EventData.filter(query).order_by("datetime")

    # 搜索筛选 - 名称包含关键词
    if search:
        events = [event for event in events if search.lower() in event.name.lower()]

    # 序列化事件数据
    events_data = []
    for event in events:
        events_data.append({
            "id": event.id,
            "region": event.region,
            "name": event.name,
            "previous_value": event.previous_value,
            "importance": event.importance,
            "datetime": event.datetime.isoformat(),
            "scraped_at": event.scraped_at.isoformat() if event.scraped_at else None,
        })

    return events_data


@router.get("/article")
async def home_page(request: Request, current_user=Depends(optional_auth_cookie)):
    """首页"""
    # 模拟热门推荐文章（顶部2-3篇）
    featured_articles = [
        {
            "id": 1,
            "title": "2024年全球股市展望：人工智能浪潮下的投资机遇",
            "author": "张明分析师",
            "publish_time": "2024-01-15",
            "feature_image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"
        },
        {
            "id": 2,
            "title": "半导体行业深度报告：AI芯片需求爆发下的投资机会",
            "author": "李强研究员",
            "publish_time": "2024-01-10",
            "feature_image": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"
        },
        {
            "id": 3,
            "title": "2024年美联储政策展望及对科技股影响",
            "author": "王伟顾问",
            "publish_time": "2024-01-08",
            "feature_image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"
        }
    ]

    # 模拟相关推荐
    recommended_articles = [
        {
            "id": 6,
            "title": "中国制造业转型升级的投资逻辑",
            "publish_time": "2024-01-02"
        },
        {
            "id": 7,
            "title": "新能源车行业2024年投资策略",
            "publish_time": "2023-12-28"
        },
        {
            "id": 8,
            "title": "云计算基础设施投资机会分析",
            "publish_time": "2023-12-25"
        }
    ]

    # 模拟热门文章
    hot_articles = [
        {
            "id": 5,
            "title": "巴菲特最新持仓分析：为何重仓科技股？",
            "views": 3562
        },
        {
            "id": 1,
            "title": "2024年全球股市展望：人工智能浪潮下的投资机遇",
            "views": 2847
        },
        {
            "id": 6,
            "title": "中国制造业转型升级的投资逻辑",
            "views": 2987
        }
    ]

    # 模拟最新评论
    recent_comments = [
        {
            "user": "投资新手",
            "content": "这篇文章分析得很透彻，特别是对半导体行业的展望很有启发！",
            "time": "2小时前"
        },
        {
            "user": "老股民",
            "content": "AI确实是未来方向，但估值是否过高需要谨慎判断",
            "time": "5小时前"
        },
        {
            "user": "机构分析师",
            "content": "数据翔实，逻辑清晰，对投资决策有重要参考价值",
            "time": "1天前"
        }
    ]

    # 模拟热门标签
    popular_tags = [
        {"name": "人工智能", "count": 156},
        {"name": "投资策略", "count": 142},
        {"name": "科技股", "count": 128},
        {"name": "半导体", "count": 115},
        {"name": "宏观经济", "count": 98},
        {"name": "美联储", "count": 87}
    ]

    # 模拟分页数据
    pagination = {
        "page": 1,
        "per_page": 10,
        "total": 45,
        "pages": 5,
        "has_prev": False,
        "has_next": True,
        "prev_num": None,
        "next_num": 2,
        "iter_pages": lambda: [1, 2, 3, 4, 5]
    }

    articles = []
    pen_name = ""
    response = await Article2.all().order_by("-published_at").limit(10).prefetch_related("tags", "author")
    for article in response:
        if article.author:
            author = article.author.username
            pen_name = article.author.pen_name
            print(author)
        else:
            author = "未知作者"
        articles.append({
            "id": article.id,
            "title": article.title,
            "excerpt": article.summary,
            "author": author,
            "pen_name": pen_name,
            "publish_time": article.published_at.strftime("%Y-%m-%d %H:%M:%S"),
            "views": article.views,
            "tags": [tag.name for tag in article.tags],
            "feature_image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80",
        })

    return templates.TemplateResponse("public/article.html", {
        "request": request,
        "article": None,  # 首页没有具体文章
        "featured_articles": featured_articles,
        "articles": articles,
        "recommended_articles": recommended_articles,
        "hot_articles": hot_articles,
        "recent_comments": recent_comments,
        "popular_tags": popular_tags,
        "pagination": pagination,
        "current_user": current_user
    })


def process_image_urls(html_content):
    """处理图片URL，将相对路径转换为绝对路径"""
    from urllib.parse import urljoin

    def replace_image_url(match):
        alt_text = match.group(1)
        img_url = match.group(2)

        # 如果是相对路径，转换为绝对路径
        if img_url.startswith('/'):
            img_url = urljoin(request.host_url, img_url)
        elif not img_url.startswith(('http://', 'https://')):
            # 假设图片存储在 /static/uploads/ 目录
            img_url = url_for('static', filename=f'uploads/{img_url}')

        return f'<img src="{img_url}" alt="{alt_text}">'

    # 使用正则表达式替换img标签
    pattern = r'<img src="([^"]*)" alt="([^"]*)">'
    return re.sub(pattern, replace_image_url, html_content)


@router.get("/article/{article_id}")
async def article_detail_page(request: Request, article_id: int, current_user=Depends(optional_auth_cookie), ):
    """文章详情页"""
    # 模拟根据article_id获取文章数据
    article = await Article2.filter(id=article_id).first().prefetch_related("tags", "author")

    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    if article.content_type == "markdown":
        # article.content = markdown.markdown(
        #     article.content,
        #     extensions=['extra', 'codehilite', 'toc']
        # )
        article.content = process_markdown(article.content)
        article.content = process_image_urls(article.content)

    # 模拟相关推荐文章
    recommended_articles = [
        {
            "id": 2,
            "title": "半导体行业深度报告：AI芯片需求爆发下的投资机会",
            "publish_time": "2024-01-10"
        },
        {
            "id": 3,
            "title": "2024年美联储政策展望及对科技股影响",
            "publish_time": "2024-01-08"
        },
        {
            "id": 4,
            "title": "生成式AI商业化路径分析：从技术到营收",
            "publish_time": "2024-01-05"
        }
    ]

    # 模拟热门文章
    hot_articles = [
        {
            "id": 5,
            "title": "巴菲特最新持仓分析：为何重仓科技股？",
            "views": 3562
        },
        {
            "id": 6,
            "title": "中国制造业转型升级的投资逻辑",
            "views": 2987
        },
        {
            "id": 7,
            "title": "新能源车行业2024年投资策略",
            "views": 2743
        }
    ]

    # 模拟最新评论（侧边栏用）
    recent_comments = [
        {
            "user": "投资新手",
            "content": "这篇文章分析得很透彻，特别是对半导体行业的展望很有启发！",
            "time": "2小时前"
        },
        {
            "user": "老股民",
            "content": "AI确实是未来方向，但估值是否过高需要谨慎判断",
            "time": "5小时前"
        },
        {
            "user": "机构分析师",
            "content": "数据翔实，逻辑清晰，对投资决策有重要参考价值",
            "time": "1天前"
        }
    ]

    # 模拟评论数据（评论区用）
    comments = [
        {
            "user": "价值投资者",
            "time": "2024-01-16 14:30",
            "content": "从长期来看，AI确实会改变很多行业，但短期要注意估值风险。作者的分析比较客观，既看到了机遇也提示了风险。",
            "likes": 24
        },
        {
            "user": "科技爱好者",
            "time": "2024-01-16 12:15",
            "content": "表格数据很有参考价值，特别是对各板块的预期分析。希望后续能看到更详细的个股推荐。",
            "likes": 18
        },
        {
            "user": "量化交易员",
            "time": "2024-01-16 09:45",
            "content": "AI在量化投资中的应用也是重要方向，期待作者后续能专门写一篇相关文章。",
            "likes": 15
        },
        {
            "user": "行业研究员",
            "time": "2024-01-15 16:20",
            "content": "对AI产业链的分析很到位，特别是上游算力需求的判断很有前瞻性。",
            "likes": 12
        },
        {
            "user": "个人投资者",
            "time": "2024-01-15 11:10",
            "content": "文章提到的核心-卫星策略很实用，已经在实际投资中应用了，效果不错。",
            "likes": 8
        }
    ]

    # 模拟上一篇下一篇
    prev_next_data = {
        1: {
            "prev": {
                "id": 3,
                "title": "2024年美联储政策展望及对科技股影响"
            },
            "next": {
                "id": 2,
                "title": "半导体行业深度报告：AI芯片需求爆发下的投资机会"
            }
        },
        2: {
            "prev": {
                "id": 1,
                "title": "2024年全球股市展望：人工智能浪潮下的投资机遇"
            },
            "next": {
                "id": 3,
                "title": "2024年美联储政策展望及对科技股影响"
            }
        },
        3: {
            "prev": {
                "id": 2,
                "title": "半导体行业深度报告：AI芯片需求爆发下的投资机会"
            },
            "next": {
                "id": 1,
                "title": "2024年全球股市展望：人工智能浪潮下的投资机遇"
            }
        }
    }

    popular_tags = [
        {"name": "人工智能", "count": 156},
        {"name": "投资策略", "count": 142},
        {"name": "科技股", "count": 128},
        {"name": "半导体", "count": 115},
        {"name": "宏观经济", "count": 98},
        {"name": "美联储", "count": 87}
    ]

    prev_next = prev_next_data.get(article_id, {"prev": None, "next": None})

    return templates.TemplateResponse("public/article_detail.html", {
        "request": request,
        "article": article,
        "recommended_articles": recommended_articles,
        "hot_articles": hot_articles,
        "recent_comments": recent_comments,
        "comments": comments,
        "comment_count": len(comments),
        "prev_article": prev_next["prev"],
        "next_article": prev_next["next"],
        "popular_tags": popular_tags,
        "current_user": current_user
    })


@router.get("/strategy")
async def strategy(request: Request):
    """
    策略页面
    """
    return templates.TemplateResponse(
        "public/strategy.html", {
            "request": request
        })


@router.get("/strategy_data")
async def strategy_data(request: Request):
    """
    策略数据
    """
    results = await Strategy.all()
    return {"message": "策略数据获取成功", "data": results}
