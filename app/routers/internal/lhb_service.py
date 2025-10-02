# app/routers/internal/lhb_service.py
from app.schemas import StockLHBDetail_Pydantic
from app.models import StockLHBDetail
from datetime import date


async def get_lhb_ranking():
    """获取龙虎榜数据 - 不需要 period 参数"""
    today = date.today()

    # 修复：确保返回的是 QuerySet
    records = StockLHBDetail.filter(listing_date=today).order_by("-lhb_net_buy_amount")

    if not await records.exists():
        # 如果没有今天的数据，返回最近的数据
        records = StockLHBDetail.all().order_by("-listing_date", "-lhb_net_buy_amount")

    return await StockLHBDetail_Pydantic.from_queryset(records)
