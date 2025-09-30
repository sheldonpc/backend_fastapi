import asyncio
import logging
import random
from datetime import datetime, time, timedelta
from functools import wraps
from zoneinfo import ZoneInfo

from app.services.market_data_service import (
    fetch_realtime_market_data,
    fetch_fx_market_data, fetch_stock_hot_follow_market_data,
    fetch_minute_cn_market_data, fetch_minute_usa_market_data, fetch_minute_hk_market_data,
    fetch_vix_index, fetch_rise_down_index, fetch_daily_market_data,
    fetch_cn_us_bond_market_data, fetch_hurun_rank_market_data,
    fetch_global_market_data, fetch_global_market_data2,
    fetch_global_market_data3, fetch_global_market_data4,
    fetch_fx_market_history_data,
    fetch_oil_data, fetch_gold_data, fetch_silver_data, fetch_eastmoney_history_market_data, crawl_llm_insight,
    brief_rise_down_data, news_ai_summary
)

logger = logging.getLogger(__name__)

# ==== 交易时间配置 ====
CN_SESSIONS = [(time(9, 30), time(11, 30)), (time(13, 0), time(23, 0))]
US_SESSIONS = [(time(9, 30), time(17, 0))]


def log_task(name: str):
    """通用任务装饰器：自动打日志"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger.info(f"开始更新 {name}")
            try:
                await func(*args, **kwargs)
                logger.info(f"✅ {name} 更新成功")
            except Exception:
                logger.exception(f"❌ {name} 更新失败")
        return wrapper
    return decorator


class NewMarketScheduler:
    """市场数据定时调度器"""

    def __init__(self):
        self.running = False
        self.tasks: list[asyncio.Task] = []
        self.force_run_once = False

    # ==== 交易时间判断 ====
    def is_cn_trading_time(self) -> bool:
        now = datetime.now(ZoneInfo("Asia/Shanghai"))
        return now.weekday() < 5 and any(start <= now.time() < end for start, end in CN_SESSIONS)

    def is_usa_trading_time(self) -> bool:
        now = datetime.now(ZoneInfo("America/New_York"))
        return now.weekday() < 5 and any(start <= now.time() < end for start, end in US_SESSIONS)

    def is_cn_trading_day(self) -> bool:
        return datetime.now(ZoneInfo("Asia/Shanghai")).weekday() < 5

    # ==== 任务定义 ====
    @log_task("全球市场指数信息")
    async def run_update_global_index_data(self):
        await fetch_realtime_market_data()

    @log_task("外汇数据")
    async def update_fx_market_data(self):
        await fetch_fx_market_data()

    @log_task("中国分时数据")
    async def update_minute_level_cn_data(self):
        await fetch_minute_cn_market_data()

    # 数据很大 获取很慢
    @log_task("美国分时数据")
    async def update_minute_level_usa_data(self):
        await fetch_minute_usa_market_data()

    @log_task("香港分时数据")
    async def update_minute_level_hk_data(self):
        await fetch_minute_hk_market_data()

    @log_task("石油数据")
    async def update_oil_data(self):
        await fetch_oil_data()

    @log_task("黄金数据")
    async def update_gold_data(self):
        await fetch_gold_data()

    @log_task("白银数据")
    async def update_silver_data(self):
        await fetch_silver_data()

    @log_task("VIX指数")
    async def update_vix_index(self):
        await fetch_vix_index()

    @log_task("涨跌数据")
    async def update_rise_down_data(self):
        await fetch_rise_down_index()

    @log_task("历史市场数据")
    async def update_index_history_data(self):
        await fetch_daily_market_data()

    @log_task("外汇历史数据")
    async def update_fx_history_data(self):
        await fetch_fx_market_history_data()

    @log_task("债券数据")
    async def update_bond_data(self):
        await fetch_cn_us_bond_market_data()

    @log_task("东方财富新闻")
    async def update_eastmoney_news(self):
        await fetch_eastmoney_history_market_data()

    @log_task("新闻1")
    async def update_news_one(self):
        await fetch_global_market_data()

    @log_task("新闻2")
    async def update_news_two(self):
        await fetch_global_market_data2()

    @log_task("新闻3")
    async def update_news_three(self):
        await fetch_global_market_data3()

    @log_task("新闻4")
    async def update_news_four(self):
        await fetch_global_market_data4()

    @log_task("dify")
    async def update_ai_insight(self):
        await crawl_llm_insight()

    @log_task("notice_rise_down")
    async def update_notice_rise_down(self):
        await brief_rise_down_data()

    @log_task("胡润排行榜")
    async def yearly_update_hurun_rank(self):
        await fetch_hurun_rank_market_data()

    @log_task("AI昨日总结")
    async def update_ai_yesterday_summary(self):
        await news_ai_summary()

    async def run_cn_5min_tasks(self):
        tasks = [
            self.update_fx_market_data,
            self.update_oil_data,
            self.update_gold_data,
            self.update_silver_data,
            self.update_vix_index,
            self.update_rise_down_data,
            self.update_notice_rise_down,
        ]

        for task in tasks:
            try:
                await task()
                sleep_time = random.uniform(5, 10)
                await asyncio.sleep(sleep_time)
            except Exception as e:
                logger.error(f"run_cn_5min_tasks任务执行失败: {task.__name__} - {str(e)}")

    async def run_global_5min_tasks(self):
        await asyncio.sleep(random.uniform(5, 10))
        await self.run_update_global_index_data()

    async def run_cn_daily_tasks(self):
        tasks = [
            self.update_index_history_data(),
            self.update_fx_history_data(),
            self.update_bond_data(),
            self.update_eastmoney_news(),
            self.update_news_one(),
            self.update_news_two(),
            self.update_news_three(),
            self.update_news_four(),
            self.update_ai_insight(),
        ]

        for task in tasks:
            try:
                await task
                sleep_time = random.uniform(5, 10)
                await asyncio.sleep(sleep_time)
            except Exception as e:
                logger.error(f"run_cn_daily_tasks任务执行失败: {task.__name__} - {str(e)}")

    async def run_hourly_tasks(self):
        await asyncio.gather(
            self.update_minute_level_cn_data(),
            # self.update_minute_level_usa_data(),
            self.update_minute_level_hk_data(),
        )

    # 每天早上7点运行一次
    async def run_ai_daily_tasks(self):
        await asyncio.gather(
            self.update_ai_yesterday_summary()
        )

    # ==== force_run_once 统一退出方法 ====
    def _shutdown_after_force_once(self):
        """当 force_run_once 启用时，运行一次后关闭整个调度器"""
        if self.force_run_once:
            logger.info("force_run_once 模式：任务已执行一次，调度器即将退出")
            self.running = False
            return True
        return False

    # ==== 调度循环 ====
    async def _scheduler_loop_5min_cn(self):
        while self.running:
            if self.is_cn_trading_time():
                await self.run_cn_5min_tasks()
                if self._shutdown_after_force_once():
                    break
            await self._safe_sleep(120)

    async def _scheduler_loop_5min_global(self):
        while self.running:
            await self.run_global_5min_tasks()
            if self._shutdown_after_force_once():
                break
            await self._safe_sleep(300)

    async def _scheduler_loop_daily_cn(self):
        daily_times = [time(7, 0), time(10, 0),time(14, 0), time(18, 0)]
        while self.running:
            now = datetime.now(ZoneInfo("Asia/Shanghai"))
            today = now.date()
            next_run = min(
                (datetime.combine(today, t, tzinfo=ZoneInfo("Asia/Shanghai"))
                 for t in daily_times
                 if datetime.combine(today, t, tzinfo=ZoneInfo("Asia/Shanghai")) > now),
                default=datetime.combine(today + timedelta(days=1), daily_times[0], tzinfo=ZoneInfo("Asia/Shanghai"))
            )
            sleep_sec = (next_run - now).total_seconds()
            logger.info(f"CN每日任务将在 {sleep_sec:.0f} 秒后执行")
            await self._safe_sleep(sleep_sec)

            if not self.running:
                break
            if self.is_cn_trading_day():
                await self.run_cn_daily_tasks()
                if self._shutdown_after_force_once():
                    break

    async def _scheduler_loop_daily_ai_summary(self):
        daily_times = [time(7, 0)]
        while self.running:
            now = datetime.now(ZoneInfo("Asia/Shanghai"))
            today = now.date()
            next_run = min(
                (datetime.combine(today, t, tzinfo=ZoneInfo("Asia/Shanghai"))
                 for t in daily_times
                 if datetime.combine(today, t, tzinfo=ZoneInfo("Asia/Shanghai")) > now),
                default=datetime.combine(today + timedelta(days=1), daily_times[0], tzinfo=ZoneInfo("Asia/Shanghai"))
            )
            sleep_sec = (next_run - now).total_seconds()
            logger.info(f"AI News Summary 每日任务将在 {sleep_sec:.0f} 秒后执行")
            await self._safe_sleep(sleep_sec)

            if not self.running:
                break
            if self.is_cn_trading_day():
                await self.run_ai_daily_tasks()
                if self._shutdown_after_force_once():
                    break

    async def _scheduler_loop_hourly(self):
        daily_times = [time(h, 0) for h in range(10, 19)]
        while self.running:
            now = datetime.now(ZoneInfo("Asia/Shanghai"))
            today = now.date()
            next_run = min(
                (datetime.combine(today, t, tzinfo=ZoneInfo("Asia/Shanghai"))
                 for t in daily_times
                 if datetime.combine(today, t, tzinfo=ZoneInfo("Asia/Shanghai")) > now),
                default=datetime.combine(today + timedelta(days=1), daily_times[0], tzinfo=ZoneInfo("Asia/Shanghai"))
            )
            sleep_sec = (next_run - now).total_seconds()
            logger.info(f"小时任务将在 {sleep_sec:.0f} 秒后执行")
            await self._safe_sleep(sleep_sec)

            if not self.running:
                break
            if self.is_cn_trading_day():
                await self.run_hourly_tasks()
                if self._shutdown_after_force_once():
                    break

    async def _safe_sleep(self, seconds: float):
        """安全 sleep，支持取消"""
        try:
            await asyncio.sleep(seconds)
        except asyncio.CancelledError:
            pass

    # ==== 调度器控制 ====
    async def start_scheduler(self, force_run_once: bool = False):
        if self.running:
            logger.warning("调度器已在运行中")
            return

        self.running = True
        self.force_run_once = force_run_once
        logger.info("市场数据调度器启动")

        self.tasks = [
            asyncio.create_task(self._scheduler_loop_5min_cn()),
            asyncio.create_task(self._scheduler_loop_daily_cn()),
            asyncio.create_task(self._scheduler_loop_5min_global()),
            asyncio.create_task(self._scheduler_loop_hourly()),
            asyncio.create_task(self._scheduler_loop_daily_ai_summary()),
        ]

    async def stop_scheduler(self):
        if not self.running:
            logger.warning("调度器未运行")
            return

        self.running = False
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        logger.info("✅ 调度器已停止")

if __name__ == "__main__":
    scheduler = NewMarketScheduler()
    print("是否在中国交易时间:", scheduler.is_cn_trading_time())
