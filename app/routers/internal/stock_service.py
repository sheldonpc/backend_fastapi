# app/routers/internal/stock_service.py
from app.schemas import (
    StockLatest_Pydantic,
    StockLast3Days_Pydantic,
    StockLast5Days_Pydantic,
    StockLast10Days_Pydantic,
    StockLast20Days_Pydantic
)
from app.models import (
    StockLatest,
    StockLast3Days,
    StockLast5Days,
    StockLast10Days,
    StockLast20Days
)


async def get_stock_ranking(period: str = None):
    """获取个股榜单数据"""
    model_map = {
        "latest": (StockLatest, StockLatest_Pydantic),
        "3d": (StockLast3Days, StockLast3Days_Pydantic),
        "5d": (StockLast5Days, StockLast5Days_Pydantic),
        "10d": (StockLast10Days, StockLast10Days_Pydantic),
        "20d": (StockLast20Days, StockLast20Days_Pydantic),
    }

    if not period or period not in model_map:
        period = "latest"

    model, pydantic_model = model_map[period]

    # 修复：确保返回的是 QuerySet
    records = model.all().order_by("-net_amount").limit(100)

    return await pydantic_model.from_queryset(records)