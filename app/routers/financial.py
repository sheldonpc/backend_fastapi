"""
金融数据路由 - 集成爬虫服务和调度器控制
"""
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional
from app.services.market_service import MarketDataService
from app.deps import get_current_user

router = APIRouter(prefix="/financial", tags=["financial-crawler"])

# 初始化市场数据服务
market_service = MarketDataService()
BEIJING_TZ = timezone(timedelta(hours=8))


# ==================== 数据查询接口 ====================

@router.get("/market/latest")
async def get_latest_market_data():
    """获取最新的市场数据 - 公开接口"""
    try:
        data = await market_service.get_latest_data()

        if "error" in data:
            raise HTTPException(status_code=500, detail=data["error"])

        return {
            "success": True,
            "data": data,
            "message": "最新市场数据获取成功"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取最新数据失败: {str(e)}")


@router.get("/market/overview")
async def get_market_overview():
    """获取市场概览 - 包含统计信息"""
    try:
        data = await market_service.get_latest_data()

        if "error" in data:
            raise HTTPException(status_code=500, detail=data["error"])

        # 计算统计信息
        total_count = data.get("total_count", 0)
        cn_count = len(data.get("cn_indices", []))
        us_count = len(data.get("us_indices", []))
        pm_count = len(data.get("precious_metals", []))

        # 计算涨跌统计
        all_items = (data.get("cn_indices", []) +
                     data.get("us_indices", []) +
                     data.get("precious_metals", []))

        rising_count = len([item for item in all_items if item.get("change", 0) > 0])
        falling_count = len([item for item in all_items if item.get("change", 0) < 0])

        overview = {
            "statistics": {
                "total_symbols": total_count,
                "cn_indices": cn_count,
                "us_indices": us_count,
                "precious_metals": pm_count,
                "rising": rising_count,
                "falling": falling_count,
                "flat": total_count - rising_count - falling_count
            },
            "market_data": data
        }

        return {
            "success": True,
            "data": overview,
            "message": "市场概览获取成功"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取市场概览失败: {str(e)}")


@router.post("/market/crawl")
async def crawl_market_data(
        background_tasks: BackgroundTasks,
        current_user=Depends(get_current_user)
):
    """
    手动触发市场数据爬取 - 需要登录
    使用后台任务避免超时
    """
    if current_user.role not in ["admin", "user"]:
        raise HTTPException(status_code=403, detail="权限不足")

    # 在后台执行爬取任务
    background_tasks.add_task(market_service.update_all_market_data)

    return {
        "success": True,
        "message": "市场数据爬取任务已启动，这可能需要几分钟时间",
        "tip": "可以通过 /financial/market/latest 查看最新数据"
    }


# ==================== 调度器控制接口 ====================

@router.post("/scheduler/start")
async def start_scheduler(current_user=Depends(get_current_user)):
    """启动调度器 - 需要管理员权限"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")

    try:
        from app.services.scheduler import market_scheduler

        # 检查是否在交易时间内
        is_trading = market_scheduler.is_trading_time()

        if is_trading:
            # 交易时间内正常启动调度器
            await market_scheduler.start_scheduler(force_run_once=False)
            message = "调度器已启动，将在交易时间内每5分钟执行一次"
        else:
            # 非交易时间内，强制执行一次后自动停止
            await market_scheduler.start_scheduler(force_run_once=True)
            message = "非交易时间，已执行一次数据爬取并自动停止调度器"

        return {
            "success": True,
            "message": message,
            "is_trading_time": is_trading,
            "current_time": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动调度器失败: {str(e)}")


@router.post("/scheduler/stop")
async def stop_scheduler(current_user=Depends(get_current_user)):
    """停止调度器 - 需要管理员权限"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")

    try:
        from app.services.scheduler import market_scheduler
        await market_scheduler.stop_scheduler()
        return {"success": True, "message": "调度器已停止"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停止调度器失败: {str(e)}")


@router.get("/scheduler/status")
async def get_scheduler_status():
    """获取调度器状态 - 公开接口"""
    try:
        from app.services.scheduler import market_scheduler

        status = {
            "running": market_scheduler.running,
            "is_trading_time": market_scheduler.is_trading_time(),
            "current_time": datetime.now(BEIJING_TZ).isoformat(),
            "trading_hours": "工作日 9:35-14:00"
        }

        return {"success": True, "data": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取调度器状态失败: {str(e)}")


@router.post("/market/crawl-now")
async def crawl_now(current_user=Depends(get_current_user)):
    """立即执行一次数据爬取 - 需要管理员权限"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")

    try:
        from app.services.scheduler import market_scheduler

        # 直接执行一次爬取任务
        await market_scheduler.run_crawler_task()

        return {
            "success": True,
            "message": "数据爬取已执行完成",
            "execution_time": datetime.now(BEIJING_TZ).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行数据爬取失败: {str(e)}")


# ==================== 数据状态检查接口 ====================

@router.get("/market/status")
async def get_crawler_status():
    """获取爬虫状态信息"""
    try:
        from app.models import IndexData
        from datetime import datetime, timedelta, timezone

        # 检查最近更新时间
        latest_update = await IndexData.all().order_by("-updated_at").first()

        if latest_update:
            # 确保时间比较的一致性
            # 使用北京时间进行比较
            now = datetime.now(BEIJING_TZ)
            updated_at = latest_update.updated_at

            # 如果数据库时间没有时区信息，假设为北京时间
            if updated_at.tzinfo is None:
                updated_at = updated_at.replace(tzinfo=BEIJING_TZ)

            time_diff = now - updated_at
            is_recent = time_diff < timedelta(minutes=30)

            status = {
                "last_update": latest_update.updated_at.isoformat(),
                "minutes_ago": int(time_diff.total_seconds() / 60),
                "is_recent": is_recent,
                "status": "数据正常" if is_recent else "数据较老"
            }
        else:
            status = {
                "last_update": None,
                "minutes_ago": None,
                "is_recent": False,
                "status": "无数据"
            }

        return {
            "success": True,
            "data": status,
            "message": "爬虫状态获取成功"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取爬虫状态失败: {str(e)}")