from app.schemas import StockHotSearchBaidu_Pydantic
from app.models import StockHotSearchBaidu


async def get_hot_search(market_type: str = None):
    """获取热搜榜数据"""
    try:
        # 构建查询
        query = StockHotSearchBaidu.all()

        # 如果指定了市场类型，进行筛选
        if market_type:
            # 将前端传递的市场类型映射到数据库中的值
            market_map = {
                "ag": "A股",
                "hk": "港股",
                "us": "美股"
            }
            db_market_type = market_map.get(market_type)
            if db_market_type:
                query = query.filter(symbol_type=db_market_type)

        # 按综合热度排序
        records = query.order_by("-comprehensive_heat")
        return await StockHotSearchBaidu_Pydantic.from_queryset(records)

    except Exception as e:
        print(f"热搜榜数据获取错误: {str(e)}")
        raise e