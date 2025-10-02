# app/routers/internal/zt_service.py
from app.schemas import (
    StockZTPool_Pydantic,
    StockZTPoolPrevious_Pydantic,
    StockZTPoolStrong_Pydantic,
    StockZTPoolDown_Pydantic
)
from app.models import (
    StockZTPool,
    StockZTPoolPrevious,
    StockZTPoolStrong,
    StockZTPoolDown
)
from datetime import date, datetime, timedelta


async def get_zt_ranking(pool_type: str = None):
    """获取涨停股池数据"""
    try:
        # 获取最近的有效交易日（可能是今天或上一个交易日）
        today = date.today()

        # 尝试查找最近有数据的交易日
        latest_trade_date = await get_latest_trade_date(pool_type)

        if not latest_trade_date:
            return []  # 没有数据

        if pool_type == "today":
            records = StockZTPool.filter(trade_date=latest_trade_date).order_by("-change_rate")
            return await StockZTPool_Pydantic.from_queryset(records)

        elif pool_type == "yesterday":
            records = StockZTPoolPrevious.filter(trade_date=latest_trade_date).order_by("-change_rate")
            return await StockZTPoolPrevious_Pydantic.from_queryset(records)

        elif pool_type == "strong":
            records = StockZTPoolStrong.filter(trade_date=latest_trade_date).order_by("-change_rate")
            return await StockZTPoolStrong_Pydantic.from_queryset(records)

        elif pool_type == "down":
            records = StockZTPoolDown.filter(trade_date=latest_trade_date).order_by("change_rate")
            return await StockZTPoolDown_Pydantic.from_queryset(records)

        else:
            # 默认返回今日涨停
            records = StockZTPool.filter(trade_date=latest_trade_date).order_by("-change_rate")
            return await StockZTPool_Pydantic.from_queryset(records)

    except Exception as e:
        print(f"涨停股池数据获取错误: {str(e)}")
        return []  # 出错时返回空数组


async def get_latest_trade_date(pool_type: str):
    """获取最近的有效交易日"""
    try:
        # 根据类型选择不同的模型
        if pool_type == "today":
            model = StockZTPool
        elif pool_type == "yesterday":
            model = StockZTPoolPrevious
        elif pool_type == "strong":
            model = StockZTPoolStrong
        elif pool_type == "down":
            model = StockZTPoolDown
        else:
            model = StockZTPool

        # 查找有数据的最新交易日
        latest_record = await model.all().order_by("-trade_date").first()

        if latest_record:
            return latest_record.trade_date

        # 如果没有数据，返回今天的日期作为默认值
        return date.today().strftime("%Y%m%d")

    except Exception as e:
        print(f"获取最近交易日错误: {str(e)}")
        return date.today().strftime("%Y%m%d")
