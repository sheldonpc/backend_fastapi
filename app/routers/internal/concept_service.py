# app/routers/internal/concept_service.py
from app.schemas import (
    ConceptLatest_Pydantic,
    ConceptLast3Days_Pydantic,
    ConceptLast5Days_Pydantic,
    ConceptLast10Days_Pydantic,
    ConceptLast20Days_Pydantic
)
from app.models import (
    ConceptLatest,
    ConceptLast3Days,
    ConceptLast5Days,
    ConceptLast10Days,
    ConceptLast20Days
)


async def get_concept_ranking(period: str = None):
    """获取概念榜单数据"""
    model_map = {
        "latest": (ConceptLatest, ConceptLatest_Pydantic),
        "3d": (ConceptLast3Days, ConceptLast3Days_Pydantic),
        "5d": (ConceptLast5Days, ConceptLast5Days_Pydantic),
        "10d": (ConceptLast10Days, ConceptLast10Days_Pydantic),
        "20d": (ConceptLast20Days, ConceptLast20Days_Pydantic),
    }

    if not period or period not in model_map:
        period = "latest"

    model, pydantic_model = model_map[period]

    # 修复：确保返回的是 QuerySet
    records = model.all().order_by("-net_amount").limit(100)

    return await pydantic_model.from_queryset(records)
