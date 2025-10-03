# app/routers/internal/hot_service.py
from app.schemas import StockHotRank_Pydantic
from app.models import StockHotRank
from datetime import date, datetime


async def get_hot_ranking():
    """获取热门股数据"""
    try:
        today = date.today()

        # 方法1：使用日期范围查询
        records = StockHotRank.filter(
            update_time__gte=datetime(today.year, today.month, today.day)
        ).order_by("current_rank")

        # 检查是否有今天的数据
        if not await records.exists():
            # 如果没有今天的数据，返回最近的数据
            records = StockHotRank.all().order_by("-update_time", "current_rank")

        return await StockHotRank_Pydantic.from_queryset(records)

    except Exception as e:
        # 添加详细错误信息便于调试
        print(f"热门股数据获取错误: {str(e)}")
        raise e
