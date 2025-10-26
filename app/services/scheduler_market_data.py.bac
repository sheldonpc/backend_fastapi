import asyncio
import logging
import random
from datetime import datetime, time, timedelta
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import List, Callable, Optional
from zoneinfo import ZoneInfo
import chinese_calendar as cn_calendar

from app.services.market_data_service import (
    fetch_realtime_market_data, fetch_fx_market_data, fetch_minute_cn_market_data,
    fetch_minute_hk_market_data, fetch_vix_index, fetch_rise_down_index,
    fetch_daily_market_data, fetch_cn_us_bond_market_data, fetch_hurun_rank_market_data,
    fetch_global_market_data, fetch_global_market_data2, fetch_global_market_data3,
    fetch_global_market_data4, fetch_fx_market_history_data, fetch_eastmoney_history_market_data,
    crawl_llm_insight, brief_rise_down_data, news_ai_summary, get_forex_data_async,
    get_industry_data, get_stock_data, get_concept_data, get_and_save_stock_lhb_detail,
    get_and_save_stock_hot_rank, get_and_save_stock_hot_search_baidu, get_and_save_stock_zt_pool,
    get_and_save_stock_zt_pool_previous, get_and_save_stock_zt_pool_strong, get_and_save_stock_zt_pool_down,
    fetch_foreign_commodity_data, get_and_save_all_stock_hot_search_baidu
)

from app.utils.logger import get_logger

logger = get_logger("scheduler_market_data")


# ==== 配置常量 ====
class TradingSession:
    CN_SESSIONS = [(time(9, 30), time(11, 30)), (time(13, 0), time(23, 0))]
    US_SESSIONS = [(time(9, 30), time(17, 0))]


class ScheduleType(Enum):
    CN_5MIN = "cn_5min"  # 中国交易时间5分钟任务
    GLOBAL_5MIN = "global_5min"  # 全球指数5分钟任务
    DAILY_CN = "daily_cn"  # 中国每日任务
    HOURLY = "hourly"  # 小时任务
    NEWS_HOURLY = "news_hourly"  # 新闻小时任务
    AI_FIRST = "ai_first"  # AI早间任务
    AI_SECOND = "ai_second"  # AI总结任务
    EASTMONEY = "eastmoney"  # 东方财富任务


@dataclass
class ScheduledTask:
    """定时任务配置"""
    name: str
    func: Callable
    schedule_type: ScheduleType
    times: List[time] = None  # 执行时间点
    interval: int = None  # 执行间隔(秒)
    require_cn_trading: bool = True  # 是否需要中国交易时间
    description: str = ""  # 任务描述


# ==== 装饰器 ====
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


class MarketDataScheduler:
    """重构后的市场数据调度器"""

    def __init__(self):
        self.running = False
        self.tasks: List[asyncio.Task] = []
        self.force_run_once = False
        self._scheduled_tasks = self._initialize_tasks()

    def _initialize_tasks(self) -> List[ScheduledTask]:
        """初始化所有定时任务配置"""
        return [
            # ==== 5分钟任务 (中国交易时间) ====
            ScheduledTask(
                name="外汇数据",
                func=self.update_fx_market_data,
                schedule_type=ScheduleType.CN_5MIN,
                interval=300,
                description="实时外汇市场数据"
            ),
            ScheduledTask(
                name="期货数据",
                func=self.update_foreign_commodity_data,
                schedule_type=ScheduleType.CN_5MIN,
                interval=300,
                description="外国商品期货数据"
            ),
            ScheduledTask(
                name="VIX指数",
                func=self.update_vix_index,
                schedule_type=ScheduleType.CN_5MIN,
                interval=300,
                description="恐慌指数数据"
            ),
            ScheduledTask(
                name="涨跌数据",
                func=self.update_rise_down_data,
                schedule_type=ScheduleType.CN_5MIN,
                interval=300,
                description="市场涨跌统计数据"
            ),
            ScheduledTask(
                name="涨跌通知",
                func=self.update_notice_rise_down,
                schedule_type=ScheduleType.CN_5MIN,
                interval=300,
                description="涨跌数据简要分析"
            ),

            # ==== 5分钟任务 (全球指数) ====
            ScheduledTask(
                name="全球市场指数",
                func=self.run_update_global_index_data,
                schedule_type=ScheduleType.GLOBAL_5MIN,
                interval=300,
                description="全球主要市场指数数据"
            ),

            # ==== 每日任务 ====
            ScheduledTask(
                name="历史市场数据",
                func=self.update_index_history_data,
                schedule_type=ScheduleType.DAILY_CN,
                times=[time(7, 0), time(10, 0), time(14, 0), time(16, 0), time(18, 0)],
                description="日线级别历史数据"
            ),
            ScheduledTask(
                name="外汇历史数据",
                func=self.update_fx_history_data,
                schedule_type=ScheduleType.DAILY_CN,
                times=[time(7, 0), time(10, 0), time(14, 0), time(16, 0), time(18, 0)],
                description="外汇历史数据"
            ),
            ScheduledTask(
                name="债券数据",
                func=self.update_bond_data,
                schedule_type=ScheduleType.DAILY_CN,
                times=[time(7, 0), time(10, 0), time(14, 0), time(16, 0), time(18, 0)],
                description="中美债券市场数据"
            ),
            ScheduledTask(
                name="行业数据",
                func=self.update_industry_data,
                schedule_type=ScheduleType.DAILY_CN,
                times=[time(7, 0), time(10, 0), time(14, 0), time(16, 0), time(18, 0)],
                description="行业板块数据"
            ),
            ScheduledTask(
                name="个股数据",
                func=self.update_stock_data,
                schedule_type=ScheduleType.DAILY_CN,
                times=[time(7, 0), time(10, 0), time(14, 0), time(16, 0), time(18, 0)],
                description="个股基本信息"
            ),
            ScheduledTask(
                name="概念股",
                func=self.update_concept_data,
                schedule_type=ScheduleType.DAILY_CN,
                times=[time(7, 0), time(10, 0), time(14, 0), time(16, 0), time(18, 0)],
                description="概念板块数据"
            ),
            ScheduledTask(
                name="龙虎榜单",
                func=self.update_lhb_data,
                schedule_type=ScheduleType.DAILY_CN,
                times=[time(7, 0), time(10, 0), time(14, 0), time(16, 0), time(18, 0)],
                description="龙虎榜详细数据"
            ),
            ScheduledTask(
                name="人气榜单",
                func=self.update_hot_rank_data,
                schedule_type=ScheduleType.DAILY_CN,
                times=[time(7, 0), time(10, 0), time(14, 0), time(16, 0), time(18, 0)],
                description="热门股票排名"
            ),
            ScheduledTask(
                name="飙升榜",
                func=self.update_hot_up_data,
                schedule_type=ScheduleType.DAILY_CN,
                times=[time(7, 0), time(10, 0), time(14, 0), time(16, 0), time(18, 0)],
                description="百度搜索飙升榜"
            ),
            ScheduledTask(
                name="百度热搜",
                func=self.update_hot_search_baidu,
                schedule_type=ScheduleType.DAILY_CN,
                times=[time(7, 0), time(10, 0), time(14, 0), time(16, 0), time(18, 0)],
                description="百度股票热搜数据"
            ),
            ScheduledTask(
                name="涨停股池",
                func=self.update_zt_pool,
                schedule_type=ScheduleType.DAILY_CN,
                times=[time(7, 0), time(10, 0), time(14, 0), time(16, 0), time(18, 0)],
                description="当日涨停股票池"
            ),
            ScheduledTask(
                name="昨日涨停股池",
                func=self.update_zt_pool_previous,
                schedule_type=ScheduleType.DAILY_CN,
                times=[time(7, 0), time(10, 0), time(14, 0), time(16, 0), time(18, 0)],
                description="昨日涨停股票池"
            ),
            ScheduledTask(
                name="强势股池",
                func=self.update_zt_pool_strong,
                schedule_type=ScheduleType.DAILY_CN,
                times=[time(7, 0), time(10, 0), time(14, 0), time(16, 0), time(18, 0)],
                description="强势涨停股票池"
            ),
            ScheduledTask(
                name="跌停股池",
                func=self.update_zt_pool_down,
                schedule_type=ScheduleType.DAILY_CN,
                times=[time(7, 0), time(10, 0), time(14, 0), time(16, 0), time(18, 0)],
                description="跌停股票池"
            ),

            # ==== 小时任务 ====
            ScheduledTask(
                name="中国分时数据",
                func=self.update_minute_level_cn_data,
                schedule_type=ScheduleType.HOURLY,
                times=[time(h, 0) for h in range(10, 19)],
                description="中国分钟级别数据"
            ),
            ScheduledTask(
                name="香港分时数据",
                func=self.update_minute_level_hk_data,
                schedule_type=ScheduleType.HOURLY,
                times=[time(h, 0) for h in range(10, 19)],
                description="香港分钟级别数据"
            ),

            # ==== 新闻小时任务 ====
            ScheduledTask(
                name="东方财富新闻",
                func=self.update_eastmoney_news,
                schedule_type=ScheduleType.NEWS_HOURLY,
                times=[time(h, 5) for h in range(7, 23)],
                require_cn_trading=False,
                description="东方财富新闻数据"
            ),
            ScheduledTask(
                name="新闻源1",
                func=self.update_news_one,
                schedule_type=ScheduleType.NEWS_HOURLY,
                times=[time(h, 5) for h in range(7, 23)],
                require_cn_trading=False,
                description="第一个新闻源数据"
            ),
            ScheduledTask(
                name="新闻源2",
                func=self.update_news_two,
                schedule_type=ScheduleType.NEWS_HOURLY,
                times=[time(h, 5) for h in range(7, 23)],
                require_cn_trading=False,
                description="第二个新闻源数据"
            ),
            ScheduledTask(
                name="新闻源3",
                func=self.update_news_three,
                schedule_type=ScheduleType.NEWS_HOURLY,
                times=[time(h, 5) for h in range(7, 23)],
                require_cn_trading=False,
                description="第三个新闻源数据"
            ),
            ScheduledTask(
                name="新闻源4",
                func=self.update_news_four,
                schedule_type=ScheduleType.NEWS_HOURLY,
                times=[time(h, 5) for h in range(7, 23)],
                require_cn_trading=False,
                description="第四个新闻源数据"
            ),

            # ==== AI任务 ====
            ScheduledTask(
                name="AI市场洞察",
                func=self.update_ai_insight,
                schedule_type=ScheduleType.AI_FIRST,
                times=[time(7, 40)],
                description="AI生成的市场洞察分析"
            ),
            ScheduledTask(
                name="AI昨日总结",
                func=self.update_ai_yesterday_summary,
                schedule_type=ScheduleType.AI_SECOND,
                times=[time(8, 0)],
                description="AI生成的昨日市场总结"
            ),

            # ==== 特殊任务 ====
            ScheduledTask(
                name="东方财富日历",
                func=self._run_eastmoney_calendar_tasks,
                schedule_type=ScheduleType.EASTMONEY,
                times=[time(7, 0)],
                require_cn_trading=False,
                description="东方财富新闻和经济日历"
            ),
            ScheduledTask(
                name="胡润排行榜",
                func=self.yearly_update_hurun_rank,
                schedule_type=ScheduleType.DAILY_CN,
                times=[time(7, 0)],
                description="胡润富豪排行榜数据(年度)"
            ),
        ]

    def get_tasks_by_schedule(self, schedule_type: ScheduleType) -> List[ScheduledTask]:
        """根据调度类型获取任务"""
        return [task for task in self._scheduled_tasks if task.schedule_type == schedule_type]

    def get_all_tasks_info(self) -> List[dict]:
        """获取所有任务的详细信息，用于监控和管理"""
        tasks_info = []
        for task in self._scheduled_tasks:
            info = {
                'name': task.name,
                'schedule_type': task.schedule_type.value,
                'times': [t.strftime('%H:%M') for t in task.times] if task.times else f"每{task.interval}秒",
                'require_cn_trading': task.require_cn_trading,
                'description': task.description,
                'enabled': True
            }
            tasks_info.append(info)
        return tasks_info

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
        return any(start <= now.time() < end for start, end in TradingSession.CN_SESSIONS)

    def is_usa_trading_time(self) -> bool:
        now = datetime.now(ZoneInfo("America/New_York"))
        return now.weekday() < 5 and any(start <= now.time() < end for start, end in TradingSession.US_SESSIONS)

    # ==== 任务方法定义 ====
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

    @log_task("AI市场洞察")
    async def update_ai_insight(self):
        await crawl_llm_insight()

    @log_task("涨跌通知")
    async def update_notice_rise_down(self):
        await brief_rise_down_data()

    @log_task("胡润排行榜")
    async def yearly_update_hurun_rank(self):
        await fetch_hurun_rank_market_data()

    @log_task("AI昨日总结")
    async def update_ai_yesterday_summary(self):
        await news_ai_summary()

    async def _run_eastmoney_calendar_tasks(self):
        """东方财富相关任务组合"""
        await self.update_eastmoney_news()
        await asyncio.sleep(5)
        await self.update_global_calendar()

    # ==== 通用的任务运行方法 ====
    async def _run_task_group(self, tasks: List[ScheduledTask]):
        """运行一组任务"""
        for task in tasks:
            try:
                # 检查交易时间要求
                if task.require_cn_trading and not self.is_cn_trading_day():
                    continue

                await task.func()
                sleep_time = random.uniform(5, 10)
                await asyncio.sleep(sleep_time)
            except Exception as e:
                logger.error(f"任务执行失败: {task.name} - {str(e)}")

    async def _run_interval_tasks(self, tasks: List[ScheduledTask]):
        """运行间隔任务"""
        while self.running:
            await self._run_task_group(tasks)
            if self._shutdown_after_force_once():
                break
            await self._safe_sleep(tasks[0].interval if tasks else 300)

    async def _run_scheduled_tasks(self, tasks: List[ScheduledTask]):
        """运行定时任务"""
        if not tasks:
            return

        times = tasks[0].times  # 所有任务共享相同的时间表
        require_cn_trading = tasks[0].require_cn_trading

        while self.running:
            now = datetime.now(ZoneInfo("Asia/Shanghai"))
            today = now.date()

            # 计算下一个执行时间
            next_run = min(
                (datetime.combine(today, t, tzinfo=ZoneInfo("Asia/Shanghai"))
                 for t in times
                 if datetime.combine(today, t, tzinfo=ZoneInfo("Asia/Shanghai")) > now),
                default=datetime.combine(today + timedelta(days=1), times[0], tzinfo=ZoneInfo("Asia/Shanghai"))
            )

            sleep_sec = (next_run - now).total_seconds()
            logger.info(f"{tasks[0].schedule_type.value} 任务将在 {sleep_sec:.0f} 秒后执行")
            await self._safe_sleep(sleep_sec)

            if not self.running:
                break

            # 检查交易时间条件
            if require_cn_trading and not self.is_cn_trading_day():
                continue

            await self._run_task_group(tasks)
            if self._shutdown_after_force_once():
                break

    # ==== 调度循环 ====
    async def _scheduler_loop_5min_cn(self):
        """中国交易时间5分钟任务"""
        tasks = self.get_tasks_by_schedule(ScheduleType.CN_5MIN)
        await self._run_interval_tasks(tasks)

    async def _scheduler_loop_5min_global(self):
        """全球指数5分钟任务"""
        tasks = self.get_tasks_by_schedule(ScheduleType.GLOBAL_5MIN)
        await self._run_interval_tasks(tasks)

    async def _scheduler_loop_daily_cn(self):
        """中国每日任务"""
        tasks = self.get_tasks_by_schedule(ScheduleType.DAILY_CN)
        await self._run_scheduled_tasks(tasks)

    async def _scheduler_loop_hourly(self):
        """小时任务"""
        tasks = self.get_tasks_by_schedule(ScheduleType.HOURLY)
        await self._run_scheduled_tasks(tasks)

    async def _scheduler_news_loop_hourly(self):
        """新闻小时任务"""
        tasks = self.get_tasks_by_schedule(ScheduleType.NEWS_HOURLY)
        await self._run_scheduled_tasks(tasks)

    async def _scheduler_ai_first(self):
        """AI早间任务"""
        tasks = self.get_tasks_by_schedule(ScheduleType.AI_FIRST)
        await self._run_scheduled_tasks(tasks)

    async def _scheduler_ai_second(self):
        """AI总结任务"""
        tasks = self.get_tasks_by_schedule(ScheduleType.AI_SECOND)
        await self._run_scheduled_tasks(tasks)

    async def _scheduler_eastmoney(self):
        """东方财富任务"""
        tasks = self.get_tasks_by_schedule(ScheduleType.EASTMONEY)
        await self._run_scheduled_tasks(tasks)

    # ==== 工具方法 ====
    def _shutdown_after_force_once(self):
        """当 force_run_once 启用时，运行一次后关闭"""
        if self.force_run_once:
            logger.info("force_run_once 模式：任务已执行一次，调度器即将退出")
            self.running = False
            return True
        return False

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

        # 打印任务概览
        self.print_task_overview()

        self.tasks = [
            asyncio.create_task(self._scheduler_loop_5min_cn()),
            asyncio.create_task(self._scheduler_loop_5min_global()),
            asyncio.create_task(self._scheduler_loop_daily_cn()),
            asyncio.create_task(self._scheduler_loop_hourly()),
            asyncio.create_task(self._scheduler_news_loop_hourly()),
            asyncio.create_task(self._scheduler_ai_first()),
            asyncio.create_task(self._scheduler_ai_second()),
            asyncio.create_task(self._scheduler_eastmoney()),
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

    def print_task_overview(self):
        """打印任务概览"""
        logger.info("=== 定时任务概览 ===")
        for schedule_type in ScheduleType:
            tasks = self.get_tasks_by_schedule(schedule_type)
            if tasks:
                logger.info(f"\n📋 {schedule_type.value} 任务组 ({len(tasks)}个任务):")
                for task in tasks:
                    time_info = f"时间: {[t.strftime('%H:%M') for t in task.times]}" if task.times else f"间隔: {task.interval}秒"
                    trading_info = "需交易时间" if task.require_cn_trading else "全天运行"
                    logger.info(f"  • {task.name}: {time_info} | {trading_info}")


# ==== 使用示例和测试 ====
if __name__ == "__main__":
    scheduler = MarketDataScheduler()

    # 打印所有任务信息
    print("是否在中国交易时间:", scheduler.is_cn_trading_day())
    print("\n=== 所有定时任务 ===")
    for task_info in scheduler.get_all_tasks_info():
        print(f"{task_info['name']} - {task_info['schedule_type']} - {task_info['times']}")
