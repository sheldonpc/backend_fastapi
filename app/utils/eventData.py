import asyncio
import aiohttp
import random
import time
from fake_useragent import UserAgent
from lxml import etree
import json
from typing import List, Dict, Optional
import logging
import datetime  # 添加缺失的datetime导入

# 配置日志
from app.utils.logger import get_logger

logger = get_logger("eventData")

class EventDataScraper:
    def __init__(self):
        self.session = None
        self.ua = UserAgent()
        self.base_url = "https://forex.eastmoney.com/FC.html"

    async def __aenter__(self):
        """异步上下文管理器入口"""
        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5, ssl=False)  # 修复：使用ssl参数
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers=self._get_headers()
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.session:
            await self.session.close()

    def _get_headers(self) -> Dict[str, str]:
        """生成随机请求头"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }

    async def _random_delay(self, min_delay: float = 1, max_delay: float = 3):
        """随机延迟，避免请求过于频繁"""
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)

    def _get_cookies(self) -> Dict[str, str]:
        """生成随机cookies"""
        return {
            'Hm_lvt_:': str(int(time.time())),
            'Hm_lpvt_:': str(int(time.time())),
            'v': str(random.randint(100000, 999999))
        }

    async def fetch_page(self, url: str, retries: int = 3) -> Optional[str]:
        """获取页面内容，带有重试机制"""
        for attempt in range(retries):
            try:
                await self._random_delay(1, 2)

                headers = self._get_headers()
                cookies = self._get_cookies()

                async with self.session.get(
                        url,
                        headers=headers,
                        cookies=cookies,
                        proxy=None  # 如果需要代理可以在这里设置
                ) as response:

                    if response.status == 200:
                        html = await response.text()
                        logger.info(f"成功获取页面，长度: {len(html)}")
                        return html
                    elif response.status == 403:
                        logger.warning(f"被服务器拒绝访问，状态码: {response.status}")
                        await asyncio.sleep(5)  # 被拒绝时等待更长时间
                    else:
                        logger.warning(f"请求失败，状态码: {response.status}, 尝试次数: {attempt + 1}")

            except aiohttp.ClientError as e:
                logger.error(f"网络请求错误: {e}, 尝试次数: {attempt + 1}")
            except asyncio.TimeoutError:
                logger.error(f"请求超时, 尝试次数: {attempt + 1}")

            # 重试前等待
            if attempt < retries - 1:
                wait_time = (attempt + 1) * 5
                logger.info(f"等待 {wait_time} 秒后重试...")
                await asyncio.sleep(wait_time)

        logger.error(f"获取页面失败，已重试 {retries} 次")
        return None

    def parse_forex_data(self, html: str) -> List[Dict[str, str]]:
        """解析外汇数据"""
        if not html:
            return []

        try:
            html_obj = etree.HTML(html)
            data = html_obj.xpath('//*[@id="tbody"]/tr')

            results = []
            for tr in data:
                try:
                    date = tr.xpath('./td[2]/text()')
                    time = tr.xpath('./td[3]/text()')
                    region = tr.xpath('./td[4]/text()')
                    name = tr.xpath('./td[5]/@title')
                    pre_value = tr.xpath('./td[9]/text()')
                    importance = tr.xpath('./td[10]/font/text()')

                    # 确保数据存在
                    if date and time:
                        datetime_str = f"{date[0]} {time[0]}"

                        result = {
                            'datetime': datetime_str,
                            'region': region[0] if region else '',
                            'name': name[0] if name else '',
                            'previous_value': pre_value[0] if pre_value else '',
                            'importance': importance[0] if importance else '',
                            'scraped_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        results.append(result)

                except Exception as e:
                    logger.error(f"解析单条数据时出错: {e}")
                    continue

            logger.info(f"成功解析 {len(results)} 条数据")
            return results

        except Exception as e:
            logger.error(f"解析HTML时出错: {e}")
            return []

    async def get_forex_data(self, save_html: bool = False) -> List[Dict[str, str]]:
        """获取外汇数据的主函数"""
        logger.info("开始获取外汇数据...")

        html = await self.fetch_page(self.base_url)
        if not html:
            return []

        # 可选：保存HTML文件
        if save_html:
            try:
                with open("getWeb.html", "w", encoding="utf-8") as f:
                    f.write(html)
                logger.info("HTML文件已保存")
            except Exception as e:
                logger.error(f"保存HTML文件时出错: {e}")

        # 解析数据
        data = self.parse_forex_data(html)
        return data

    async def save_to_json(self, data: List[Dict[str, str]], filename: str = "forex_data.json"):
        """保存数据到JSON文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"数据已保存到 {filename}")
        except Exception as e:
            logger.error(f"保存JSON文件时出错: {e}")


# 使用示例
async def main():
    """主函数示例"""
    async with EventDataScraper() as scraper:
        # 获取数据并保存HTML
        forex_data = await scraper.get_forex_data(save_html=True)

        # 打印结果
        for i, item in enumerate(forex_data[:5]):  # 只显示前5条
            print(f"数据 {i + 1}: {item}")

        # 保存到JSON
        # await scraper.save_to_json(forex_data)

        return forex_data


if __name__ == "__main__":
    # 运行示例
    data = asyncio.run(main())
    print(f"总共获取到 {len(data)} 条数据")