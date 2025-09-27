import asyncio
import logging
from datetime import datetime, time, timezone, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

import requests

from app.services.market_data_service import fetch_realtime_market_data, fetch_realtime_usa_market_data, \
    fetch_fx_market_data, fetch_stock_hot_follow_market_data, fetch_minute_cn_market_data, fetch_minute_usa_market_data, \
    fetch_vix_index, fetch_rise_down_index, fetch_daily_market_data, \
    fetch_cn_us_bond_market_data, fetch_hurun_rank_market_data, fetch_global_market_data, \
    fetch_eastmoney_history_news_market_data, fetch_fx_market_history_data, fetch_oil_data, fetch_gold_data, \
    fetch_silver_data


class NewMarketScheduler:
    """市场数据定时调度器"""
    def __init__(self):
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.force_run_once = False

    def is_cn_trading_time(self):
        cn_time = datetime.now(ZoneInfo("Asia/Shanghai"))
        if cn_time.weekday() >= 5:  # 5=周六, 6=周日
            return False
        elif cn_time.time() >= time(9, 00) and cn_time.time() <= time(16, 0):
            return True
        else:
            return False

    def is_usa_trading_time(self):
        usa_time = datetime.now(ZoneInfo("America/New_York"))
        if usa_time.weekday() >= 5:  # 5=周六, 6=周日
            return False
        elif usa_time.time() >= time(9, 00) and usa_time.time() <= time(16, 0):
            return True
        else:
            return False

    async def run_update_cn_data(self):
        # fetch_realtime_market_data()
        logging.info("开始更新中国市场数据")
        try:
            data = await fetch_realtime_market_data()
            logging.info("success: 中国市场数据更新成功")
        except Exception as e:
            logging.error(f"error: 中国市场数据更新失败: {e}")


    async def run_update_usa_data(self):
        logging.info("开始更新美国市场数据")
        try:
            data = await fetch_realtime_usa_market_data()
            logging.info("success: 美国市场数据更新成功")
        except Exception as e:
            logging.error(f"error: 美国市场数据更新失败: {e}")

    async def fetch_fx_market_data(self):
        logging.info("开始更新外汇数据")
        try:
            data = await fetch_fx_market_data()
            logging.info("success: 外汇数据更新成功")
        except Exception as e:
            logging.error(f"error: 外汇数据更新失败: {e}")

    async def update_hot_stock(self):
        logging.info("开始更新热门股票数据")
        try:
            data = await fetch_stock_hot_follow_market_data()
            logging.info("success: 外汇数据更新成功")
        except Exception as e:
            logging.error(f"error: 外汇数据更新失败: {e}")

    # 接口有问题
    async def update_minute_level_cn_data(self):
        logging.info("开始更新中国分时数据")
        try:
            data = await fetch_minute_cn_market_data()
            logging.info("success: 中国分时数据更新成功")
        except Exception as e:
            logging.error(f"error: 中国分时数据更新失败: {e}")

    async def update_minute_level_usa_data(self):
        logging.info("开始更新美国分时数据")
        try:
            data = await fetch_minute_usa_market_data()
            logging.info("success: 美国分时数据更新成功")
        except Exception as e:
            logging.error(f"error: 美国分时数据更新失败: {e}")

    async def update_oil_data(self):
        logging.info("开始更新贵金属数据")
        try:
            data = await fetch_oil_data()
            logging.info("success: 贵金属数据更新成功")
        except Exception as e:
            logging.error(f"error: 贵金属数据更新失败: {e}")

    async def update_gold_data(self):
        logging.info("开始更新贵金属数据")
        try:
            data = await fetch_gold_data()
            logging.info("success: 贵金属数据更新成功")
        except Exception as e:
            logging.error(f"error: 贵金属数据更新失败: {e}")

    async def update_silver_data(self):
        logging.info("开始更新贵金属数据")
        try:
            data = await fetch_silver_data()
            logging.info("success: 贵金属数据更新成功")
        except Exception as e:
            logging.error(f"error: 贵金属数据更新失败: {e}")

    async def update_vix_index(self):
        logging.info("开始更新VIX指数数据")
        try:
            # fetch_vix_index
            data = await fetch_vix_index()
            logging.info("success: VIX指数数据更新成功")
        except Exception as e:
            logging.error(f"error: VIX指数数据更新失败: {e}")

    async def update_rise_down_data(self):
        logging.info("开始更新涨跌数据")
        try:
            data = await fetch_rise_down_index()
            logging.info("success: 涨跌数据更新成功")
        except Exception as e:
            logging.error(f"error: 涨跌数据更新失败: {e}")

    # 获取历史数据 sz399001, sh000001, sz399006, hsi, SP500, NASDAQ, DJ, gold, silver, Pt
    async def update_index_history_data(self):
        logging.info("开始更新历史数据")
        try:
            data = await fetch_daily_market_data()
            logging.info("success: 历史数据更新成功")
        except Exception as e:
            logging.error(f"error: 历史数据更新失败: {e}")

    async def update_fx_history_data(self):
        logging.info("开始更新外汇历史数据")
        try:
            data = await fetch_fx_market_history_data()
            logging.info("success:外汇历史数据更新成功")
        except Exception as e:
            logging.error(f"error:外汇历史数据更新失败: {e}")

    async def update_bond_data(self):
        logging.info("开始更新债券数据")
        try:
            data = await fetch_cn_us_bond_market_data()
            logging.info("success: 债券数据更新成功")
        except Exception as e:
            logging.error(f"error: 债券数据更新失败: {e}")

    async def update_global_news(self):
        logging.info("开始更新全球新闻数据")
        try:
            data = await fetch_global_market_data()
            logging.info("success: 全球新闻数据更新成功")
        except Exception as e:
            logging.error(f"error: 全球新闻数据更新失败: {e}")

    async def update_eastmoney_news(self):
        logging.info("开始更新东方财富新闻数据")
        try:
            data = await fetch_eastmoney_history_news_market_data()
            logging.info("success: 东方财富新闻数据更新成功")
        except Exception as e:
            logging.error(f"error: 东方财富新闻数据更新失败: {e}")

    async def yearly_update_huren_rank(self):
        logging.info("开始更新胡润排名数据")
        try:
            data = await fetch_hurun_rank_market_data()
            logging.info("success:胡润排名数据更新成功")
        except Exception as e:
            logging.error(f"error:胡润排名数据更新失败: {e}")


if __name__ == "__main__":
    scheduler = NewMarketScheduler()
    print(scheduler.is_cn_trading_time())