# app/routers/board.py
from fastapi import APIRouter, HTTPException
from .internal import industry_service, stock_service, concept_service, lhb_service, hot_service, zt_service

router = APIRouter(prefix="/api/board", tags=["Board"])


@router.get("/{board_type}/{period}/")
@router.get("/{board_type}/")
async def get_board_data(board_type: str, period: str = None):
    """为榜单中心页面提供的统一接口"""
    service_map = {
        "industry": industry_service.get_industry_ranking,
        "stock": stock_service.get_stock_ranking,
        "concept": concept_service.get_concept_ranking,
        "lhb": lhb_service.get_lhb_ranking,
        "hot": hot_service.get_hot_ranking,
        "zt": zt_service.get_zt_ranking,
    }

    if board_type not in service_map:
        raise HTTPException(status_code=400, detail="不支持的榜单类型")

    try:
        # 修复：传递 period 参数
        if board_type in ["lhb", "hot"]:
            # 这些函数不需要 period 参数
            return await service_map[board_type]()
        else:
            return await service_map[board_type](period)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取{board_type}数据失败: {str(e)}")