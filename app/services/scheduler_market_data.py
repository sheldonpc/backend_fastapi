import asyncio
import logging
import random
from datetime import datetime, time, timedelta
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import List, Callable, Optional, Dict
from zoneinfo import ZoneInfo
import chinese_calendar as cn_calendar

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.job import Job

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
    CN_5MIN = "cn_5min"
    GLOBAL_5MIN = "global_5min"
    DAILY_CN = "daily_cn"
    HOURLY = "hourly"
    NEWS_HOURLY = "news_hourly"
    AI_FIRST = "ai_first"
    AI_SECOND = "ai_second"
    EASTMONEY = "eastmoney"

    def __lt__(self, other):
        """使枚举支持排序"""
        return self.value < other.value


@dataclass
class ScheduledTask:
    name: str
    func: Callable
    schedule_type: ScheduleType
    times: List[time] = None
    interval: int = None
    require_cn_trading: bool = True
    description: str = ""


# ==== 装饰器 ====
def log_task(name: str):
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


class MarketDataAPScheduler:
    """基于 APScheduler 的市场数据调度器"""

    def __init__(self):
        # 使用更安全的配置
        self.scheduler = AsyncIOScheduler(
            timezone=ZoneInfo("Asia/Shanghai"),
            job_defaults={
                'misfire_grace_time': 300,  # 任务错过执行的宽限期
                'coalesce': True,  # 合并多次错过的执行
                'max_instances': 1  # 同一任务最多1个实例
            }
        )
        self.jobs: Dict[str, Job] = {}
        self.force_run_once = False
        self.running = False
        self.tasks: List[asyncio.Task] = []
        self._scheduled_tasks = self._initialize_tasks()
        self._stop_event = asyncio.Event()

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

    # ==== 保持原有的公共方法接口 ====
    def get_tasks_by_schedule(self, schedule_type: ScheduleType) -> List[ScheduledTask]:
        return [task for task in self._scheduled_tasks if task.schedule_type == schedule_type]

    def get_all_tasks_info(self) -> List[dict]:
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

    def is_cn_trading_day(self) -> bool:
        """保持原有的交易时间判断逻辑"""
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

    # ==== 保持原有的任务方法定义 ====
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

    # ==== APScheduler 配置方法 ====
    def _setup_interval_tasks(self):
        """配置间隔任务"""
        interval_tasks = [
            task for task in self._scheduled_tasks
            if task.interval is not None
        ]

        for task in interval_tasks:
            job_id = f"interval_{task.schedule_type.value}_{task.name}"

            # 使用闭包捕获当前 task 的值
            current_task = task

            async def wrapped_task():
                if not current_task.require_cn_trading or self.is_cn_trading_day():
                    logger.info(f"执行间隔任务: {current_task.name}")
                    await current_task.func()

            try:
                self.jobs[job_id] = self.scheduler.add_job(
                    wrapped_task,
                    IntervalTrigger(seconds=current_task.interval),
                    id=job_id,
                    name=f"{current_task.name} - {current_task.description}",
                    replace_existing=True
                )
                logger.debug(f"已添加间隔任务: {job_id}")
            except Exception as e:
                logger.error(f"添加间隔任务失败 {job_id}: {e}")

    def _setup_cron_tasks(self):
        """配置 Cron 定时任务"""
        # 手动按调度类型分组
        tasks_by_schedule = {}
        for task in self._scheduled_tasks:
            if task.times is not None:
                schedule_type = task.schedule_type
                if schedule_type not in tasks_by_schedule:
                    tasks_by_schedule[schedule_type] = []
                tasks_by_schedule[schedule_type].append(task)

        # 按调度类型处理任务组
        for schedule_type, tasks_list in tasks_by_schedule.items():
            if not tasks_list:
                continue

            # 每个组的所有任务共享相同的时间表
            first_task = tasks_list[0]
            times = first_task.times
            require_cn_trading = first_task.require_cn_trading

            for time_point in times:
                job_id = f"cron_{schedule_type.value}_{time_point.strftime('%H%M')}"

                # 使用闭包捕获当前变量
                current_tasks_list = tasks_list
                current_require_cn_trading = require_cn_trading
                current_schedule_type = schedule_type
                current_time_point = time_point

                async def run_task_group():
                    if not current_require_cn_trading or self.is_cn_trading_day():
                        logger.info(
                            f"执行定时任务组: {current_schedule_type.value} - {current_time_point.strftime('%H:%M')}")
                        for task in current_tasks_list:
                            try:
                                await task.func()
                                await asyncio.sleep(random.uniform(2, 5))
                            except Exception as e:
                                logger.error(f"任务执行失败: {task.name} - {str(e)}")

                try:
                    self.jobs[job_id] = self.scheduler.add_job(
                        run_task_group,
                        CronTrigger(hour=time_point.hour, minute=time_point.minute),
                        id=job_id,
                        name=f"{schedule_type.value} - {time_point.strftime('%H:%M')}",
                        replace_existing=True
                    )
                    logger.debug(f"已添加定时任务: {job_id}")
                except Exception as e:
                    logger.error(f"添加定时任务失败 {job_id}: {e}")

    def _setup_special_tasks(self):
        """配置特殊任务"""
        # 胡润排行榜 - 每年一次
        hurun_task = next((task for task in self._scheduled_tasks if task.name == "胡润排行榜"), None)
        if hurun_task:
            try:
                self.jobs['hurun_yearly'] = self.scheduler.add_job(
                    hurun_task.func,
                    CronTrigger(day=1, month=1, hour=7),
                    id='hurun_yearly',
                    name="胡润排行榜年度更新",
                    replace_existing=True
                )
                logger.debug("已添加胡润排行榜任务")
            except Exception as e:
                logger.error(f"添加胡润排行榜任务失败: {e}")

    def setup_all_schedules(self):
        """配置所有调度任务"""
        logger.info("正在配置 APScheduler 任务...")

        try:
            self._setup_interval_tasks()
            self._setup_cron_tasks()
            self._setup_special_tasks()

            logger.info(f"✅ 已配置 {len(self.jobs)} 个 APScheduler 任务")
        except Exception as e:
            logger.error(f"配置调度任务失败: {e}")
            raise

    # ==== 调度器控制方法 ====
    async def start_scheduler(self, force_run_once: bool = False):
        """启动调度器"""
        if self.running:
            logger.warning("调度器已在运行中")
            return

        self.force_run_once = force_run_once
        self.running = True

        if force_run_once:
            logger.info("force_run_once 模式：立即执行所有任务一次")
            try:
                for task in self._scheduled_tasks:
                    if not task.require_cn_trading or self.is_cn_trading_day():
                        try:
                            await task.func()
                            await asyncio.sleep(1)
                        except Exception as e:
                            logger.error(f"任务执行失败: {task.name} - {str(e)}")
            finally:
                self.running = False
            return

        # 正常启动 APScheduler
        try:
            self.setup_all_schedules()

            if not self.scheduler.running:
                self.scheduler.start()
                logger.info("✅ APScheduler 已启动")

            # 启动保活任务
            self._stop_event.clear()
            self.tasks = [asyncio.create_task(self._keep_alive())]

            logger.info("✅ APScheduler 市场数据调度器启动完成")
            self.print_task_overview()

            # 打印任务状态
            for job_id, job in self.jobs.items():
                if job.next_run_time:
                    logger.info(f"任务: {job.name} -> 下次运行: {job.next_run_time}")
                else:
                    logger.info(f"任务: {job.name} -> 等待调度")

        except Exception as e:
            logger.error(f"启动调度器失败: {e}")
            self.running = False
            raise

    async def _keep_alive(self):
        """保持调度器运行的背景任务"""
        try:
            await self._stop_event.wait()
        except asyncio.CancelledError:
            logger.debug("保活任务被取消")
        except Exception as e:
            logger.error(f"保活任务异常: {e}")

    async def stop_scheduler(self):
        """停止调度器"""
        if not self.running:
            logger.warning("调度器未运行")
            return

        logger.info("正在停止调度器...")
        self.running = False

        try:
            # 先设置停止事件
            self._stop_event.set()

            # 取消保活任务
            for task in self.tasks:
                if not task.done():
                    task.cancel()

            if self.tasks:
                await asyncio.gather(*self.tasks, return_exceptions=True)

            # 停止 APScheduler
            if hasattr(self, 'scheduler') and self.scheduler.running:
                self.scheduler.shutdown(wait=False)

            self.jobs.clear()
            self.tasks.clear()

            logger.info("✅ APScheduler 调度器已停止")

        except Exception as e:
            logger.error(f"停止调度器时发生错误: {e}")
            # 强制清理
            self.jobs.clear()
            self.tasks.clear()
            if hasattr(self, 'scheduler'):
                try:
                    self.scheduler.shutdown(wait=False)
                except:
                    pass

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

    # ==== 新增的管理功能 ====
    def get_job_status(self) -> Dict[str, dict]:
        """获取所有作业状态"""
        status = {}
        for job_id, job in self.jobs.items():
            status[job_id] = {
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'pending': job.pending,
            }
        return status

    def pause_job(self, job_id: str):
        """暂停特定作业"""
        if job_id in self.jobs:
            self.jobs[job_id].pause()
            logger.info(f"已暂停作业: {job_id}")

    def resume_job(self, job_id: str):
        """恢复特定作业"""
        if job_id in self.jobs:
            self.jobs[job_id].resume()
            logger.info(f"已恢复作业: {job_id}")

    def trigger_job(self, job_id: str):
        """立即触发特定作业"""
        if job_id in self.jobs:
            self.jobs[job_id].modify(next_run_time=datetime.now())
            logger.info(f"已触发作业: {job_id}")


# ==== 使用示例和测试 ====
if __name__ == "__main__":
    scheduler = MarketDataAPScheduler()

    # 打印所有任务信息
    print("是否在中国交易时间:", scheduler.is_cn_trading_day())
    print("\n=== 所有定时任务 ===")
    for task_info in scheduler.get_all_tasks_info():
        print(f"{task_info['name']} - {task_info['schedule_type']} - {task_info['times']}")