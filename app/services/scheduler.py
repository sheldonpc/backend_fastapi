import asyncio
import logging
from datetime import datetime, time, timezone, timedelta
from typing import Optional
from app.services.market_service import MarketDataService

logger = logging.getLogger(__name__)
BEIJING_TZ = timezone(timedelta(hours=8))


class MarketScheduler:
    """市场数据定时调度器"""

    def __init__(self):
        self.market_service = MarketDataService()
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.force_run_once = False  # 新增：强制执行一次的标志

    def is_trading_time(self) -> bool:
        """检查是否在交易时间内"""
        now = datetime.now(BEIJING_TZ)

        # 检查是否为工作日（周一到周五）
        if now.weekday() >= 5:  # 5=周六, 6=周日
            return False

        # 检查时间范围 9:35-14:00
        current_time = now.time()
        start_time = time(9, 35)  # 9:35
        end_time = time(14, 0)  # 14:00

        return start_time <= current_time <= end_time

    async def run_crawler_task(self):
        """执行单次爬取任务"""
        try:
            logger.info("开始执行金融数据爬取任务...")
            result = await self.market_service.update_all_market_data()

            if result["success"]:
                logger.info(f"爬取成功: {result['successful_crawls']}/{result['total_targets']} 个目标")
                logger.info(f"保存到数据库: {result['saved_to_db']} 条记录")
            else:
                logger.error(f"爬取失败: {result.get('error')}")

        except Exception as e:
            logger.error(f"执行爬取任务时出错: {e}")

    async def start_scheduler(self, force_run_once: bool = False):
        """启动调度器"""
        if self.running:
            logger.warning("调度器已在运行中")
            return

        self.running = True
        self.force_run_once = force_run_once  # 设置强制执行标志
        logger.info("市场数据调度器启动")

        # 创建后台任务
        self.task = asyncio.create_task(self._scheduler_loop())

    async def stop_scheduler(self):
        """停止调度器"""
        if not self.running:
            return

        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

        logger.info("市场数据调度器已停止")

    async def _scheduler_loop(self):
        """调度器主循环"""
        try:
            # 如果设置了强制执行一次的标志
            if self.force_run_once:
                logger.info("管理员手动触发，立即执行一次数据爬取")
                await self.run_crawler_task()
                self.force_run_once = False  # 重置标志

                # 如果不在交易时间内，执行完毕后自动停止调度器
                if not self.is_trading_time():
                    logger.info("非交易时间，手动执行完毕后自动停止调度器")
                    self.running = False
                    return

            while self.running:
                if self.is_trading_time():
                    logger.info("当前在交易时间内，执行数据爬取")
                    await self.run_crawler_task()
                    # 交易时间内每5分钟执行一次
                    await asyncio.sleep(300)  # 5分钟
                else:
                    logger.debug("当前不在交易时间内，跳过执行")
                    # 非交易时间每30分钟检查一次
                    await asyncio.sleep(1800)  # 30分钟

        except asyncio.CancelledError:
            logger.info("调度器循环被取消")
        except Exception as e:
            logger.error(f"调度器循环出错: {e}")


# 全局调度器实例
market_scheduler = MarketScheduler()