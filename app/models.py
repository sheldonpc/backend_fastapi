from datetime import datetime
from zoneinfo import ZoneInfo

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255)
    hashed_password = fields.CharField(max_length=255)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    avatar_url = fields.CharField(max_length=255, null=True)

    role = fields.CharField(max_length=50, default="user")  # 新增角色字段，默认普通用户


    def __str__(self):
        return self.username

User_Pydantic = pydantic_model_creator(User, name="User")
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)

class Category(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Tag(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)
    created_at = fields.DatetimeField()
    def __str__(self):
        return self.name

class Article(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    author = fields.ForeignKeyField("models.User", related_name="articles")
    is_published = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # 分类+标签
    category = fields.ForeignKeyField("models.Category", related_name="articles")
    tag = fields.ManyToManyField("models.Tag", related_name="articles", through="article_tag")


    def __str__(self):
        return self.title

Category_Pydantic = pydantic_model_creator(Category, name="Category")
CategoryIn_Pydantic = pydantic_model_creator(Category, name="CategoryIn", exclude_readonly=True)

Tag_Pydantic = pydantic_model_creator(Tag, name="Tag")
TagIn_Pydantic = pydantic_model_creator(Tag, name="TagIn", exclude_readonly=True)

Article_Pydantic = pydantic_model_creator(Article, name="Article")
ArticleIn_Pydantic = pydantic_model_creator(Article, name="ArticleIn", exclude_readonly=True)


class Comment(models.Model):
    id = fields.IntField(pk=True)
    content = fields.TextField()
    author = fields.ForeignKeyField("models.User", related_name="comments")
    article = fields.ForeignKeyField("models.Article", related_name="comments")
    is_visible = fields.BooleanField(default=True)  # 审核/屏蔽
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    is_approved = fields.BooleanField(default=False)  # 是否审核通过

    def __str__(self):
        return f"Comment {self.id} by {self.author.username}"

Comment_Pydantic = pydantic_model_creator(Comment, name="Comment")
CommentIn_Pydantic = pydantic_model_creator(Comment, name="CommentIn", exclude_readonly=True)

class ArticleLike(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="article_likes")
    article = fields.ForeignKeyField("models.Article", related_name="likes")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "article")  # 同一个用户只能点赞一次

class CommentLike(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="comment_likes")
    comment = fields.ForeignKeyField("models.Comment", related_name="likes")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "comment")

class ArticleFavorite(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="favorites")
    article = fields.ForeignKeyField("models.Article", related_name="favorites")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "article")

# 金融资讯
class FinancialNews(models.Model):
    """金融信息"""
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    author = fields.ForeignKeyField("models.User", related_name="financial_news")
    is_published = fields.BooleanField(default=False)
    # 无需在代码中处理时间戳，ORM 会自动维护
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    news_type = fields.CharField(max_length=50, default="general")
    symbol = fields.CharField(max_length=50, null=True)
    sentiment_score = fields.FloatField(null=True)
    source_url = fields.CharField(max_length=500, null=True)


# AI分析结果模型
class SentimentAnalysis(models.Model):
    """市场情绪分析结果"""
    id = fields.IntField(pk=True)
    symbol = fields.CharField(max_length=20)
    analysis_date = fields.DatetimeField(auto_now_add=True)
    sentiment_score = fields.FloatField()  # -1 (极度悲观) 到 1 (极度乐观)
    confidence = fields.FloatField()  # 0-1, 分析置信度
    summary = fields.TextField()  # AI生成的情绪分析摘要
    news_count = fields.IntField(default=0)  # 分析的新闻数量


# 废弃
# 废弃：股指和贵金属实时数据模型
class IndexData(models.Model):
    """股指和贵金属实时数据"""
    id = fields.IntField(pk=True)
    symbol = fields.CharField(max_length=50, unique=True)  # Shanghai, Shenzhen, ChiNext等
    name = fields.CharField(max_length=100)  # 中文名称
    timestamp = fields.DatetimeField()  # 数据时间戳
    
    # 价格相关字段
    price = fields.DecimalField(max_digits=15, decimal_places=4)  # 当前价格
    change = fields.DecimalField(max_digits=15, decimal_places=4, null=True)  # 涨跌额
    change_percent = fields.CharField(max_length=20, null=True)  # 涨跌幅百分比
    
    # 详细交易数据（可能为空）
    open_today = fields.DecimalField(max_digits=15, decimal_places=4, null=True)  # 今开
    close_yesterday = fields.DecimalField(max_digits=15, decimal_places=4, null=True)  # 昨收
    highest = fields.DecimalField(max_digits=15, decimal_places=4, null=True)  # 最高
    lowest = fields.DecimalField(max_digits=15, decimal_places=4, null=True)  # 最低
    volume = fields.CharField(max_length=50, null=True)  # 成交量（字符串格式，如"5.57亿手"）
    amount = fields.CharField(max_length=50, null=True)  # 成交额（字符串格式，如"9497.23亿元"）
    
    # 数据类型分类
    data_type = fields.CharField(max_length=30)  # index(指数), precious_metal(贵金属), us_stock(美股)
    market_region = fields.CharField(max_length=30)  # CN(中国), US(美国), Global(全球)
    
    # 更新时间
    updated_at = fields.DatetimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name}({self.symbol}): {self.price}"
    
    class Meta:
        table = "index_data"

def shanghai_now():
    return datetime.now(tz=ZoneInfo("Asia/Shanghai"))

# class GlobalIndexRealtimeData(models.Model):
#     """中国指数实时数据"""
#     id = fields.IntField(pk=True)
#     code = fields.CharField(max_length=20)
#     name = fields.CharField(max_length=50)
#     price = fields.DecimalField(max_digits=15, decimal_places=4)
#     change = fields.DecimalField(max_digits=15, decimal_places=4)
#     change_percent = fields.DecimalField(max_digits=15, decimal_places=4)
#     open_today = fields.DecimalField(max_digits=15, decimal_places=4)
#     highest = fields.DecimalField(max_digits=15, decimal_places=4)
#     lowest = fields.DecimalField(max_digits=15, decimal_places=4)
#     close_yesterday = fields.DecimalField(max_digits=15, decimal_places=4)
#     amplitude = fields.DecimalField(max_digits=15, decimal_places=4)
#     timestamp = fields.DatetimeField()
#     updated_at = fields.DatetimeField()
#
#     def __str__(self):
#         return f"{self.name}({self.code}): {self.price}"
#
#     class Meta:
#         table = "global_index_data"
#         unique_together = ("code", "timestamp")


class GlobalIndexLatest(models.Model):
    """全球指数最新数据（主表）"""
    id = fields.IntField(pk=True)
    code = fields.CharField(max_length=20, unique=True)  # 唯一约束
    name = fields.CharField(max_length=50)
    price = fields.DecimalField(max_digits=15, decimal_places=4)
    change = fields.DecimalField(max_digits=15, decimal_places=4)
    change_percent = fields.DecimalField(max_digits=15, decimal_places=4)
    open_today = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    highest = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    lowest = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    close_yesterday = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    amplitude = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    timestamp = fields.DatetimeField()   # 行情时间
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "global_index_latest"
        unique_together = ("code", "timestamp")

class GlobalIndexHistory(models.Model):
    """全球指数历史数据（历史表）"""
    id = fields.IntField(pk=True)
    code = fields.CharField(max_length=20)
    name = fields.CharField(max_length=50)
    price = fields.DecimalField(max_digits=15, decimal_places=4)
    change = fields.DecimalField(max_digits=15, decimal_places=4)
    change_percent = fields.DecimalField(max_digits=15, decimal_places=4)
    open_today = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    highest = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    lowest = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    close_yesterday = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    amplitude = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    timestamp = fields.DatetimeField()   # 行情时间
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "global_index_history"
        unique_together = ("code", "timestamp")  # 避免重复

# "代码", "名称", "最新价", "涨跌额", "涨跌幅", "开盘价", "最高价", "最低价", "昨收价", "振幅", "最新行情时间"
# 废弃
class CNIndexRealtimeData(models.Model):
    """中国指数实时数据"""
    id = fields.IntField(pk=True)
    code = fields.CharField(max_length=20)
    name = fields.CharField(max_length=50)
    price = fields.DecimalField(max_digits=15, decimal_places=4)
    change = fields.DecimalField(max_digits=15, decimal_places=4)
    change_percent = fields.DecimalField(max_digits=15, decimal_places=4)
    open_today = fields.DecimalField(max_digits=15, decimal_places=4)
    highest = fields.DecimalField(max_digits=15, decimal_places=4)
    lowest = fields.DecimalField(max_digits=15, decimal_places=4)
    close_yesterday = fields.DecimalField(max_digits=15, decimal_places=4)
    amplitude = fields.DecimalField(max_digits=15, decimal_places=4)
    timestamp = fields.DatetimeField()

    def __str__(self):
        return f"{self.name}({self.code}): {self.price}"

    class Meta:
        table = "cn_index_data"
# 废弃
class USAIndexRealtimeData(models.Model):
    """美国指数实时数据"""
    id = fields.IntField(pk=True)
    code = fields.CharField(max_length=20)
    name = fields.CharField(max_length=50)
    price = fields.DecimalField(max_digits=15, decimal_places=4)
    change = fields.DecimalField(max_digits=15, decimal_places=4)
    change_percent = fields.DecimalField(max_digits=15, decimal_places=4)
    open_today = fields.DecimalField(max_digits=15, decimal_places=4)
    highest = fields.DecimalField(max_digits=15, decimal_places=4)
    lowest = fields.DecimalField(max_digits=15, decimal_places=4)
    close_yesterday = fields.DecimalField(max_digits=15, decimal_places=4)
    amplitude = fields.DecimalField(max_digits=15, decimal_places=4)
    timestamp = fields.DatetimeField()

    def __str__(self):
        return f"{self.name}({self.code}): {self.price}"

    class Meta:
        table = "usa_index_data"

class RealTimeForeignCurrencyData(models.Model):
    """外汇实时数据"""
    id = fields.IntField(pk=True)
    code = fields.CharField(max_length=20)
    buying_price = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    selling_price = fields.DecimalField(max_digits=15, decimal_places=4, null=True)

class DailyFxSnapshot(models.Model):
    """每日外汇快照（宽表）"""
    date = fields.DateField(unique=True)  # 主键或唯一索引

    usd = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    eur = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    jpy = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    hkd = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    gbp = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    aud = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    nzd = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    sgd = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    chf = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    cad = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    myr = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    rub = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    zar = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    krw = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    aed = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    qar = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    huf = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    pln = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    dkk = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    sek = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    nok = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    try_ = fields.DecimalField(max_digits=15, decimal_places=4, null=True)  # try 是关键字
    php = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    thb = fields.DecimalField(max_digits=15, decimal_places=4, null=True)
    mop = fields.DecimalField(max_digits=15, decimal_places=4, null=True)

    class Meta:
        table = "daily_fx_snapshot"
        unique_together = ("date",)


class HotStock(models.Model):
    """热门股票"""
    id = fields.IntField(pk=True)
    code = fields.CharField(max_length=20)
    name = fields.CharField(max_length=50)
    followers = fields.IntField()
    price = fields.DecimalField(max_digits=15, decimal_places=4)

# 今开     最高     最低        成交量        成交额    时间戳
# 代码      名称   最新价  涨跌额   涨跌幅     买入     卖出     昨收  \
class MinuteLevelCNStockData(models.Model):
    """中国股票分钟级数据"""
    id = fields.IntField(pk=True)

    code = fields.CharField(max_length=20)
    name = fields.CharField(max_length=50)
    price = fields.DecimalField(max_digits=15, decimal_places=4)
    change = fields.DecimalField(max_digits=15, decimal_places=4)
    change_percent = fields.DecimalField(max_digits=15, decimal_places=4)
    buying_price = fields.DecimalField(max_digits=15, decimal_places=4)
    selling_price = fields.DecimalField(max_digits=15, decimal_places=4)
    close_yesterday = fields.DecimalField(max_digits=15, decimal_places=4)
    open_today = fields.DecimalField(max_digits=15, decimal_places=4)
    high = fields.DecimalField(max_digits=15, decimal_places=4)
    low = fields.DecimalField(max_digits=15, decimal_places=4)
    volume = fields.IntField()
    amount = fields.DecimalField(max_digits=15, decimal_places=4)
    timestamp = fields.DatetimeField()

    class Meta:
        table = "minute_level_cn_stock_data"
        unique_together = ("code", "name")

# 港股分钟级数据
    #  序号   代码                     名称    最新价  涨跌额  涨跌幅  \
    # 今开      最高      最低      昨收        成交量        成交额
class MinuteLevelHKStockData(models.Model):
    id = fields.IntField(pk=True)
    code = fields.CharField(max_length=20)
    name = fields.CharField(max_length=50)
    price = fields.DecimalField(max_digits=15, decimal_places=4)
    change = fields.DecimalField(max_digits=15, decimal_places=4)
    change_percent = fields.DecimalField(max_digits=15, decimal_places=4)
    close_yesterday = fields.DecimalField(max_digits=15, decimal_places=4)
    open_today = fields.DecimalField(max_digits=15, decimal_places=4)
    high = fields.DecimalField(max_digits=15, decimal_places=4)
    low = fields.DecimalField(max_digits=15, decimal_places=4)
    volume = fields.IntField()
    amount = fields.DecimalField(max_digits=15, decimal_places=4)
    timestamp = fields.DatetimeField()

    class Meta:
        table = "minute_level_hk_stock_data"
        unique_together = ("code", "name")

class CNSpecificStockData(models.Model):
    """特定数据模型 (精确匹配15个字段)"""

    id = fields.IntField(pk=True)

    # 价格数据 (4个字段)
    latest_price = fields.DecimalField(max_digits=10, decimal_places=2, description="最新价")
    high_price = fields.DecimalField(max_digits=10, decimal_places=2, description="最高价")
    low_price = fields.DecimalField(max_digits=10, decimal_places=2, description="最低价")
    open_price = fields.DecimalField(max_digits=10, decimal_places=2, description="今开价")

    # 基础信息 (3个字段)
    code = fields.CharField(max_length=10, description="股票代码")
    name = fields.CharField(max_length=50, description="股票简称")
    prev_close = fields.DecimalField(max_digits=10, decimal_places=2, description="昨收价")

    # 财务数据 (3个字段)
    net_profit = fields.DecimalField(max_digits=20, decimal_places=2, description="净利润")
    market_cap = fields.DecimalField(max_digits=20, decimal_places=2, description="总市值")
    float_market_cap = fields.DecimalField(max_digits=20, decimal_places=2, description="流通市值")

    # 分类信息 (2个字段)
    industry = fields.CharField(max_length=50, description="所属行业")
    region = fields.CharField(max_length=50, description="地域板块")

    # 估值指标 (3个字段)
    pe_ttm = fields.DecimalField(max_digits=10, decimal_places=2, description="市盈率（动态，TTM）")
    pe_static = fields.DecimalField(max_digits=10, decimal_places=2, description="市盈率（静态）")
    pe_rolling = fields.DecimalField(max_digits=10, decimal_places=2, description="市盈率（滚动）")

    # 时间信息 (1个字段)
    listing_date = fields.CharField(max_length=8, description="上市日期")  # 保持YYYYMMDD格式

    class Meta:
        table = "cn_stock_data"
        unique_together = [("code",)]

    def __str__(self):
        return f"{self.code} {self.name}"


class SpecificStockHistory(models.Model):
    """个股历史行情数据模型"""

    id = fields.IntField(pk=True)

    # 基础信息
    date = fields.DateField(description="日期")
    code = fields.CharField(max_length=10, description="股票代码")

    # 价格数据
    open_price = fields.DecimalField(max_digits=10, decimal_places=2, description="开盘价")
    close_price = fields.DecimalField(max_digits=10, decimal_places=2, description="收盘价")
    high_price = fields.DecimalField(max_digits=10, decimal_places=2, description="最高价")
    low_price = fields.DecimalField(max_digits=10, decimal_places=2, description="最低价")

    # 交易量数据
    volume = fields.BigIntField(description="成交量(手)")
    amount = fields.DecimalField(max_digits=20, decimal_places=2, description="成交额(元)")

    # 波动指标
    amplitude = fields.DecimalField(max_digits=10, decimal_places=2, description="振幅(%)")
    change_percent = fields.DecimalField(max_digits=10, decimal_places=2, description="涨跌幅(%)")
    change_amount = fields.DecimalField(max_digits=10, decimal_places=2, description="涨跌额")
    turnover_rate = fields.DecimalField(max_digits=10, decimal_places=2, description="换手率(%)")

    # 时间戳
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "specific_stock_history"
        table_description = "个股历史行情数据表"
        unique_together = [("date", "code")]  # 同一股票同一天只能有一条记录
        indexes = [
            ("code", "date"),  # 按股票代码和日期建立索引
        ]
        ordering = ["code", "-date"]  # 默认按代码和日期倒序排列

    def __str__(self):
        return f"{self.code} {self.date}"

# 弃用
class OilRealTimeData(models.Model):
    """原油实时数据模型（根据网页显示格式）"""

    id = fields.IntField(pk=True)

    # 基础信息
    symbol = fields.CharField(max_length=20, description="原油品种代码")  # brent, wti
    name = fields.CharField(max_length=50, description="原油品种名称")  # 布伦特原油, WTI纽约原油
    unit = fields.CharField(max_length=20, default="美元/桶", description="价格单位")

    # 主要价格数据
    current_price = fields.DecimalField(max_digits=10, decimal_places=3, description="当前价格")
    change_amount = fields.DecimalField(max_digits=10, decimal_places=3, description="涨跌额")
    change_percent = fields.DecimalField(max_digits=10, decimal_places=3, description="涨跌幅(%)")

    # 详细价格数据
    prev_close = fields.DecimalField(max_digits=10, decimal_places=3, description="昨收价")
    open_price = fields.DecimalField(max_digits=10, decimal_places=3, description="今开价")
    high_price = fields.DecimalField(max_digits=10, decimal_places=3, description="最高价")
    low_price = fields.DecimalField(max_digits=10, decimal_places=3, description="最低价")

    # 时间信息
    update_time = fields.DatetimeField(description="行情更新时间")  # 不自动更新

    # 系统字段
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "oil_real_time_data"
        indexes = [("symbol",)]

    def __str__(self):
        return f"{self.name} {self.current_price} {self.unit}"

    @property
    def price_display(self) -> str:
        """格式化价格显示"""
        return f"US$ {self.current_price}"

    @property
    def change_display(self) -> str:
        """格式化涨跌显示"""
        return f"{self.change_amount} {self.change_percent}%"

    @property
    def is_brent(self) -> bool:
        """是否为布伦特原油"""
        return self.symbol == "brent"

    @property
    def is_wti(self) -> bool:
        """是否为WTI原油"""
        return self.symbol == "wti"
# 弃用
class GoldRealTimeData(models.Model):
    """黄金实时数据模型"""

    id = fields.IntField(pk=True)

    # 基础信息
    symbol = fields.CharField(max_length=20, description="黄金品种代码")  # gds_AUTD, hf_GC, hf_XAU
    name = fields.CharField(max_length=50, description="黄金品种名称")  # 黄金延期, 纽约黄金, 伦敦金
    exchange = fields.CharField(max_length=30, description="交易所/市场")  # 上海黄金交易所, COMEX, 伦敦

    # 价格数据
    current_price = fields.DecimalField(max_digits=12, decimal_places=3, description="当前价格")
    prev_close = fields.DecimalField(max_digits=12, decimal_places=3, description="昨收价", null=True)
    open_price = fields.DecimalField(max_digits=12, decimal_places=3, description="开盘价")
    high_price = fields.DecimalField(max_digits=12, decimal_places=3, description="最高价")
    low_price = fields.DecimalField(max_digits=12, decimal_places=3, description="最低价")

    # 买卖价格
    bid_price = fields.DecimalField(max_digits=12, decimal_places=3, description="买价", null=True)
    ask_price = fields.DecimalField(max_digits=12, decimal_places=3, description="卖价", null=True)

    # 交易数据
    volume = fields.BigIntField(description="成交量", null=True)
    change_amount = fields.DecimalField(max_digits=10, decimal_places=3, description="涨跌额", null=True)
    change_percent = fields.DecimalField(max_digits=10, decimal_places=3, description="涨跌幅(%)", null=True)

    # 单位信息
    unit = fields.CharField(max_length=20, description="价格单位")  # 元/克, 美元/盎司

    # 时间信息
    update_time = fields.CharField(max_length=10, description="更新时间")  # 02:19:58
    data_date = fields.DateField(description="数据日期")  # 2025-09-27

    # 系统字段
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "gold_real_time_data"
        unique_together = [("symbol", "data_date")]
        indexes = [("symbol", "data_date")]
        ordering = ["-data_date", "-update_time"]

    def __str__(self):
        return f"{self.name} {self.current_price} {self.unit}"

    @property
    def is_shfe(self) -> bool:
        """是否为上海黄金交易所品种"""
        return self.symbol == "gds_AUTD"

    @property
    def is_comex(self) -> bool:
        """是否为COMEX黄金"""
        return self.symbol == "hf_GC"

    @property
    def is_london(self) -> bool:
        """是否为伦敦金"""
        return self.symbol == "hf_XAU"

    @property
    def price_display(self) -> str:
        """格式化价格显示"""
        if self.is_shfe:
            return f"¥ {self.current_price}/克"
        else:
            return f"$ {self.current_price}/盎司"

    @property
    def change_display(self) -> str:
        """格式化涨跌显示"""
        if self.change_amount and self.change_percent:
            sign = "+" if float(self.change_amount) > 0 else ""
            return f"{sign}{self.change_amount} ({sign}{self.change_percent}%)"
        return "N/A"
# 弃用
class SilverRealTimeData(models.Model):
    """白银实时数据模型"""

    id = fields.IntField(pk=True)

    # 基础信息
    symbol = fields.CharField(max_length=20, description="白银品种代码")  # gds_AGTD, hf_SI, hf_XAG
    name = fields.CharField(max_length=50, description="白银品种名称")  # 白银延期, 纽约白银, 伦敦银
    exchange = fields.CharField(max_length=30, description="交易所/市场")  # 上海黄金交易所, COMEX, 伦敦

    # 价格数据
    current_price = fields.DecimalField(max_digits=12, decimal_places=3, description="当前价格")
    prev_close = fields.DecimalField(max_digits=12, decimal_places=3, description="昨收价", null=True)
    open_price = fields.DecimalField(max_digits=12, decimal_places=3, description="开盘价")
    high_price = fields.DecimalField(max_digits=12, decimal_places=3, description="最高价")
    low_price = fields.DecimalField(max_digits=12, decimal_places=3, description="最低价")

    # 买卖价格
    bid_price = fields.DecimalField(max_digits=12, decimal_places=3, description="买价", null=True)
    ask_price = fields.DecimalField(max_digits=12, decimal_places=3, description="卖价", null=True)

    # 交易数据
    volume = fields.BigIntField(description="成交量", null=True)
    change_amount = fields.DecimalField(max_digits=10, decimal_places=3, description="涨跌额", null=True)
    change_percent = fields.DecimalField(max_digits=10, decimal_places=3, description="涨跌幅(%)", null=True)

    # 单位信息
    unit = fields.CharField(max_length=20, description="价格单位")  # 元/千克, 美元/盎司

    # 时间信息
    update_time = fields.CharField(max_length=10, description="更新时间")  # 02:30:00
    data_date = fields.DateField(description="数据日期")  # 2025-09-27

    # 系统字段
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "silver_real_time_data"
        unique_together = [("symbol", "data_date")]
        indexes = [("symbol", "data_date")]
        ordering = ["-data_date", "-update_time"]

    def __str__(self):
        return f"{self.name} {self.current_price} {self.unit}"

    @property
    def is_shfe(self) -> bool:
        """是否为上海黄金交易所品种"""
        return self.symbol == "gds_AGTD"

    @property
    def is_comex(self) -> bool:
        """是否为COMEX白银"""
        return self.symbol == "hf_SI"

    @property
    def is_london(self) -> bool:
        """是否为伦敦银"""
        return self.symbol == "hf_XAG"

    @property
    def price_display(self) -> str:
        """格式化价格显示"""
        if self.is_shfe:
            return f"¥ {self.current_price}/千克"
        else:
            return f"$ {self.current_price}/盎司"

    @property
    def change_display(self) -> str:
        """格式化涨跌显示"""
        if self.change_amount is not None and self.change_percent is not None:
            sign = "+" if float(self.change_amount) > 0 else ""
            return f"{sign}{self.change_amount} ({sign}{self.change_percent}%)"
        return "N/A"

    @property
    def is_positive(self) -> bool:
        """是否上涨"""
        return self.change_amount is not None and float(self.change_amount) > 0


class ForeignCommodityRealTimeData2(models.Model):
    symbol = fields.CharField(max_length=20, unique=True, description="品种代码，如 CL GC FEF")
    name = fields.CharField(max_length=100, description="品种名称")

    current_price = fields.DecimalField(max_digits=12, decimal_places=4)
    rmb_price = fields.DecimalField(max_digits=12, decimal_places=4)
    change_amount = fields.DecimalField(max_digits=12, decimal_places=4)
    change_percent = fields.DecimalField(max_digits=8, decimal_places=3)
    open_price = fields.DecimalField(max_digits=12, decimal_places=4)
    high_price = fields.DecimalField(max_digits=12, decimal_places=4)
    low_price = fields.DecimalField(max_digits=12, decimal_places=4)
    settlement_price = fields.DecimalField(max_digits=12, decimal_places=4)
    open_interest = fields.BigIntField(default=0)
    bid_price = fields.DecimalField(max_digits=12, decimal_places=4)
    ask_price = fields.DecimalField(max_digits=12, decimal_places=4)

    update_time = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "foreign_commodity_realtime_data_fix"


class ForeignCommodityHistory2(models.Model):
    id = fields.BigIntField(pk=True)
    symbol = fields.CharField(max_length=20, description="品种代码，如 CL GC FEF")
    name = fields.CharField(max_length=100, description="品种名称")

    current_price = fields.DecimalField(max_digits=12, decimal_places=4)
    rmb_price = fields.DecimalField(max_digits=12, decimal_places=4)
    change_amount = fields.DecimalField(max_digits=12, decimal_places=4)
    change_percent = fields.DecimalField(max_digits=8, decimal_places=3)
    open_price = fields.DecimalField(max_digits=12, decimal_places=4)
    high_price = fields.DecimalField(max_digits=12, decimal_places=4)
    low_price = fields.DecimalField(max_digits=12, decimal_places=4)
    settlement_price = fields.DecimalField(max_digits=12, decimal_places=4)
    open_interest = fields.BigIntField(default=0)
    bid_price = fields.DecimalField(max_digits=12, decimal_places=4)
    ask_price = fields.DecimalField(max_digits=12, decimal_places=4)

    timestamp = fields.DatetimeField(default=datetime.utcnow)

    class Meta:
        table = "foreign_commodity_history_fix"
        indexes = [
            ("symbol", "timestamp"),
        ]

class VIXRealTimeData(models.Model):
    """VIX恐慌指数实时数据模型"""

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, default="VIX恐慌指数", description="指数名称")

    # 主要价格数据
    current_price = fields.DecimalField(max_digits=8, decimal_places=4, description="当前价格")
    change_amount = fields.DecimalField(max_digits=8, decimal_places=4, description="涨跌额")
    change_percent = fields.DecimalField(max_digits=8, decimal_places=2, description="涨跌幅(%)")

    # 日内价格数据
    open_price = fields.DecimalField(max_digits=8, decimal_places=4, description="今开价")
    high_price = fields.DecimalField(max_digits=8, decimal_places=4, description="最高价")
    prev_close = fields.DecimalField(max_digits=8, decimal_places=4, description="昨收价")
    low_price = fields.DecimalField(max_digits=8, decimal_places=4, description="最低价")

    # 时间信息
    update_time = fields.DatetimeField()  # 04:14:00
    api_date = fields.DatetimeField()

    class Meta:
        table = "vix_real_time_data"
        ordering = ["-created_at"]

    def __str__(self):
        return f"VIX指数 {self.current_price}"

class MarketIndexData(models.Model):
    """主要指数涨跌数据模型"""

    id = fields.IntField(pk=True)

    # 基础信息
    index_code = fields.CharField(max_length=10, description="指数代码")  # sh000001, sz399001
    index_name = fields.CharField(max_length=50, description="指数名称")  # 上证指数, 深证成指

    # 价格数据
    last_price = fields.DecimalField(max_digits=12, decimal_places=3, description="最新价")
    change = fields.DecimalField(max_digits=10, decimal_places=4, description="涨跌幅")
    change_amount = fields.DecimalField(max_digits=10, decimal_places=3, description="涨跌额")

    # 涨跌家数
    up_num = fields.IntField(description="上涨家数")
    down_num = fields.IntField(description="下跌家数")
    flat_num = fields.IntField(description="平盘家数")

    # 时间信息
    update_time = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "market_index_data"
        unique_together = [("index_code", "update_time")]
        ordering = ["-update_time"]

    def __str__(self):
        return f"{self.index_name} {self.last_price}"

    @property
    def change_display(self) -> str:
        """格式化涨跌显示"""
        sign = "+" if float(self.change) > 0 else ""
        return f"{sign}{self.change_amount} ({sign}{float(self.change) * 100:.2f}%)"

    @property
    def up_down_ratio(self) -> float:
        """涨跌比"""
        if self.down_num > 0:
            return round(self.up_num / self.down_num, 2)
        return 0


class MarketUpDownStats(models.Model):
    """全市场涨跌统计"""

    id = fields.IntField(pk=True)

    # 基础统计
    up_num = fields.IntField(description="上涨家数")
    down_num = fields.IntField(description="下跌家数")
    flat_num = fields.IntField(description="平盘家数")
    rise_num = fields.IntField(description="上涨家数(全市场)")
    fall_num = fields.IntField(description="下跌家数(全市场)")
    average_rise = fields.DecimalField(max_digits=10, decimal_places=4, description="平均涨跌幅")

    # 涨跌分布
    up_2 = fields.IntField(description="涨幅2%以上")
    up_4 = fields.IntField(description="涨幅4%以上")
    up_6 = fields.IntField(description="涨幅6%以上")
    up_8 = fields.IntField(description="涨幅8%以上")
    up_10 = fields.IntField(description="涨幅10%以上")

    down_2 = fields.IntField(description="跌幅2%以上")
    down_4 = fields.IntField(description="跌幅4%以上")
    down_6 = fields.IntField(description="跌幅6%以上")
    down_8 = fields.IntField(description="跌幅8%以上")
    down_10 = fields.IntField(description="跌幅10%以上")

    # 特殊状态
    suspend_num = fields.IntField(description="停牌家数")
    status = fields.BooleanField(description="数据状态")

    # 时间信息
    update_time = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "market_up_down_stats"
        ordering = ["-update_time"]

    def __str__(self):
        return f"全市场涨跌 {self.up_num}↑/{self.down_num}↓"

    @property
    def up_percent(self) -> float:
        """上涨比例"""
        total = self.up_num + self.down_num + self.flat_num
        return round(self.up_num / total * 100, 2) if total > 0 else 0

    @property
    def strong_up_percent(self) -> float:
        """强势上涨比例(涨幅>4%)"""
        total = self.up_num + self.down_num + self.flat_num
        strong_up = self.up_4 + self.up_6 + self.up_8 + self.up_10
        return round(strong_up / total * 100, 2) if total > 0 else 0

    @property
    def strong_down_percent(self) -> float:
        """强势下跌比例(跌幅>4%)"""
        total = self.up_num + self.down_num + self.flat_num
        strong_down = self.down_4 + self.down_6 + self.down_8 + self.down_10
        return round(strong_down / total * 100, 2) if total > 0 else 0


class SH000001History(models.Model):
    """上证指数历史数据模型"""

    id = fields.IntField(pk=True)
    date = fields.DateField(description="交易日期", unique=True)
    open = fields.DecimalField(max_digits=12, decimal_places=3, description="开盘价")
    high = fields.DecimalField(max_digits=12, decimal_places=3, description="最高价")
    low = fields.DecimalField(max_digits=12, decimal_places=3, description="最低价")
    close = fields.DecimalField(max_digits=12, decimal_places=3, description="收盘价")
    volume = fields.BigIntField(description="成交量")

    class Meta:
        table = "sh000001_history"
        ordering = ["-date"]

    def __str__(self):
        return f"上证指数 {self.date} {self.close}"


class SZ399001History(models.Model):
    """深证成指历史数据模型"""

    id = fields.IntField(pk=True)
    date = fields.DateField(description="交易日期", unique=True)
    open = fields.DecimalField(max_digits=12, decimal_places=3, description="开盘价")
    high = fields.DecimalField(max_digits=12, decimal_places=3, description="最高价")
    low = fields.DecimalField(max_digits=12, decimal_places=3, description="最低价")
    close = fields.DecimalField(max_digits=12, decimal_places=3, description="收盘价")
    volume = fields.BigIntField(description="成交量")

    class Meta:
        table = "sz399001_history"
        ordering = ["-date"]

    def __str__(self):
        return f"深证成指 {self.date} {self.close}"


class SZ399006History(models.Model):
    """创业板指历史数据模型"""

    id = fields.IntField(pk=True)
    date = fields.DateField(description="交易日期", unique=True)
    open = fields.DecimalField(max_digits=12, decimal_places=3, description="开盘价")
    high = fields.DecimalField(max_digits=12, decimal_places=3, description="最高价")
    low = fields.DecimalField(max_digits=12, decimal_places=3, description="最低价")
    close = fields.DecimalField(max_digits=12, decimal_places=3, description="收盘价")
    volume = fields.BigIntField(description="成交量")

    class Meta:
        table = "sz399006_history"
        ordering = ["-date"]

    def __str__(self):
        return f"创业板指 {self.date} {self.close}"

class HSIHistory(models.Model):
    """恒生历史数据模型"""

    id = fields.IntField(pk=True)
    date = fields.DateField(description="交易日期", unique=True)
    open = fields.DecimalField(max_digits=12, decimal_places=3, description="开盘价")
    high = fields.DecimalField(max_digits=12, decimal_places=3, description="最高价")
    low = fields.DecimalField(max_digits=12, decimal_places=3, description="最低价")
    close = fields.DecimalField(max_digits=12, decimal_places=3, description="收盘价")
    volume = fields.BigIntField(description="成交量")

    class Meta:
        table = "hsi_history"
        ordering = ["-date"]

    def __str__(self):
        return f"创业板指 {self.date} {self.close}"

class SP500History(models.Model):
    """标普500历史数据模型"""
    id = fields.IntField(pk=True)
    date = fields.DateField(description="交易日期", unique=True)
    code = fields.CharField(max_length=10, description="股票代码")
    name = fields.CharField(max_length=50, description="股票名称")
    open = fields.DecimalField(max_digits=12, decimal_places=3, description="今开")
    close = fields.DecimalField(max_digits=12, decimal_places=3, description="最新价")
    high = fields.DecimalField(max_digits=12, decimal_places=3, description="最高价")
    low = fields.DecimalField(max_digits=12, decimal_places=3, description="最低价")
    amplitude = fields.DecimalField(max_digits=10, decimal_places=3, description="振幅")

    class Meta:
        table = "spx_history"
        ordering = ["-date"]

    def __str__(self):
        return f"标普500 {self.date} {self.close}"

class NDXHistory(models.Model):
    """纳斯达克指数历史数据模型"""

    id = fields.IntField(pk=True)
    date = fields.DateField(description="交易日期", unique=True)
    code = fields.CharField(max_length=10, description="指数代码", default="NDX")
    name = fields.CharField(max_length=50, description="指数名称", default="纳斯达克")
    open = fields.DecimalField(max_digits=12, decimal_places=3, description="今开")
    close = fields.DecimalField(max_digits=12, decimal_places=3, description="最新价")
    high = fields.DecimalField(max_digits=12, decimal_places=3, description="最高")
    low = fields.DecimalField(max_digits=12, decimal_places=3, description="最低")
    amplitude = fields.DecimalField(max_digits=10, decimal_places=3, description="振幅")

    class Meta:
        table = "ndx_history"
        ordering = ["-date"]

    def __str__(self):
        return f"纳斯达克 {self.date} {self.close}"

class DJIAHistory(models.Model):
    """道琼斯指数历史数据模型"""

    id = fields.IntField(pk=True)
    date = fields.DateField(description="交易日期", unique=True)
    code = fields.CharField(max_length=10, description="指数代码", default="DJIA")
    name = fields.CharField(max_length=50, description="指数名称", default="道琼斯")
    open = fields.DecimalField(max_digits=12, decimal_places=3, description="今开")
    close = fields.DecimalField(max_digits=12, decimal_places=3, description="最新价")
    high = fields.DecimalField(max_digits=12, decimal_places=3, description="最高")
    low = fields.DecimalField(max_digits=12, decimal_places=3, description="最低")
    amplitude = fields.DecimalField(max_digits=10, decimal_places=3, description="振幅")

    class Meta:
        table = "djia_history"
        ordering = ["-date"]

    def __str__(self):
        return f"道琼斯 {self.date} {self.close}"

class GoldHistory(models.Model):
    """黄金价格历史数据模型"""
    id = fields.IntField(pk=True)
    date = fields.DateField(description="交易日期", unique=True)
    open = fields.DecimalField(max_digits=12, decimal_places=3, description="今开")
    close = fields.DecimalField(max_digits=12, decimal_places=3, description="最新价")
    high = fields.DecimalField(max_digits=12, decimal_places=3, description="最高")
    low = fields.DecimalField(max_digits=12, decimal_places=3, description="最低")

    class Meta:
        table = "gold_history"
        ordering = ["-date"]

    def __str__(self):
        return f"黄金 {self.date} {self.close}"

class SilverHistory(models.Model):
    """白银价格历史数据模型"""
    id = fields.IntField(pk=True)
    date = fields.DateField(description="交易日期", unique=True)
    open = fields.DecimalField(max_digits=12, decimal_places=3, description="今开")
    close = fields.DecimalField(max_digits=12, decimal_places=3, description="最新价")
    high = fields.DecimalField(max_digits=12, decimal_places=3, description="最高")
    low = fields.DecimalField(max_digits=12, decimal_places=3, description="最低")

    class Meta:
        table = "silver_history"
        ordering = ["-date"]

    def __str__(self):
        return f"白银 {self.date} {self.close}"

class PlatinumHistory(models.Model):
    """铂金价格历史数据模型"""
    id = fields.IntField(pk=True)
    date = fields.DateField(description="交易日期", unique=True)
    open = fields.DecimalField(max_digits=12, decimal_places=3, description="今开")
    close = fields.DecimalField(max_digits=12, decimal_places=3, description="最新价")
    high = fields.DecimalField(max_digits=12, decimal_places=3, description="最高")
    low = fields.DecimalField(max_digits=12, decimal_places=3, description="最低")
    class Meta:
        table = "platinum_history"
        ordering = ["-date"]

    def __str__(self):
        return f"铂金 {self.date} {self.close}"


class BondYieldHistory(models.Model):
    """债券收益率历史数据模型"""

    id = fields.IntField(pk=True)
    date = fields.DateField(description="交易日期", unique=True)

    # 中国国债收益率
    cn_2y = fields.DecimalField(max_digits=8, decimal_places=4, description="中国国债收益率2年", null=True)
    cn_5y = fields.DecimalField(max_digits=8, decimal_places=4, description="中国国债收益率5年", null=True)
    cn_10y = fields.DecimalField(max_digits=8, decimal_places=4, description="中国国债收益率10年", null=True)
    cn_30y = fields.DecimalField(max_digits=8, decimal_places=4, description="中国国债收益率30年", null=True)
    cn_spread_10y_2y = fields.DecimalField(max_digits=8, decimal_places=4, description="中国国债收益率10年-2年", null=True)
    cn_gdp_growth = fields.DecimalField(max_digits=8, decimal_places=4, description="中国GDP年增率", null=True)

    # 美国国债收益率
    us_2y = fields.DecimalField(max_digits=8, decimal_places=4, description="美国国债收益率2年", null=True)
    us_5y = fields.DecimalField(max_digits=8, decimal_places=4, description="美国国债收益率5年", null=True)
    us_10y = fields.DecimalField(max_digits=8, decimal_places=4, description="美国国债收益率10年", null=True)
    us_30y = fields.DecimalField(max_digits=8, decimal_places=4, description="美国国债收益率30年", null=True)
    us_spread_10y_2y = fields.DecimalField(max_digits=8, decimal_places=4, description="美国国债收益率10年-2年", null=True)
    us_gdp_growth = fields.DecimalField(max_digits=8, decimal_places=4, description="美国GDP年增率", null=True)

    class Meta:
        table = "bond_yield_history"
        ordering = ["-date"]

    def __str__(self):
        return f"债券收益率 {self.date} 中10Y:{self.cn_10y} 美10Y:{self.us_10y}"

    @property
    def cn_yield_curve(self) -> dict:
        """中国国债收益率曲线"""
        return {
            '2年': self.cn_2y,
            '5年': self.cn_5y,
            '10年': self.cn_10y,
            '30年': self.cn_30y
        }

    @property
    def us_yield_curve(self) -> dict:
        """美国国债收益率曲线"""
        return {
            '2年': self.us_2y,
            '5年': self.us_5y,
            '10年': self.us_10y,
            '30年': self.us_30y
        }

    @property
    def cn_us_spread_10y(self) -> float:
        """中美10年期国债利差"""
        if self.cn_10y and self.us_10y:
            return float(self.cn_10y) - float(self.us_10y)
        return 0.0

    @property
    def cn_yield_curve_steepness(self) -> float:
        """中国收益率曲线陡峭度(30年-2年)"""
        if self.cn_30y and self.cn_2y:
            return float(self.cn_30y) - float(self.cn_2y)
        return 0.0

    @property
    def us_yield_curve_steepness(self) -> float:
        """美国收益率曲线陡峭度(30年-2年)"""
        if self.us_30y and self.us_2y:
            return float(self.us_30y) - float(self.us_2y)
        return 0.0


class RichList(models.Model):
    """富豪排行榜数据模型"""

    id = fields.IntField(pk=True)
    rank = fields.IntField(description="排名")
    wealth = fields.DecimalField(max_digits=12, decimal_places=2, description="财富(亿元)")
    name = fields.CharField(max_length=50, description="姓名")
    company = fields.CharField(max_length=100, description="企业")
    industry = fields.CharField(max_length=100, description="行业")
    year = fields.IntField(description="榜单年份")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "rich_list"
        ordering = ["rank",]

    def __str__(self):
        return f"{self.year}年-第{self.rank}名: {self.name}"

    @property
    def wealth_display(self) -> str:
        """格式化财富显示"""
        return f"{self.wealth}亿元"

    @property
    def rank_display(self) -> str:
        """格式化排名显示"""
        return f"第{self.rank}名"

    @property
    def is_top_10(self) -> bool:
        """是否前十名"""
        return self.rank <= 10

    @property
    def is_top_100(self) -> bool:
        """是否前一百名"""
        return self.rank <= 100

class News1(models.Model):
    """新闻数据模型"""

    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200, description="新闻标题")
    content = fields.TextField(description="新闻内容")
    publish_time = fields.DatetimeField(description="发布时间")
    source = fields.CharField(max_length=500, description="新闻来源", null=True)

    class Meta:
        table = "news"
        ordering = ["-publish_time"]
        indexes = [
            ("title", "publish_time"),  # 按标题和时间查询
        ]

    def __str__(self):
        return f"{self.title} ({self.publish_time})"

    @property
    def is_recent(self) -> bool:
        """是否近期新闻(24小时内)"""
        return (datetime.now() - self.publish_time).total_seconds() < 86400

    @property
    def short_content(self) -> str:
        """获取摘要(前100字)"""
        return self.content[:100] + "..." if len(self.content) > 100 else self.content

    @property
    def formatted_time(self) -> str:
        """格式化时间显示"""
        return self.publish_time.strftime("%Y-%m-%d %H:%M:%S")

# 标题 内容  时间 链接
class News2(models.Model):
    """新闻数据模型"""
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200, description="新闻标题")
    content = fields.TextField(description="新闻内容")
    publish_time = fields.DatetimeField(description="发布时间")
    source = fields.CharField(max_length=500, description="新闻来源", null=True)

    class Meta:
        table = "news2"
        unique_together = [
            ("title", "publish_time"),  # 按标题和时间查询
        ]
        ordering = ["-publish_time"]

# 标题 摘要  时间 链接
class News3(models.Model):
    """新闻数据模型"""
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200, description="新闻标题")
    content = fields.TextField(description="新闻内容")
    publish_time = fields.DatetimeField(description="发布时间")
    source = fields.CharField(max_length=500, description="新闻来源", null=True)
    class Meta:
        table = "news3"
        ordering = ["-publish_time"]

    def __str__(self):
        return f"{self.title} ({self.publish_time})"

class News4(models.Model):
    """新闻数据模型"""
    id = fields.IntField(pk=True)
    publish_time = fields.DatetimeField(description="发布时间")
    content = fields.TextField(description="新闻内容")

    class Meta:
        table = "news4"
        ordering = ["-publish_time"]

    def __str__(self):
        return f"{self.publish_time}"

# 标题 摘要 发布时间 链接
class EastMoneyHistoryNews(models.Model):
    """东方财富历史新闻数据模型"""
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200, description="新闻标题")
    summary = fields.TextField(description="新闻摘要", null=True)
    publish_time = fields.DatetimeField(description="发布时间")
    source = fields.CharField(max_length=500, description="新闻来源", null=True)
    class Meta:
        table = "east_money_history_news"
        ordering = ["-publish_time"]

    def __str__(self):
        return f"{self.title} ({self.publish_time})"


class KeyPoint(models.Model):
    """关键要点（Tortoise ORM 模型）"""
    id = fields.IntField(pk=True)
    type = fields.CharField(max_length=10, description="类型: positive/warning/negative")
    text = fields.CharField(max_length=50, description="要点内容（不超过50字）")

    # 关联到 CNMarket（多对一）
    market = fields.ForeignKeyField(
        "models.CNMarket",
        related_name="key_points",
        on_delete=fields.CASCADE
    )

    class Meta:
        table = "market_key_points"  # 自定义表名


class CNMarket(models.Model):
    """市场研判结果（Tortoise ORM 模型）"""
    id = fields.IntField(pk=True)
    market_region = fields.CharField(max_length=2, default="CN", description="市场区域")
    data_type = fields.CharField(max_length=10, default="index", description="数据类型")
    confidence = fields.IntField(description="置信度 (0-100)")
    sentiment = fields.CharField(max_length=10, description="情绪: 看好/中性/看空/乐观/悲观")
    sentiment_level = fields.CharField(max_length=10, description="情绪级别: bullish/neutral/bearish")
    focus_sectors = fields.JSONField(description="关注行业列表", default=list)
    support_level = fields.FloatField(null=True, description="支撑位（可选）")
    resistance_level = fields.FloatField(null=True, description="阻力位（可选）")
    created_at = fields.DatetimeField(auto_now_add=True)

    # 反向关系（通过 KeyPoint.market 关联）
    key_points: fields.ReverseRelation[KeyPoint]

    class Meta:
        table = "cn_market_reports"  # 自定义表名

    async def to_dict(self) -> dict:
        """将 ORM 对象转为 JSON 兼容的字典（用于 API 返回）"""
        return {
            "market_region": self.market_region,
            "data_type": self.data_type,
            "confidence": self.confidence,
            "sentiment": self.sentiment,
            "sentiment_level": self.sentiment_level,
            "key_points": [
                {"type": kp.type, "text": kp.text}
                for kp in await self.key_points.all()  # 注意：异步调用
            ],
            "focus_sectors": self.focus_sectors,
            "support_level": self.support_level,
            "resistance_level": self.resistance_level
        }

    @classmethod
    async def from_dict(cls, data: dict) -> "CNMarket":
        """从 JSON 数据创建并保存 CNMarket 对象（含关联 KeyPoint）"""
        market = await cls.create(
            market_region=data.get("market_region", "CN"),
            data_type=data.get("data_type", "index"),
            confidence=data["confidence"],
            sentiment=data["sentiment"],
            sentiment_level=data["sentiment_level"],
            focus_sectors=data["focus_sectors"],
            support_level=data.get("support_level"),
            resistance_level=data.get("resistance_level")
        )

        # 批量创建关联的 KeyPoint
        if "key_points" in data:
            await KeyPoint.bulk_create([
                KeyPoint(type=kp["type"], text=kp["text"], market=market)
                for kp in data["key_points"]
            ])

        return market