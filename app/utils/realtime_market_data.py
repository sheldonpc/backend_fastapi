import asyncio
import random
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

from fake_useragent import UserAgent
import requests


class MarketDataParser:
    """市场数据解析器"""

    @staticmethod
    def safe_float(value: str) -> float:
        """安全转换为float"""
        if not value or value in ('--', '', 'NaN'):
            return 0.0
        try:
            return float(value)
        except ValueError:
            return 0.0

    @staticmethod
    def safe_int(value: str) -> int:
        """安全转换为int"""
        if not value or value in ('--', '', 'NaN'):
            return 0
        try:
            return int(float(value))
        except ValueError:
            return 0

    @classmethod
    def parse_cn_market_data(cls, response_text: str) -> Dict[str, Dict[str, Any]]:
        """解析中国股市数据（A股、港股）"""
        result = {}
        pattern = r'var hq_str_(\w+)="([^"]*)"'
        matches = re.findall(pattern, response_text)

        for code, data_str in matches:
            data_parts = data_str.split(',')

            if code.startswith('rt_hk'):
                # 港股数据解析
                result[code] = cls._parse_hk_index_data(code, data_parts)
            else:
                # A股指数数据解析
                result[code] = cls._parse_cn_index_data(code, data_parts)

        return result

    @classmethod
    def _parse_hk_index_data(cls, code: str, data_parts: List[str]) -> Dict[str, Any]:
        """解析港股指数数据"""
        if len(data_parts) < 20:
            return {'code': code, 'error': '数据格式错误'}
        date =  data_parts[17]
        time = data_parts[18]
        normalized_date = date.replace('/', '-')
        date_time_str = f"{normalized_date} {time}"
        date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")

        return {
            'code': code,
            'symbol': data_parts[0],  # HSI
            'name': data_parts[1],  # 恒生指数
            'current_price': cls.safe_float(data_parts[6]),  # 当前价 26674.160
            'prev_close': cls.safe_float(data_parts[3]),  # 前收盘 26622.881
            'open_price': cls.safe_float(data_parts[2]),  # 开盘价 26888.400
            'high_price': cls.safe_float(data_parts[4]),  # 最高价 26558.280
            'low_price': cls.safe_float(data_parts[5]),  # 最低价 26855.559
            'change': cls.safe_float(data_parts[7]),  # 涨跌额 232.680
            'change_percent': cls.safe_float(data_parts[8]),  # 涨跌幅 0.870
            'turnover': cls.safe_float(data_parts[11]),  # 成交额 314926135.272
            'volume': cls.safe_int(data_parts[12]),  # 成交量 20514156899
            'year_high': cls.safe_float(data_parts[15]),  # 52周最高 27058.030
            'year_low': cls.safe_float(data_parts[16]),  # 52周最低 18671.490
            'date': data_parts[17],  # 日期 2025/09/30
            'time': data_parts[18],  # 时间 16:09:00
            'date_time': date_time
        }

    @classmethod
    def _parse_cn_index_data(cls, code: str, data_parts: List[str]) -> Dict[str, Any]:
        """解析A股指数数据"""
        if len(data_parts) < 30:
            return {'code': code, 'error': '数据格式错误'}
        date_str = data_parts[30] if len(data_parts) > 30 else ''  # 2025-09-30
        time_str = data_parts[31] if len(data_parts) > 31 else ''  # 15:30:39
        datetime_obj = None
        if date_str and time_str:
            try:
                datetime_str = f"{date_str} {time_str}"
                datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
            except ValueError as e:
                print(f"A股日期时间解析错误: {e}")

        return {
            'code': code,
            'name': data_parts[0],
            'open_price': cls.safe_float(data_parts[1]),
            'prev_close': cls.safe_float(data_parts[2]),
            'current_price': cls.safe_float(data_parts[3]),
            'high_price': cls.safe_float(data_parts[4]),
            'low_price': cls.safe_float(data_parts[5]),
            'volume': cls.safe_int(data_parts[8]),
            'amount': cls.safe_float(data_parts[9]),
            'date': data_parts[30] if len(data_parts) > 30 else '',
            'time': data_parts[31] if len(data_parts) > 31 else '',
            'date_time': datetime_obj
        }

    @classmethod
    def parse_global_market_data(cls, response_text: str) -> Dict[str, Dict[str, Any]]:
        """解析全球市场数据"""
        result = {}
        pattern = r'var hq_str_(\w+)="([^"]*)"'
        matches = re.findall(pattern, response_text)

        for code, data_str in matches:
            data_parts = data_str.split(',')

            if code.startswith('gb_'):
                result[code] = cls._parse_us_stock_data(code, data_parts)
            elif code.startswith('znb_'):
                result[code] = cls._parse_global_index_data(code, data_parts)

        return result

    @classmethod
    def _parse_us_stock_data(cls, code: str, data_parts: List[str]) -> Dict[str, Any]:
        """解析美股指数数据"""
        if len(data_parts) < 5:
            return {'code': code, 'error': '数据格式错误'}

        current_price = cls.safe_float(data_parts[1])
        change_amount = cls.safe_float(data_parts[4])

        return {
            'code': code,
            'name': data_parts[0],
            'current_price': current_price,
            'change_percent': cls.safe_float(data_parts[2]),
            'update_time': data_parts[3],
            'change_amount': change_amount,
            'prev_close': current_price - change_amount if current_price and change_amount else 0,
            'open_price': cls.safe_float(data_parts[5]) if len(data_parts) > 5 else 0,
            'high_price': cls.safe_float(data_parts[6]) if len(data_parts) > 6 else 0,
            'low_price': cls.safe_float(data_parts[7]) if len(data_parts) > 7 else 0,
            'year_high': cls.safe_float(data_parts[8]) if len(data_parts) > 8 else 0,
            'year_low': cls.safe_float(data_parts[9]) if len(data_parts) > 9 else 0,
        }

    @classmethod
    def _parse_global_index_data(cls, code: str, data_parts: List[str]) -> Dict[str, Any]:
        """解析全球其他指数数据"""
        if len(data_parts) < 5:
            return {'code': code, 'error': '数据格式错误'}

        # 判断数据格式类型
        is_europe_format = len(data_parts) >= 8 and '/' in str(data_parts[4])

        if is_europe_format:
            return cls._parse_europe_index_data(code, data_parts)
        else:
            return cls._parse_asia_pacific_index_data(code, data_parts)

    @classmethod
    def _parse_europe_index_data(cls, code: str, data_parts: List[str]) -> Dict[str, Any]:
        """解析欧洲指数数据"""
        return {
            'code': code,
            'name': data_parts[0],
            'current_price': cls.safe_float(data_parts[1]),
            'change_amount': cls.safe_float(data_parts[2]),
            'change_percent': cls.safe_float(data_parts[3]),
            'date': data_parts[4],
            'volume': cls.safe_int(data_parts[5]) if len(data_parts) > 5 else 0,
            'update_date': data_parts[6] if len(data_parts) > 6 else '',
            'update_time': data_parts[7] if len(data_parts) > 7 else '',
            'open_price': cls.safe_float(data_parts[8]) if len(data_parts) > 8 else 0,
            'high_price': cls.safe_float(data_parts[9]) if len(data_parts) > 9 else 0,
            'prev_close': cls.safe_float(data_parts[10]) if len(data_parts) > 10 else 0,
            'low_price': cls.safe_float(data_parts[11]) if len(data_parts) > 11 else 0,
        }

    @classmethod
    def _parse_asia_pacific_index_data(cls, code: str, data_parts: List[str]) -> Dict[str, Any]:
        """解析亚太指数数据"""
        return {
            'code': code,
            'name': data_parts[0],
            'current_price': cls.safe_float(data_parts[1]),
            'change_amount': cls.safe_float(data_parts[2]),
            'change_percent': cls.safe_float(data_parts[3]),
            'update_time': data_parts[4] if len(data_parts) > 4 else '',
            'volume': cls.safe_int(data_parts[5]) if len(data_parts) > 5 else 0,
            'update_date': data_parts[6] if len(data_parts) > 6 else '',
            'update_time_full': data_parts[7] if len(data_parts) > 7 else '',
            'open_price': cls.safe_float(data_parts[8]) if len(data_parts) > 8 else 0,
            'prev_close': cls.safe_float(data_parts[9]) if len(data_parts) > 9 else 0,
            'high_price': cls.safe_float(data_parts[10]) if len(data_parts) > 10 else 0,
            'low_price': cls.safe_float(data_parts[11]) if len(data_parts) > 11 else 0,
        }

    @classmethod
    def categorize_market_data(cls, market_data: Dict) -> Dict[str, List]:
        """将市场数据按地区分类"""
        categories = {
            'china': [],  # 中国
            'us': [],  # 美国
            'europe': [],  # 欧洲
            'asia_pacific': [],  # 亚太
            'others': []  # 其他
        }

        # 地区映射
        region_map = {
            'china': ['sh000001', 'sz399001', 'sh000300', 'rt_hkHSI'],
            'us': ['gb_dji', 'gb_ixic', 'gb_inx'],
            'europe': ['UKX', 'DAX', 'CAC', 'SMI', 'FTSEMIB', 'MADX', 'OMX', 'HEX',
                       'OSEAX', 'ISEQ', 'AEX', 'IBEX', 'SX5E', 'XU100'],
            'asia_pacific': ['NKY', 'TWJQ', 'FSSTI', 'KOSPI', 'FBMKLCI', 'SET', 'JCI',
                             'PCOMP', 'KSE100', 'SENSEX', 'VNINDEX', 'CSEALL', 'SASEIDX',
                             'AS51', 'NZSE50FG']
        }

        for code, data in market_data.items():
            found = False
            for region, codes in region_map.items():
                for pattern in codes:
                    if pattern in code:
                        categories[region].append(data)
                        found = True
                        break
                if found:
                    break
            if not found:
                categories['others'].append(data)

        return categories


class MarketDataFetcher:
    """市场数据获取器"""

    def __init__(self):
        self.parser = MarketDataParser()
        self.session = requests.Session()

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "User-Agent": UserAgent().random,
            "host": "hq.sinajs.cn",
            "referer": "https://finance.sina.com.cn/",
        }

    async def _fetch_data(self, url: str) -> str:
        """获取数据"""
        response = self.session.get(url, headers=self._get_headers())
        return response.text


async def get_all_realtime_market_data(
        include_china: bool = True,
        include_global: bool = True,
        categorize: bool = False
) -> Dict:
    """
    获取实时市场数据

    Args:
        include_china: 是否包含中国股市数据
        include_global: 是否包含全球市场数据
        categorize: 是否按地区分类数据

    Returns:
        市场数据字典，如果categorize为True则返回分类后的数据
    """
    fetcher = MarketDataFetcher()
    parser = MarketDataParser()

    all_market_data = {}

    # 中国股市数据
    if include_china:
        china_url = "https://hq.sinajs.cn/?list=sh000001,sz399001,sh000300,rt_hkHSI"
        china_data_text = await fetcher._fetch_data(china_url)
        china_data = parser.parse_cn_market_data(china_data_text)
        all_market_data.update(china_data)

        # 添加随机延迟
        await asyncio.sleep(random.uniform(0.5, 1))

    # 全球市场数据
    if include_global:
        global_url = "https://hq.sinajs.cn/?list=gb_dji,gb_ixic,gb_inx,znb_UKX,znb_DAX,znb_INDEXCF,znb_CAC,znb_SMI,znb_FTSEMIB,znb_MADX,znb_OMX,znb_HEX,znb_OSEAX,znb_ISEQ,znb_AEX,znb_IBEX,znb_SX5E,znb_XU100,znb_NKY,znb_TWJQ,znb_FSSTI,znb_KOSPI,znb_FBMKLCI,znb_SET,znb_JCI,znb_PCOMP,znb_KSE100,znb_SENSEX,znb_VNINDEX,znb_CSEALL,znb_SASEIDX,znb_SPTSX,znb_MEXBOL,znb_IBOV,znb_MERVAL,znb_AS51,znb_NZSE50FG,znb_CASE,znb_JALSH"
        global_data_text = await fetcher._fetch_data(global_url)
        global_data = parser.parse_global_market_data(global_data_text)
        all_market_data.update(global_data)

    # 如果需要分类数据
    if categorize:
        return parser.categorize_market_data(all_market_data)

    return all_market_data


# 测试函数
async def test_hk_data():
    """测试港股数据解析"""
    fetcher = MarketDataFetcher()
    parser = MarketDataParser()

    china_url = "https://hq.sinajs.cn/?list=sh000001,sz399001,sh000300,rt_hkHSI"
    china_data_text = await fetcher._fetch_data(china_url)
    china_data = parser.parse_cn_market_data(china_data_text)

    # 打印港股数据
    if 'rt_hkHSI' in china_data:
        hk_data = china_data['rt_hkHSI']
        print("港股数据解析结果:")
        for key, value in hk_data.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    asyncio.run(test_hk_data())