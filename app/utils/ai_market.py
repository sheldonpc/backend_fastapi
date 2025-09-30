from decimal import Decimal
from typing import Dict, Any
import asyncio
import logging
import aiohttp
import requests
import json

logger = logging.getLogger(__name__)

def calculate_market_temperature(risedown_data: Dict[str, Any]) -> float:
    """
    计算市场温度值（0.0 ~ 100.0）

    Args:
        risedown_data: 包含 MarketUpDownStats 字段的字典

    Returns:
        float: 市场温度，保留1位小数
    """
    # 获取基础数据
    rise_num = risedown_data.get("rise_num", 0)
    fall_num = risedown_data.get("fall_num", 0)
    flat_num = risedown_data.get("flat_num", max(0, 5000 - rise_num - fall_num))
    total = rise_num + fall_num + flat_num
    if total == 0:
        return 0.0

    # 1. 广度得分（0~25）
    breadth = rise_num / total
    breadth_score = min(25.0, max(0.0, breadth * 25 / 0.8))  # 80% 对应 25分

    # 2. 强度得分（涨超6%占比，0~25）
    up_6 = risedown_data.get("up_6", 0)
    strong_ratio = up_6 / total
    strength_score = min(25.0, max(0.0, strong_ratio * 25 / 0.06))  # 6% 对应 25分

    # 3. 赚钱效应得分（涨停/跌停比，0~25）
    limit_up = risedown_data.get("up_10", 0)
    # 估算跌停：用 down_4 * 0.15（可后续替换为 down_10）
    down_4 = risedown_data.get("down_4", 0)
    estimated_limit_down = max(1, int(down_4 * 0.15))
    profit_ratio = limit_up / estimated_limit_down
    profit_score = min(25.0, max(0.0, profit_ratio * 25 / 10))  # 比值10 对应 25分

    # 4. 动能得分（平均涨跌幅，-3% ~ +3% 映射到 0~25）
    avg_rise = float(risedown_data.get("average_rise", Decimal("0.0")))
    # 将 [-3%, +3%] 映射到 [0, 25]，低于 -3% 得0，高于 +3% 得25
    if avg_rise <= -3.0:
        momentum_score = 0.0
    elif avg_rise >= 3.0:
        momentum_score = 25.0
    else:
        momentum_score = (avg_rise + 3.0) * (25.0 / 6.0)

    # 总分
    total_score = breadth_score + strength_score + profit_score + momentum_score
    return round(min(100.0, max(0.0, total_score)), 1)

from app import config
DIFY_KEY = config.API_KEY

async def talk_to_dify(query: str) -> dict:
    """调用 Dify API 并返回完整 JSON 响应"""
    API_KEY = DIFY_KEY
    DIFY_API_URL = "https://api.dify.ai/v1/chat-messages"

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "inputs": {},
        "query": query,
        "response_mode": "blocking",
        "conversation_id": "",
        "user": "user-123"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(DIFY_API_URL, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    return await resp.json()
                logger.error(f"Dify 请求失败: {resp.status}")
        except Exception as e:
            logger.error(f"Dify 请求异常: {e}")
    return None

DIFY_SUMMARY_API_KEY = config.DIFY_SUMMARY_API_KEY


async def dify_summarize(query: str) -> dict:
    """调用 Dify API 并返回完整 JSON 响应"""
    API_KEY = DIFY_SUMMARY_API_KEY
    DIFY_API_URL = "https://api.dify.ai/v1/chat-messages"

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "inputs": {},
        "query": query,
        "response_mode": "blocking",  # 使用阻塞模式
        "conversation_id": "",
        "user": "user-sheldon"
    }

    timeout = aiohttp.ClientTimeout(total=60)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.post(DIFY_API_URL, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    response_data = await resp.json()  # 解析 JSON

                    # 提取需要的数据
                    result = {
                        "answer": response_data.get("answer", ""),  # 主要分析内容
                        "task_id": response_data.get("task_id", ""),
                        "conversation_id": response_data.get("conversation_id", ""),
                        "usage": response_data.get("metadata", {}).get("usage", {})
                    }
                    return result

                else:
                    logger.error(f"dify_summarize 请求失败: {resp.status}")
                    return None

        except asyncio.TimeoutError:
            logger.error("Dify API 请求超时")
        except Exception as e:
            logger.error(f"dify_summarize 请求异常: {e}")
    return None