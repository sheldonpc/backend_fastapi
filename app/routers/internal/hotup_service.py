from app.schemas import StockHotUp_Pydantic
from app.models import StockHotUp
from datetime import date, datetime


async def get_hot_up():
    """获取飙升榜数据"""
    try:
        today = date.today()

        # 方法1：使用日期范围查询
        records = StockHotUp.filter(
            update_time__gte=datetime(today.year, today.month, today.day)
        ).order_by("current_rank")

        # 检查是否有今天的数据
        if not await records.exists():
            # 如果没有今天的数据，返回最近的数据
            records = StockHotUp.all().order_by("-rank_change")

        return await StockHotUp_Pydantic.from_queryset(records)

    except Exception as e:
        # 添加详细错误信息便于调试
        print(f"飙升榜数据获取错误: {str(e)}")
        raise e
