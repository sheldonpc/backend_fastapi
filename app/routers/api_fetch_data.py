import logging
from fastapi import APIRouter, BackgroundTasks
from app.services.market_data_service import fetch_realtime_market_data, fetch_fx_market_data, \
    fetch_fx_market_history_data, fetch_minute_cn_market_data, fetch_minute_hk_market_data, \
    fetch_foreign_commodity_data, fetch_vix_index, fetch_rise_down_index, fetch_daily_market_data, \
    fetch_global_index_history, fetch_sge_history, fetch_index_history, fetch_cn_us_bond_market_data, \
    fetch_hurun_rank_market_data, fetch_global_market_data, fetch_global_market_data2, fetch_global_market_data3, \
    fetch_global_market_data4, fetch_eastmoney_history_market_data

router = APIRouter(
    prefix="/fetch",
    tags=["fetch_test"],
)

logger = logging.getLogger(__name__)

@router.post("/market-data")
async def trigger_market_data_fetch(background_tasks: BackgroundTasks):
    """
    手动触发全球指数数据拉取（后台任务）
    """
    background_tasks.add_task(fetch_realtime_market_data)
    return {"message": "全球指数数据拉取任务已加入后台队列"}


@router.post("/fx-data")
async def trigger_fx_data_fetch(background_tasks: BackgroundTasks):
    """
    手动触发外汇数据拉取（后台任务）
    """
    background_tasks.add_task(fetch_fx_market_data)
    return {"message": "外汇数据拉取任务已加入后台队列"}

@router.post("/fx-history")
async def trigger_fx_history_fetch(background_tasks: BackgroundTasks):
    """
    手动触发历史外汇牌价（中国银行）增量拉取（后台任务）
    """
    background_tasks.add_task(fetch_fx_market_history_data)
    return {"message": "历史外汇牌价增量拉取任务已加入后台队列"}

@router.post("/cn-minute")
async def trigger_cn_minute_fetch(background_tasks: BackgroundTasks):
    """
    手动触发 A 股分钟级行情快照拉取（覆盖式全量更新）
    """
    background_tasks.add_task(fetch_minute_cn_market_data)
    return {"message": "A股分钟级行情拉取任务已加入后台队列"}


@router.post("/hk-minute")
async def trigger_hk_minute_fetch(background_tasks: BackgroundTasks):
    """
    手动触发 港股实时行情快照拉取（覆盖式全量更新）
    """
    background_tasks.add_task(fetch_minute_hk_market_data)
    return {"message": "港股实时行情拉取任务已加入后台队列"}

@router.post("/foreign-commodity")
async def trigger_foreign_commodity_fetch(background_tasks: BackgroundTasks):
    """
    手动触发外盘商品实时数据拉取
    """
    background_tasks.add_task(fetch_foreign_commodity_data)
    return {"message": "外盘商品数据拉取任务已加入后台队列"}

@router.post("/vix")
async def trigger_vix_fetch(background_tasks: BackgroundTasks):
    """
    手动触发 VIX 指数数据拉取
    """
    background_tasks.add_task(fetch_vix_index)
    return {"message": "VIX 指数数据拉取任务已加入后台队列"}

@router.post("/rise-down")
async def trigger_rise_down_fetch(background_tasks: BackgroundTasks):
    """
    手动触发涨跌家数指数数据拉取
    """
    background_tasks.add_task(fetch_rise_down_index)
    return {"message": "涨跌家数指数数据拉取任务已加入后台队列"}

@router.post("/daily-market-data")
async def trigger_daily_market_data_fetch(background_tasks: BackgroundTasks):
    """
    手动触发每日市场数据（国内指数、全球指数、贵金属）拉取
    """
    background_tasks.add_task(fetch_daily_market_data)
    return {"message": "每日市场数据拉取任务已加入后台队列"}

@router.post("/cn-us-bond-market-data")
async def trigger_cn_us_bond_market_data_fetch(background_tasks: BackgroundTasks):
    """
    手动触发中美债券市场数据拉取
    """
    background_tasks.add_task(fetch_cn_us_bond_market_data)
    return {"message": "中美债券市场数据拉取任务已加入后台队列"}

@router.post("/hurun-rich-list")
async def trigger_hurun_rank_market_data_fetch(background_tasks: BackgroundTasks):
    """
    手动触发胡润百富榜数据拉取
    """
    background_tasks.add_task(fetch_hurun_rank_market_data)
    return {"message": "胡润百富榜数据拉取任务已加入后台队列"}

@router.post("/global-market-data")
async def trigger_global_market_data_fetch(background_tasks: BackgroundTasks):
    """
    手动触发全球市场数据（富途新闻）拉取
    """
    background_tasks.add_task(fetch_global_market_data)
    return {"message": "全球市场数据拉取任务已加入后台队列"}

@router.post("/global-market-data2")
async def trigger_global_market_data2_fetch(background_tasks: BackgroundTasks):
    """
    手动触发全球市场数据（同花顺）拉取
    """
    background_tasks.add_task(fetch_global_market_data2)
    return {"message": "全球市场数据2拉取任务已加入后台队列"}

@router.post("/global-market-data3")
async def trigger_global_market_data3_fetch(background_tasks: BackgroundTasks):
    """
    手动触发全球市场数据（东方财富）拉取
    """
    background_tasks.add_task(fetch_global_market_data3)
    return {"message": "全球市场数据3拉取任务已加入后台队列"}

@router.post("/global-market-data4")
async def trigger_global_market_data4_fetch(background_tasks: BackgroundTasks):
    """
    手动触发全球市场数据（新浪）拉取
    """
    background_tasks.add_task(fetch_global_market_data4)
    return {"message": "全球市场数据4拉取任务已加入后台队列"}

@router.post("/eastmoney-history-news")
async def trigger_eastmoney_history_news_market_data_fetch(background_tasks: BackgroundTasks):
    """
    手动触发东方财富历史资讯数据拉取
    """
    background_tasks.add_task(fetch_eastmoney_history_market_data)
    return {"message": "东方财富历史资讯数据拉取任务已加入后台队列"}