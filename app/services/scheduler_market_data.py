import asyncio
import logging
import random
from datetime import datetime, time, timedelta
from functools import wraps
from zoneinfo import ZoneInfo
import chinese_calendar as cn_calendar
from app.services.market_data_service import (
    fetch_realtime_market_data,
    fetch_fx_market_data,
    fetch_minute_cn_market_data, fetch_minute_hk_market_data,
    fetch_vix_index, fetch_rise_down_index, fetch_daily_market_data,
    fetch_cn_us_bond_market_data, fetch_hurun_rank_market_data,
    fetch_global_market_data, fetch_global_market_data2,
    fetch_global_market_data3, fetch_global_market_data4,
    fetch_fx_market_history_data,
    fetch_eastmoney_history_market_data, crawl_llm_insight,
    brief_rise_down_data, news_ai_summary, get_forex_data_async, get_industry_data, get_stock_data, get_concept_data,
    get_and_save_stock_lhb_detail, get_and_save_stock_hot_rank,
    get_and_save_stock_hot_search_baidu, get_and_save_stock_zt_pool, get_and_save_stock_zt_pool_previous,
    get_and_save_stock_zt_pool_strong, get_and_save_stock_zt_pool_down, fetch_foreign_commodity_data,
    get_and_save_all_stock_hot_search_baidu
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
    def is_cn_trading_day(self) -> bool:
        now = datetime.now(ZoneInfo("Asia/Shanghai"))
        current_date = now.date()

        # 判断是否为周末
        if now.weekday() >= 5:
            return False

        # 判断是否为节假日
        if cn_calendar.is_holiday(current_date):
            return False

        # 判断是否为调休工作日（节假日但需要上班）
        if cn_calendar.is_in_lieu(current_date):
            return True

        # 检查交易时间段
        return any(start <= now.time() < end for start, end in CN_SESSIONS)

    def is_usa_trading_time(self) -> bool:
        now = datetime.now(ZoneInfo("America/New_York"))
        return now.weekday() < 5 and any(start <= now.time() < end for start, end in US_SESSIONS)

    # ==== 任务定义 ====
    @log_task("全球市场指数信息")
    async def run_update_global_index_data(self):
        await fetch_realtime_market_data()

    @log_task("外汇数据")
    async def update_fx_market_data(self):
        await fetch_fx_market_data()

    @log_task("期货数据")
    async def update_foreign_commodity_data(self):
        await fetch_foreign_commodity_data()

    @log_task("中国分时数据")
    async def update_minute_level_cn_data(self):
        await fetch_minute_cn_market_data()

    @log_task("香港分时数据")
    async def update_minute_level_hk_data(self):
        await fetch_minute_hk_market_data()

    @log_task("VIX指数")
    async def update_vix_index(self):
        await fetch_vix_index()

    @log_task("涨跌数据")
    async def update_rise_down_data(self):
        await fetch_rise_down_index()

    @log_task("历史市场数据")
    async def update_index_history_data(self):
        await fetch_daily_market_data()

    @log_task("全球经济日历")
    async def update_global_calendar(self):
        await get_forex_data_async()

    @log_task("行业数据")
    async def update_industry_data(self):
        await get_industry_data()

    @log_task("个股数据")
    async def update_stock_data(self):
        await get_stock_data()

    @log_task("概念股")
    async def update_concept_data(self):
        await get_concept_data()

    @log_task("龙虎榜单")
    async def update_lhb_data(self):
        await get_and_save_stock_lhb_detail()

    @log_task("人气榜单")
    async def update_hot_rank_data(self):
        await get_and_save_stock_hot_rank()

    @log_task("飙升榜")
    async def update_hot_up_data(self):
        await get_and_save_all_stock_hot_search_baidu()

    @log_task("百度热搜")
    async def update_hot_search_baidu(self):
        await get_and_save_stock_hot_search_baidu()

    @log_task("涨停股池")
    async def update_zt_pool(self):
        await get_and_save_stock_zt_pool()

    @log_task("昨日涨停股池")
    async def update_zt_pool_previous(self):
        await get_and_save_stock_zt_pool_previous()

    @log_task("强势股池")
    async def update_zt_pool_strong(self):
        await get_and_save_stock_zt_pool_strong()

    @log_task("跌停股池")
    async def update_zt_pool_down(self):
        await get_and_save_stock_zt_pool_down()

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

        if not self.is_cn_trading_day():
            return

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
            self.update_industry_data(),
            self.update_stock_data(),
            self.update_concept_data(),
            self.update_lhb_data(),
            self.update_hot_rank_data(),
            self.update_hot_up_data(),
            self.update_hot_search_baidu(),
            self.update_zt_pool(),
            self.update_zt_pool_previous(),
            self.update_zt_pool_strong(),
            self.update_zt_pool_down(),
            self.update_foreign_commodity_data()
        ]

        for task in tasks:
            try:
                await task
                sleep_time = random.uniform(5, 10)
                await asyncio.sleep(sleep_time)
            except Exception as e:
                logger.error(f"run_cn_daily_tasks任务执行失败: {task.__name__} - {str(e)}")

    async def run_news_hourly_tasks(self):
        tasks = [
            self.update_eastmoney_news(),
            self.update_news_one(),
            self.update_news_two(),
            self.update_news_three(),
            self.update_news_four(),
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

    async def run_first_ai_daily_tasks(self):
        await asyncio.gather(
            self.update_ai_insight()
        )

    # 每天早上7点运行一次
    async def run_second_ai_daily_tasks(self):
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
            if self.is_cn_trading_day():
                await self.run_cn_5min_tasks()
                if self._shutdown_after_force_once():
                    break
            await self._safe_sleep(120)

    # 全球指数信息5分钟更新一次
    async def _scheduler_loop_5min_global(self):
        while self.running:
            if not self.is_cn_trading_day():
                return
            await self.run_global_5min_tasks()
            if self._shutdown_after_force_once():
                break
            await self._safe_sleep(300)

    async def _scheduler_loop_daily_cn(self):
        daily_times = [time(7, 0), time(10, 0), time(14, 0), time(18, 0)]
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

    async def _scheduler_second_loop_daily_ai_summary(self):
        daily_times = [time(8, 0)]
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
            logger.info(f"Second: AI News Summary 每日任务将在 {sleep_sec:.0f} 秒后执行")
            await self._safe_sleep(sleep_sec)

            if not self.running:
                break
            if self.is_cn_trading_day():
                await self.run_second_ai_daily_tasks()
                if self._shutdown_after_force_once():
                    break

    async def _scheduler_first_loop_daily_ai_summary(self):
        daily_times = [time(7, 40)]
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
            logger.info(f"First: AI News Summary 每日任务将在 {sleep_sec:.0f} 秒后执行")
            await self._safe_sleep(sleep_sec)

            if not self.running:
                break
            if self.is_cn_trading_day():
                await self.run_first_ai_daily_tasks()
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

    async def _scheduler_news_loop_real_hourly(self):
        daily_times = [time(h, 5) for h in range(7, 23)]
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
            logger.info(f"新闻小时任务将在 {sleep_sec:.0f} 秒后执行")
            await self._safe_sleep(sleep_sec)

            if not self.running:
                break
            await self.run_news_hourly_tasks()
            if self._shutdown_after_force_once():
                break

    async def _scheduler_daily_eastmoney_news(self):
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
            logger.info(f"Eastmoney mews任务将在 {sleep_sec:.0f} 秒后执行")
            await self._safe_sleep(sleep_sec)

            if not self.running:
                break
            await self.update_eastmoney_news()
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
            asyncio.create_task(self._scheduler_first_loop_daily_ai_summary()),
            asyncio.create_task(self._scheduler_second_loop_daily_ai_summary()),
            asyncio.create_task(self._scheduler_news_loop_real_hourly()),
            asyncio.create_task(self._scheduler_daily_eastmoney_news()),
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
    print("是否在中国交易时间:", scheduler.is_cn_trading_day())
