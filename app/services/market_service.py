import asyncio
import os
import random
import time
import json
import sys
import logging
from decimal import Decimal
from typing import Dict
from datetime import datetime, timezone, timedelta
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from app.config import FINANCIAL_TARGETS, CHROMEDRIVER_PATH, CRAWLER_HEADLESS, CRAWLER_INTERVAL_SECONDS
from app.models import IndexData, FinancialNews

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# ==================== 配置区 ====================
INTERVAL_SECONDS = 300  # 抓取间隔，单位：秒（300 = 5分钟）
# 定义北京时区
BEIJING_TZ = timezone(timedelta(hours=8))
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

class FinancialDataCrawler:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self.driver_path = self._find_chromedriver()
        self.targets = self._load_targets()

    def _load_targets(self):
        if FINANCIAL_TARGETS:
            logger.info(f"从配置加载{len(FINANCIAL_TARGETS)}个数据源")
            return FINANCIAL_TARGETS
        else:
            logger.warning("没有找到金融数据源配置")
            raise Exception("没有找到金融数据源配置")

    def _find_chromedriver(self):
        if os.path.exists(CHROMEDRIVER_PATH):
            logger.info(f"使用配置的ChromeDriver路径: {CHROMEDRIVER_PATH}")
            return CHROMEDRIVER_PATH

        # 然后查找其他可能的路径
        possible_paths = [
            os.path.join(os.getcwd(), "chromedriver.exe"),
            os.path.join(os.path.dirname(__file__), "chromedriver.exe"),
            "chromedriver.exe",  # 系统PATH中
        ]

        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"使用自动查找的ChromeDriver路径: {path}")
                return path

        raise FileNotFoundError("没有找到ChromeDriver")

    def _setup_driver(self):
        try:
            options = Options()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

            service = Service(self.driver_path)
            self.driver = Chrome(service=service, options=options)
            logger.info("已创建ChromeDriver实例")
        except Exception as e:
            logger.error(f"创建ChromeDriver实例时出错: {e}")
            raise

    def _safe_text(self, element):
        return element.text.strip() if element else "N/A"

    # def _parse_decimal(self, value):
    #     if not value or value == "N/A":
    #         return None
    #
    #     try:
    #         import re
    #         # 修复正则表达式，支持负号
    #         cleaned = re.sub(r'[^\d.-]', '', str(value))
    #         if cleaned:
    #             return Decimal(cleaned)
    #     except Exception as e:
    #         logger.warning(f"解析数字时出错: {value} - {e}")
    #
    #     return None

    def _parse_decimal(self, value):
        if not value or value == "N/A":
            return None

        try:
            import re
            # 处理包含括号的格式，如 "-171.50(-0.37%)"
            # 提取第一个数字部分（括号前的部分）
            if '(' in str(value):
                # 分割并取第一部分
                value = str(value).split('(')[0]

            # 清理字符串，只保留数字、小数点和负号
            cleaned = re.sub(r'[^\d.-]', '', str(value))

            # 确保只有一个负号且在开头，防止多个负号
            if cleaned.count('-') > 1:
                # 如果有多个负号，只保留第一个
                if cleaned.startswith('-'):
                    cleaned = '-' + cleaned.replace('-', '')
                else:
                    cleaned = cleaned.replace('-', '')

            # 确保只有一个小数点
            if cleaned.count('.') > 1:
                # 如果有多个小数点，只保留第一个
                parts = cleaned.split('.')
                cleaned = parts[0] + '.' + ''.join(parts[1:])

            if cleaned and cleaned not in ['-', '.', '-.']:
                return Decimal(cleaned)
        except Exception as e:
            logger.warning(f"解析数字时出错: {value} - {type(e).__name__}: {e}")

        return None

    def _parse_change_with_percent(self, value):
        """
        解析包含涨跌额和百分比的数据
        例如: "-171.50(-0.37%)" -> (Decimal('-171.50'), '-0.37%')
        """
        if not value or value == "N/A":
            return None, None

        try:
            import re
            value_str = str(value).strip()

            # 检查是否包含括号
            if '(' in value_str and ')' in value_str:
                # 提取括号前的数字部分（涨跌额）
                change_part = value_str.split('(')[0].strip()

                # 提取括号内的百分比部分
                percent_match = re.search(r'\(([^)]+)\)', value_str)
                percent_part = percent_match.group(1) if percent_match else None

                # 解析涨跌额
                change_decimal = self._parse_decimal(change_part)

                return change_decimal, percent_part
            else:
                # 如果没有括号，只有一个数字
                change_decimal = self._parse_decimal(value_str)
                return change_decimal, None

        except Exception as e:
            logger.warning(f"解析涨跌数据时出错: {value} - {type(e).__name__}: {e}")
            return None, None

    def _extract_us_index_data(self) -> Dict:
        """提取美股指数数据"""
        try:
            price = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="hqPrice"]'))
            )
            change = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="hqSummary"]/div[3]/div[1]'))
            )
            hqTime = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="hqSummary"]/div[3]/div[2]'))
            )

            # //*[@id="hqDetails"]/table/tbody/tr/td[1]
            open_today = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="hqDetails"]/table/tbody/tr/td[1]'))
            )

            amount = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="hqDetails"]/table/tbody/tr/td[2]'))
            )

            range_change = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="hqDetails"]/table/tbody/tr/td[3]'))
            )

            highest = self._safe_text(range_change).split("-")[0]
            lowest = self._safe_text(range_change).split("-")[1]

            close_yesterday = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="hqDetails"]/table/tbody/tr/td[4]'))
            )

            # 解析包含百分比的涨跌数据
            change_text = self._safe_text(change)
            change_amount, change_percent = self._parse_change_with_percent(change_text)

            return {
                "price": self._safe_text(price),
                "change": str(change_amount) if change_amount else "N/A",
                "change_percent": change_percent if change_percent else "N/A",
                "time": self._safe_text(hqTime),
                "open_today": self._safe_text(open_today),
                "close_yesterday": self._safe_text(close_yesterday),
                "highest": highest,
                "lowest": lowest,
                "volume": "N/A",
                "amount": self._safe_text(amount),
            }
        except Exception as e:
            raise Exception(f"提取美股数据失败: {e}")

    def _extract_a_share_data(self) -> Dict:
        """提取A股/指数的完整行情数据"""
        try:
            # 主价格信息
            price_elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="price"]'))
            )
            change_elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="change"]'))
            )
            changeP_elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="changeP"]'))
            )
            hqTime_elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="hqTime"]'))
            )

            # 详细行情表格
            open_today_elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="hqDetails"]/table/tbody/tr[1]/td[1]'))
            )
            close_yesterday_elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="hqDetails"]/table/tbody/tr[2]/td[1]'))
            )
            highest_elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="hqDetails"]/table/tbody/tr[1]/td[2]'))
            )
            lowest_elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="hqDetails"]/table/tbody/tr[2]/td[2]'))
            )
            volume_elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="hqDetails"]/table/tbody/tr[3]/td[1]'))
            )
            amount_elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="hqDetails"]/table/tbody/tr[4]/td[1]'))
            )

            return {
                "price": self._safe_text(price_elem),
                "change": self._safe_text(change_elem),
                "change_percent": self._safe_text(changeP_elem),
                "time": self._safe_text(hqTime_elem),
                "open_today": self._safe_text(open_today_elem),
                "close_yesterday": self._safe_text(close_yesterday_elem),
                "highest": self._safe_text(highest_elem),
                "lowest": self._safe_text(lowest_elem),
                "volume": self._safe_text(volume_elem),
                "amount": self._safe_text(amount_elem),
            }
        except Exception as e:
            raise Exception(f"提取A股数据失败: {e}")

    # def _extract_us_index_data(self) -> Dict:
    #     """提取美股指数数据"""
    #     try:
    #         price = WebDriverWait(self.driver, 10).until(
    #             EC.presence_of_element_located((By.XPATH, '//*[@id="hqPrice"]'))
    #         )
    #         change = WebDriverWait(self.driver, 10).until(
    #             EC.presence_of_element_located((By.XPATH, '//*[@id="hqSummary"]/div[3]/div[1]'))
    #         )
    #         hqTime = WebDriverWait(self.driver, 10).until(
    #             EC.presence_of_element_located((By.XPATH, '//*[@id="hqSummary"]/div[3]/div[2]'))
    #         )
    #
    #         return {
    #             "price": self._safe_text(price),
    #             "change": self._safe_text(change),
    #             "change_percent": "N/A",
    #             "time": self._safe_text(hqTime),
    #             "open_today": "N/A",
    #             "close_yesterday": "N/A",
    #             "highest": "N/A",
    #             "lowest": "N/A",
    #             "volume": "N/A",
    #             "amount": "N/A",
    #         }
    #     except Exception as e:
    #         raise Exception(f"提取美股数据失败: {e}")

    def _extract_futures_data(self) -> Dict:
        """提取期货数据"""
        try:
            price = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="table-box-futures-hq"]/tbody/tr[1]/td[1]/div/span[1]')
                )
            )
            change = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="table-box-futures-hq"]/tbody/tr[1]/td[1]/div/p/span[1]')
                )
            )
            changeP = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="table-box-futures-hq"]/tbody/tr[1]/td[1]/div/p/span[2]')
                )
            )
            hqTime = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="table-box-futures-hq"]/tbody/tr[1]/td[1]/p')
                )
            )

            open_today = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="table-box-futures-hq"]/tbody/tr[1]/td[3]')
                )
            )

            highest = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="table-box-futures-hq"]/tbody/tr[1]/td[4]')
                )
            )

            lowest = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="table-box-futures-hq"]/tbody/tr[1]/td[5]')
                )
            )



            return {
                "price": self._safe_text(price),
                "change": self._safe_text(change),
                "change_percent": self._safe_text(changeP),
                "time": self._safe_text(hqTime).strip(),
                "open_today": self._safe_text(open_today),
                "close_yesterday": "N/A",
                "highest": self._safe_text(highest),
                "lowest": self._safe_text(lowest),
                "volume": "N/A",
                "amount": "N/A",
            }
        except Exception as e:
            raise Exception(f"提取期货数据失败: {e}")

    async def fetch_single_target(self, target: Dict) -> Dict:
        """抓取单个目标"""
        name = target["name"]
        url = target["url"]
        data_type = target["type"]

        logger.info(f"抓取 {target['display_name']} ({name})...")

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.driver.get, url)
            sleep_time = random.uniform(1, 5)
            await asyncio.sleep(sleep_time)

            # 根据类型提取数据
            if data_type == "a_share":
                data = await loop.run_in_executor(None, self._extract_a_share_data)
            elif data_type == "us_index":
                data = await loop.run_in_executor(None, self._extract_us_index_data)
            elif data_type == "futures":
                data = await loop.run_in_executor(None, self._extract_futures_data)
            else:
                data = {"error": "未知类型"}

            # 添加目标元信息
            result = {
                "timestamp": datetime.now(BEIJING_TZ).strftime("%Y-%m-%d %H:%M:%S"),
                # "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "display_name": target["display_name"],
                "data_type": target["data_type"],
                "market_region": target["market_region"],
                **data
            }

            logger.info(f"✅ {name} 数据获取成功")
            return result
        except Exception as e:
            logger.error(f"❌ {name} 抓取失败: {e}")
            return {
                # "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": datetime.now(BEIJING_TZ).strftime("%Y-%m-%d %H:%M:%S"),
                "display_name": target["display_name"],
                "data_type": target["data_type"],
                "market_region": target["market_region"],
                "error": str(e),
                "price": "N/A",
                "change": "N/A",
                "change_percent": "N/A",
                "time": "N/A",
                "open_today": "N/A",
                "close_yesterday": "N/A",
                "highest": "N/A",
                "lowest": "N/A",
                "volume": "N/A",
                "amount": "N/A",
            }

    async def fetch_all_markets(self) -> Dict[str, Dict]:
        """抓取所有市场"""
        self._setup_driver()

        logger.info("开始批量获取金融数据...")
        results = {}

        for target in self.targets:
            result = await self.fetch_single_target(target)
            results[target["name"]] = result

            await asyncio.sleep(random.uniform(1, 5))

        logger.info(f"数据抓取完成，获取到{len(results)}条数据")
        return results

    async def save_to_database(self, results: Dict[str, Dict]) -> int:
        if not IndexData:
            logger.warning("IndexData模型未导入，跳过数据库保存")
            return 0

        saved_count = 0

        for symbol, data in results.items():
            try:
                if "error" in data:
                    logger.warning(f"跳过错误数据: {symbol}")
                    continue

                # 解析数据
                # parsed_data = {
                #     "name": data.get("display_name", symbol),
                #     "timestamp": datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S"),
                #     "price": self._parse_decimal(data.get("price")),
                #     "change": self._parse_decimal(data.get("change")),
                #     "change_percent": data.get("change_percent"),
                #     "open_today": self._parse_decimal(data.get("open_today")),
                #     "close_yesterday": self._parse_decimal(data.get("close_yesterday")),
                #     "highest": self._parse_decimal(data.get("highest")),
                #     "lowest": self._parse_decimal(data.get("lowest")),
                #     "volume": data.get("volume") if data.get("volume") != "N/A" else None,
                #     "amount": data.get("amount") if data.get("amount") != "N/A" else None,
                #     "data_type": data.get("data_type", "unknown"),
                #     "market_region": data.get("market_region", "Unknown")
                # }

                # 解析数据
                parsed_data = {
                    "name": data.get("display_name", symbol),
                    # "timestamp": datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S"),
                    "timestamp": datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=BEIJING_TZ),
                    "price": self._parse_decimal(data.get("price")),
                    "change": self._parse_decimal(data.get("change")),
                    "change_percent": data.get("change_percent"),
                    "open_today": self._parse_decimal(data.get("open_today")),
                    "close_yesterday": self._parse_decimal(data.get("close_yesterday")),
                    "highest": self._parse_decimal(data.get("highest")),
                    "lowest": self._parse_decimal(data.get("lowest")),
                    "volume": data.get("volume") if data.get("volume") != "N/A" else None,
                    "amount": data.get("amount") if data.get("amount") != "N/A" else None,
                    "data_type": data.get("data_type", "unknown"),
                    "market_region": data.get("market_region", "Unknown")
                }

                # 确保price不为None
                if parsed_data["price"] is None:
                    logger.warning(f"跳过无效价格数据: {symbol}")
                    continue

                await IndexData.update_or_create(
                    symbol=symbol,
                    defaults=parsed_data
                )
                saved_count += 1
                logger.info(f"数据保存成功: {symbol}")

            except Exception as e:
                logger.error(f"数据保存失败: {symbol} - {e}")
        return saved_count

    def save_to_file(self, results: Dict[str, Dict]) -> str:
        """保存结果到JSON文件"""
        timestamp_str = datetime.now(BEIJING_TZ).strftime("%Y%m%d_%H%M%S")
        filename = f"market_data_{timestamp_str}.json"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 数据已保存至: {filename}")
            return filename
        except Exception as e:
            logger.error(f"保存文件失败: {e}")
            return ""

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            logger.info("浏览器已关闭")


# ==================== 主要服务类 ====================
class MarketDataService:
    """市场数据服务 - FastAPI集成接口"""

    def __init__(self):
        self.crawler = None

    async def update_all_market_data(self) -> Dict:
        """更新所有市场数据"""
        try:
            # 初始化爬虫
            self.crawler = FinancialDataCrawler(headless=True)

            # 获取数据
            results = await self.crawler.fetch_all_markets()

            # 保存到数据库
            saved_count = await self.crawler.save_to_database(results)

            # 保存JSON文件（备份）
            backup_file = self.crawler.save_to_file(results)

            return {
                "success": True,
                "total_targets": len(self.crawler.targets),
                "successful_crawls": len([r for r in results.values() if "error" not in r]),
                "saved_to_db": saved_count,
                "backup_file": backup_file,
                "results": results
            }

        except Exception as e:
            logger.error(f"更新市场数据失败: {e}")
            return {"success": False, "error": str(e)}

        finally:
            if self.crawler:
                self.crawler.close()

    async def get_latest_data(self) -> Dict:
        """获取最新的数据库数据"""
        if not IndexData:
            return {"error": "数据库模型未导入"}

        try:
            # 获取最新的10条数据，按更新时间倒序
            latest_data = await IndexData.all().order_by("-updated_at").limit(10)

            result = {
                "cn_indices": [],
                "us_indices": [],
                "precious_metals": [],
                "total_count": len(latest_data),
                "query_limit": 10  # 添加查询限制信息
            }

            for item in latest_data:
                item_info = {
                    "symbol": item.symbol,
                    "name": item.name,
                    "price": float(item.price) if item.price else 0,
                    "change": float(item.change) if item.change else 0,
                    "change_percent": item.change_percent,
                    "updated_at": item.updated_at.isoformat()
                }

                # 根据数据分类规范进行分类
                if item.data_type == "index" and item.market_region == "CN":
                    result["cn_indices"].append(item_info)
                elif item.data_type == "index" and item.market_region == "US":
                    result["us_indices"].append(item_info)
                elif item.data_type == "precious_metal":
                    result["precious_metals"].append(item_info)

            return result

        except Exception as e:
            logger.error(f"获取最新数据失败: {e}")
            return {"error": str(e)}

def run_continuous_crawler():
    crawler = None
    try:
        crawler = FinancialDataCrawler(headless=True)

        print(f"📈 金融数据采集器（含开盘/昨收/最高/最低/量/额）")
        print(f"🔁 每 {CRAWLER_INTERVAL_SECONDS // 60} 分钟自动运行一次\n")

        run_count = 1
        while True:
            print(f"\n🕒 第 {run_count} 轮抓取开始...")

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                results = loop.run_until_complete(crawler.fetch_all_markets())
                # crawler.save_to_file(results)

                print(f"💤 等待 {CRAWLER_INTERVAL_SECONDS} 秒...")
                time.sleep(CRAWLER_INTERVAL_SECONDS)
                run_count += 1
            finally:
                loop.close()
    except Exception as e:
        print(f"数据爬取出现错误: {e}")

    finally:
        if crawler:
            crawler.close()
        print("数据爬取已结束")

async def main():
    service = MarketDataService()
    result = await service.update_all_market_data()

    if result["success"]:
        logger.info(f"数据更新成功: {result['successful_crawls']}/{result['total_targets']} 个目标")
        logger.info(f"保存到数据库: {result['saved_to_db']} 条记录")
        if result["backup_file"]:
            logger.info(f"备份文件: {result['backup_file']}")
    else:
        logger.error(f"数据更新失败: {result.get('error')}")


if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        # 连续运行模式
        run_continuous_crawler()
    else:
        # 单次运行模式
        asyncio.run(main())