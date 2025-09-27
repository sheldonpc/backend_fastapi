from fastapi import APIRouter

router = APIRouter(
    prefix="/market",
    tags=["market"],
)

@router.get("/")
async def get_market_data():
    """
    获取行情数据
    """
    return {"message": "获取行情数据成功"}