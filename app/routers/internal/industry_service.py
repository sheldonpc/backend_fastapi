# app/routers/internal/industry_service.py
from app.schemas import (
    IndustryLatest_Pydantic,
    IndustryLast3Days_Pydantic,
    IndustryLast5Days_Pydantic,
    IndustryLast10Days_Pydantic,
    IndustryLast20Days_Pydantic
)
from app.models import (
    IndustryLatest,
    IndustryLast3Days,
    IndustryLast5Days,
    IndustryLast10Days,
    IndustryLast20Days
)


async def get_industry_ranking(period: str = None):
    """获取行业榜单数据"""
    model_map = {
        "latest": (IndustryLatest, IndustryLatest_Pydantic),
        "3d": (IndustryLast3Days, IndustryLast3Days_Pydantic),
        "5d": (IndustryLast5Days, IndustryLast5Days_Pydantic),
        "10d": (IndustryLast10Days, IndustryLast10Days_Pydantic),
        "20d": (IndustryLast20Days, IndustryLast20Days_Pydantic),
    }

    # 默认使用最新数据
    if not period or period not in model_map:
        period = "latest"

    model, pydantic_model = model_map[period]

    # 修复：确保返回的是 QuerySet，不是列表
    records = model.all().order_by("-net_amount")

    # 修复：直接返回 Pydantic 模型序列化结果
    return await pydantic_model.from_queryset(records)