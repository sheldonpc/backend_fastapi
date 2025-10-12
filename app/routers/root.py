import re
from datetime import datetime, timedelta
from math import ceil
from typing import Optional

from fastapi import Request
from urllib.parse import urljoin  # 如果还需要 urljoin
# from flask import url_for, request
from tortoise.expressions import Q
from fastapi import APIRouter, Query, HTTPException, Depends, Form, Request
from fastapi.responses import RedirectResponse, JSONResponse

from app.deps import optional_auth_cookie, require_auth_cookie
from app.models import GlobalIndexLatest, ForeignCommodityRealTimeData2, RealTimeForeignCurrencyData, News2, \
    StockMarketActivity, CNMarket, VIXRealTimeData, News4, News3, DifyTemplate, BondYieldHistory, EventData, Article2, \
    Strategy, Comment2, User
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

    # 生成分页页码列表，不包含最后一页
    def iter_pages():
        # 简单的分页逻辑，显示当前页前后各2页
        start = max(1, page - 2)
        end = min(total_pages - 1, page + 2)  # 修改这里，不包含最后一页

        # 如果开始页大于1，添加第一页和省略号
        if start > 1:
            yield 1
            if start > 2:
                yield None

        # 添加中间页码
        for p in range(start, end + 1):
            yield p

        # 如果结束页小于总页数-1，添加省略号
        if end < total_pages - 1:
            yield None

        # 不再添加最后一页

    # 创建分页对象
    pagination_info = {
        "page": page,
        "per_page": per_page,
        "total": total_news,
        "pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_num": page - 1 if page > 1 else None,
        "next_num": page + 1 if page < total_pages else None,
        "iter_pages": iter_pages
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
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(10, ge=1, le=100, description="每页数量"),
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

    # 计算分页
    total_count = len(events)
    total_pages = (total_count + page_size - 1) // page_size
    offset = (page - 1) * page_size
    paginated_events = events[offset:offset + page_size]

    # 计算显示范围
    start_item = (page - 1) * page_size + 1
    end_item = min(page * page_size, total_count)

    # 获取最新数据更新时间
    latest_event = await EventData.all().order_by("-scraped_at").first()
    last_updated = latest_event.scraped_at if latest_event else None

    return templates.TemplateResponse("public/eco_calendar.html", {
        "request": request,
        "events": paginated_events,
        "current_date": date,
        "selected_region": region,
        "selected_importance": importance,
        "search_keyword": search or "",
        "last_updated": last_updated,
        "current_user": current_user,
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "start_item": start_item,
        "end_item": end_item,
    })


@router.get("/api/calendar/events")
async def get_calendar_events_api(
        date: str = Query(..., description="查询日期，格式: YYYY-MM-DD"),
        region: str = Query(None, description="地区筛选"),
        importance: str = Query(None, description="重要性筛选"),
        search: str = Query(None, description="搜索关键词"),
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(10, ge=1, le=100, description="每页数量"),
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

    # 计算分页
    total_count = len(events)
    total_pages = (total_count + page_size - 1) // page_size
    offset = (page - 1) * page_size
    paginated_events = events[offset:offset + page_size]

    # 序列化事件数据
    events_data = []
    for event in paginated_events:
        events_data.append({
            "id": event.id,
            "region": event.region,
            "name": event.name,
            "previous_value": event.previous_value,
            "importance": event.importance,
            "datetime": event.datetime.isoformat(),
            "scraped_at": event.scraped_at.isoformat() if event.scraped_at else None,
        })

    # 返回包含分页信息的响应
    return {
        "events": events_data,
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages
    }


@router.get("/article")
async def home_page(request: Request, page: int = 1, per_page: int = 5, current_user=Depends(optional_auth_cookie)):
    """首页"""
    # 计算偏移量
    offset = (page - 1) * per_page

    # 获取精选文章
    featured_articles = []
    featured = await Article2.all().filter(is_featured=True).order_by("-published_at").limit(3).prefetch_related("tags",
                                                                                                                 "author")
    for article in featured:
        featured_articles.append({
            "id": article.id,
            "title": article.title,
            "author": article.author.username,
            "publish_time": article.published_at.strftime("%Y-%m-%d"),
            "feature_image": article.cover
        })

    # 获取推荐文章
    recommended_articles = []
    reco = await Article2.all().filter(is_top=True).order_by("-published_at").limit(5)
    for article in reco:
        recommended_articles.append({
            "id": article.id,
            "title": article.title,
            "publish_time": article.published_at.strftime("%Y-%m-%d"),
        })

    # 获取热门文章
    hot = await Article2.all().order_by("-views").limit(5)
    hot_articles = []
    for article in hot:
        hot_articles.append({
            "id": article.id,
            "title": article.title,
            "views": article.views
        })

    # 获取最新评论
    recent_comments = []
    comments = await Comment2.all().order_by("-created_at").limit(10).prefetch_related("author")
    for comment in comments:
        recent_comments.append({
            "user": comment.author.username,
            "content": comment.content,
            "time": comment.created_at.strftime("%Y-%m-%d %H:%M")
        })

    # 获取文章总数
    total_articles = await Article2.all().filter(status="published").count()

    # 计算分页信息
    total_pages = (total_articles + per_page - 1) // per_page  # 向上取整
    has_prev = page > 1
    has_next = page < total_pages
    prev_num = page - 1 if has_prev else None
    next_num = page + 1 if has_next else None

    # 生成分页页码列表
    def iter_pages():
        # 简单的分页逻辑，显示当前页前后各2页
        start = max(1, page - 2)
        end = min(total_pages, page + 2)

        # 如果开始页大于1，添加第一页和省略号
        if start > 1:
            yield 1
            if start > 2:
                yield None

        # 添加中间页码
        for p in range(start, end + 1):
            yield p

        # 如果结束页小于总页数，添加省略号和最后一页
        if end < total_pages:
            if end < total_pages - 1:
                yield None
            yield total_pages

    # 创建分页对象
    pagination = {
        "page": page,
        "per_page": per_page,
        "total": total_articles,
        "pages": total_pages,
        "has_prev": has_prev,
        "has_next": has_next,
        "prev_num": prev_num,
        "next_num": next_num,
        "iter_pages": iter_pages
    }

    # 获取当前页的文章
    articles = []
    pen_name = ""
    response = await (Article2.all().filter(status="published").
                      order_by("-published_at").offset(offset).limit(per_page).prefetch_related("tags", "author"))
    for article in response:
        if article.author:
            author = article.author.username
            pen_name = article.author.pen_name
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
            "feature_image": article.cover,
        })

    return templates.TemplateResponse("public/article.html", {
        "request": request,
        "featured_articles": featured_articles,
        "articles": articles,
        "recommended_articles": recommended_articles,
        "hot_articles": hot_articles,
        "recent_comments": recent_comments,
        "pagination": pagination,
        "current_user": current_user
    })


def process_image_urls(html_content, request: Request):
    """处理图片URL，将相对路径转换为绝对路径"""
    from urllib.parse import urljoin

    def replace_image_url(match):
        alt_text = match.group(1)
        img_url = match.group(2)

        # 如果是相对路径，转换为绝对路径
        # if img_url.startswith('/'):
        #     img_url = urljoin(request.host_url, img_url)
        # elif not img_url.startswith(('http://', 'https://')):
        #     # 假设图片存储在 /static/uploads/ 目录
        #     img_url = url_for('static', filename=f'uploads/{img_url}')

        if img_url.startswith('/'):
            # 构建完整的 URL
            base_url = str(request.base_url)
            img_url = urljoin(base_url, img_url.lstrip('/'))
        elif not img_url.startswith(('http://', 'https://')):
            # 对于静态文件，构建正确的 URL
            img_url = str(request.base_url) + f"static/uploads/{img_url}"

        return f'<img src="{img_url}" alt="{alt_text}">'

    # 使用正则表达式替换img标签
    pattern = r'<img src="([^"]*)" alt="([^"]*)">'
    return re.sub(pattern, replace_image_url, html_content)


@router.post("/article_addcomment/{article_id}")
async def submit_comment(
        request: Request,
        article_id: int,
        content: str = Form(...),
        parent_id: Optional[str] = Form(None),
        current_user: User = Depends(require_auth_cookie)
):
    """提交评论"""
    try:
        # 验证文章是否存在
        article = await Article2.get_or_none(id=article_id)
        if not article:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "message": "文章不存在"}
                )
            raise HTTPException(status_code=404, detail="文章不存在")

        # 处理parent_id
        parent_id_int = None
        if parent_id and parent_id.strip():  # 确保不是空字符串
            try:
                parent_id_int = int(parent_id)
            except ValueError:
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JSONResponse(
                        status_code=400,
                        content={"success": False, "message": "无效的父评论ID"}
                    )
                raise HTTPException(status_code=400, detail="无效的父评论ID")

        # 如果是回复评论，验证父评论是否存在
        parent_comment = None
        if parent_id_int:
            parent_comment = await Comment2.get_or_none(id=parent_id_int, article_id=article_id)
            if not parent_comment:
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JSONResponse(
                        status_code=404,
                        content={"success": False, "message": "父评论不存在"}
                    )
                raise HTTPException(status_code=404, detail="父评论不存在")

        # 创建评论
        comment = await Comment2.create(
            content=content,
            author_id=current_user.id,
            article_id=article_id,
            parent_id=parent_id_int,
            is_approved=True  # 如果需要审核，可以设置为False
        )

        # 更新文章评论数
        article.comment_count += 1
        await article.save()

        # 获取完整的评论信息
        comment = await Comment2.get(id=comment.id).prefetch_related('author')

        # 如果是AJAX请求，返回JSON
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JSONResponse(content={
                "success": True,
                "comment": {
                    "id": comment.id,
                    "content": comment.content,
                    "created_at": comment.created_at.strftime('%Y-%m-%d %H:%M'),
                    "author": {
                        "id": comment.author.id,
                        "username": comment.author.username,
                        "pen_name": comment.author.pen_name if hasattr(comment.author,
                                                                       'pen_name') else comment.author.username,
                        "avatar_url": comment.author.avatar_url if hasattr(comment.author, 'avatar_url') else None,
                    }
                }
            })

        # 否则重定向回文章详情页
        return RedirectResponse(url=f"/article/{article_id}#comments", status_code=303)

    except Exception as e:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": f"评论提交失败: {str(e)}"}
            )
        raise HTTPException(status_code=500, detail=f"评论提交失败: {str(e)}")


@router.get("/article/{article_id}/comments")
async def get_comments(
        request: Request,
        article_id: int,
        page: int = 1,
        sort: str = "newest"
):
    """获取评论列表（AJAX）"""
    try:
        # 验证文章是否存在
        article = await Article2.get_or_none(id=article_id)
        if not article:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": "文章不存在"}
            )

        # 构建查询
        query = Comment2.filter(article_id=article_id, parent=None, is_approved=True)

        # 排序
        if sort == "hottest":
            # 假设你有一个点赞字段，如果没有，可以使用创建时间
            query = query.order_by("-created_at")
        else:  # newest
            query = query.order_by("-created_at")

        # 分页
        per_page = 10
        offset = (page - 1) * per_page
        comments = await query.prefetch_related('author', 'replies__author').offset(offset).limit(per_page)

        # 转换为字典格式
        comments_data = []
        for comment in comments:
            comment_dict = {
                "id": comment.id,
                "content": comment.content,
                "created_at": comment.created_at.strftime('%Y-%m-%d %H:%M'),
                "author": {
                    "id": comment.author.id,
                    "username": comment.author.username,
                    "pen_name": comment.author.pen_name if hasattr(comment.author,
                                                                   'pen_name') else comment.author.username,
                    "avatar_url": comment.author.avatar_url if hasattr(comment.author, 'avatar_url') else None,
                },
                "replies": []
            }

            # 添加回复
            for reply in comment.replies:
                if reply.is_approved:
                    comment_dict["replies"].append({
                        "id": reply.id,
                        "content": reply.content,
                        "created_at": reply.created_at.strftime('%Y-%m-%d %H:%M'),
                        "author": {
                            "id": reply.author.id,
                            "username": reply.author.username,
                            "pen_name": reply.author.pen_name if hasattr(reply.author,
                                                                         'pen_name') else reply.author.username,
                            "avatar_url": reply.author.avatar_url if hasattr(reply.author, 'avatar_url') else None,
                        }
                    })

            comments_data.append(comment_dict)

        return JSONResponse(content={"comments": comments_data})

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"获取评论失败: {str(e)}"}
        )


@router.get("/article/{article_id}")
async def article_detail_page(request: Request, article_id: int, current_user=Depends(optional_auth_cookie)):
    """文章详情页"""
    # 获取文章数据
    article = await Article2.filter(id=article_id).first().prefetch_related("tags", "author")

    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    if article.content_type == "markdown":
        article.content = process_markdown(article.content)
        article.content = process_image_urls(article.content, request)

    # 获取文章评论
    comments = await Comment2.filter(article_id=article_id, parent=None, is_approved=True).order_by(
        "-created_at").prefetch_related("author", "replies__author")

    # 获取评论总数
    comment_count = await Comment2.filter(article_id=article_id, is_approved=True).count()

    # 更新文章的评论数
    if article.comment_count != comment_count:
        article.comment_count = comment_count
        await article.save()

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
        "comment_count": comment_count,
        "prev_article": prev_next["prev"],
        "next_article": prev_next["next"],
        "popular_tags": popular_tags,
        "current_user": current_user
    })


@router.get("/strategy")
async def strategy(request: Request, current_user=Depends(optional_auth_cookie)):
    """
    策略页面
    """
    return templates.TemplateResponse(
        "public/strategy.html", {
            "request": request,
            "current_user": current_user
        })


@router.get("/strategy_data")
async def strategy_data(request: Request):
    """
    策略数据
    """
    results = await Strategy.filter(review=True)
    return {"message": "策略数据获取成功", "data": results}


@router.get("/profile")
async def profile(request: Request, current_user=Depends(optional_auth_cookie)):
    """
    个人中心
    """
    return templates.TemplateResponse(
        "public/profile.html", {
            "request": request,
            "current_user": current_user
        })
