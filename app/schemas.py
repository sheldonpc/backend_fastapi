from typing import Optional, Annotated, Dict, Any

from pydantic import BaseModel, EmailStr, constr, Field
from tortoise.contrib.pydantic import pydantic_model_creator
from datetime import datetime
from typing import List, Optional

from app.models import Comment, ArticleLike, CommentLike, ArticleFavorite, FinancialNews, SentimentAnalysis, IndexData, \
    IndustryLatest, StockLast3Days, StockLast5Days, StockLast10Days, StockLast20Days, StockLatest, StockLHBDetail, \
    StockHotRank, StockHotUp, StockHotSearchBaidu, StockZTPool, StockZTPoolPrevious, StockZTPoolStrong, StockZTPoolDown, \
    StockHKHotRank, IndustryLast3Days, IndustryLast5Days, IndustryLast10Days, IndustryLast20Days, ConceptLatest, \
    ConceptLast3Days, ConceptLast5Days, ConceptLast10Days, ConceptLast20Days


class SendCodeRequest(BaseModel):
    email: str


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    code: str


class UserLogin(BaseModel):
    identifier: str
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    avatar_url: Optional[str] = None


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    role: str
    created_at: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


PasswordStr = Annotated[
    str,
    Field(min_length=8, max_length=20, pattern="^[a-zA-Z0-9!@#$_]+$")
]


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: PasswordStr


class PasswordChangeConfirm(BaseModel):
    code: str
    new_password: PasswordStr


class PasswordResetRequest(BaseModel):
    email: str
    code: str
    new_password: PasswordStr


TitleStr = Annotated[
    str,
    Field(min_length=1, max_length=255)
]

# 用于返回给前端的完整评论信息
Comment_Pydantic = pydantic_model_creator(Comment, name="Comment")

# 用于接收前端请求的数据（不包含只读字段）
CommentIn_Pydantic = pydantic_model_creator(Comment, name="CommentIn", exclude_readonly=True)

ArticleLike_Pydantic = pydantic_model_creator(ArticleLike, name="ArticleLike")
CommentLike_Pydantic = pydantic_model_creator(CommentLike, name="CommentLike")
ArticleFavorite_Pydantic = pydantic_model_creator(ArticleFavorite, name="ArticleFavorite")

FinancialNews_Pydantic = pydantic_model_creator(FinancialNews, name="FinancialNews")
MarketData_Pydantic = pydantic_model_creator(IndexData, name="MarketData")
SentimentAnalysis_Pydantic = pydantic_model_creator(SentimentAnalysis, name="SentimentAnalysis")

# 行业
IndustryLatest_Pydantic = pydantic_model_creator(IndustryLatest, name="IndustryLatest")
IndustryLast3Days_Pydantic = pydantic_model_creator(IndustryLast3Days, name="IndustryLast3Days")
IndustryLast5Days_Pydantic = pydantic_model_creator(IndustryLast5Days, name="IndustryLast5Days")
IndustryLast10Days_Pydantic = pydantic_model_creator(IndustryLast10Days, name="IndustryLast10Days")
IndustryLast20Days_Pydantic = pydantic_model_creator(IndustryLast20Days, name="IndustryLast20Days")

# 个股
StockLatest_Pydantic = pydantic_model_creator(StockLatest, name="StockLatest")
StockLast3Days_Pydantic = pydantic_model_creator(StockLast3Days, name="StockLast3Days")
StockLast5Days_Pydantic = pydantic_model_creator(StockLast5Days, name="StockLast5Days")
StockLast10Days_Pydantic = pydantic_model_creator(StockLast10Days, name="StockLast10Days")
StockLast20Days_Pydantic = pydantic_model_creator(StockLast20Days, name="StockLast20Days")

# 概念
ConceptLatest_Pydantic = pydantic_model_creator(ConceptLatest, name="ConceptLatest")
ConceptLast3Days_Pydantic = pydantic_model_creator(ConceptLast3Days, name="ConceptLast3Days")
ConceptLast5Days_Pydantic = pydantic_model_creator(ConceptLast5Days, name="ConceptLast5Days")
ConceptLast10Days_Pydantic = pydantic_model_creator(ConceptLast10Days, name="ConceptLast10Days")
ConceptLast20Days_Pydantic = pydantic_model_creator(ConceptLast20Days, name="ConceptLast20Days")

# 其他
StockLHBDetail_Pydantic = pydantic_model_creator(StockLHBDetail, name="StockLHBDetail")
StockHotRank_Pydantic = pydantic_model_creator(StockHotRank, name="StockHotRank")
StockHotUp_Pydantic = pydantic_model_creator(StockHotUp, name="StockHotUp")
StockHotSearchBaidu_Pydantic = pydantic_model_creator(StockHotSearchBaidu, name="StockHotSearchBaidu")
StockZTPool_Pydantic = pydantic_model_creator(StockZTPool, name="StockZTPool")
StockZTPoolPrevious_Pydantic = pydantic_model_creator(StockZTPoolPrevious, name="StockZTPoolPrevious")
StockZTPoolStrong_Pydantic = pydantic_model_creator(StockZTPoolStrong, name="StockZTPoolStrong")
StockZTPoolDown_Pydantic = pydantic_model_creator(StockZTPoolDown, name="StockZTPoolDown")
StockHKHotRank_Pydantic = pydantic_model_creator(StockHKHotRank, name="StockHKHotRank")


class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100, description="分类名称")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="分类名称")


class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TagBase(BaseModel):
    name: str = Field(..., max_length=100, description="标签名称")


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="标签名称")


class Tag(TagBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    content: str = Field(..., description="评论内容")
    parent_id: Optional[int] = Field(None, description="父评论ID，用于回复功能")
    is_approved: bool = Field(True, description="是否已审核通过")


class CommentCreate(CommentBase):
    article_id: int = Field(..., description="所属文章ID")


class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, description="评论内容")
    is_approved: Optional[bool] = Field(None, description="是否已审核通过")


class Comment(CommentBase):
    id: int
    author_id: Optional[int] = Field(None, description="评论作者ID")
    article_id: int = Field(..., description="所属文章ID")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommentWithReplies(Comment):
    replies: List["CommentWithReplies"] = Field(default_factory=list, description="回复评论列表")


# 解决前向引用问题
CommentWithReplies.update_forward_refs()


class ArticleBase(BaseModel):
    title: str = Field(..., max_length=100, description="标题")
    slug: str = Field(..., max_length=100, description="文章标识")
    content: str = Field(..., description="内容")
    content_type: str = Field("markdown", max_length=10, description="内容类型")
    summary: Optional[str] = Field(None, description="摘要")
    status: str = Field("draft", max_length=10, description="状态")
    is_top: bool = Field(False, description="是否置顶")
    is_featured: bool = Field(False, description="是否精选")
    cover: Optional[str] = Field(None, max_length=500, description="封面")
    published_at: Optional[datetime] = Field(None, description="发布时间")
    category_id: Optional[int] = Field(None, description="分类ID")
    tag_ids: List[int] = Field(default_factory=list, description="标签ID列表")


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100, description="标题")
    slug: Optional[str] = Field(None, max_length=100, description="文章标识")
    content: Optional[str] = Field(None, description="内容")
    content_type: Optional[str] = Field(None, max_length=10, description="内容类型")
    summary: Optional[str] = Field(None, description="摘要")
    status: Optional[str] = Field(None, max_length=10, description="状态")
    is_top: Optional[bool] = Field(None, description="是否置顶")
    is_featured: Optional[bool] = Field(None, description="是否精选")
    cover: Optional[str] = Field(None, max_length=500, description="封面")
    published_at: Optional[datetime] = Field(None, description="发布时间")
    category_id: Optional[int] = Field(None, description="分类ID")
    tag_ids: Optional[List[int]] = Field(None, description="标签ID列表")


class Article(ArticleBase):
    id: int
    views: int = Field(0, description="浏览量")
    likes: int = Field(0, description="点赞数")
    comment_count: int = Field(0, description="评论数量")
    author_id: Optional[int] = Field(None, description="作者ID")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ArticleDetail(Article):
    category: Optional[Category] = Field(None, description="分类")
    tags: List[Tag] = Field(default_factory=list, description="标签列表")
    comments: List[Comment] = Field(default_factory=list, description="评论列表")


class ArticleList(BaseModel):
    articles: List[Article] = Field(default_factory=list, description="文章列表")
    total: int = Field(0, description="总数")
    page: int = Field(1, description="当前页码")
    size: int = Field(10, description="每页数量")


class ArticleIn(ArticleBase):
    """用于创建文章的输入模型"""
    pass


class ArticleOut(Article):
    """用于返回文章的输出模型"""
    pass


class Article2In(BaseModel):
    """Article2的输入模型，与ArticleIn相同，但保持命名一致性"""
    title: str = Field(..., max_length=100, description="标题")
    category: str = Field(..., max_length=100, description="分类")
    summary: Optional[str] = Field(None, description="摘要")
    cover: Optional[str] = Field(None, max_length=500, description="封面")
    tags: List[str] = Field(default_factory=list, description="标签")
    content: str = Field(..., description="内容")
    contentType: str = Field("markdown", max_length=10, description="内容类型")
    status: str = Field("draft", max_length=10, description="状态")
    author: str = Field(..., max_length=100, description="作者")


class Article2Out(Article):
    """Article2的输出模型，与ArticleOut相同，但保持命名一致性"""
    pass


class Article2Update(ArticleUpdate):
    """Article2的更新模型，与ArticleUpdate相同，但保持命名一致性"""
    pass


class Article2Detail(ArticleDetail):
    """Article2的详情模型，与ArticleDetail相同，但保持命名一致性"""
    pass


class Article2List(ArticleList):
    """Article2的列表模型，与ArticleList相同，但保持命名一致性"""
    pass


class ImageResponse(BaseModel):
    """图片上传响应模型"""
    url: str = Field(..., description="图片URL")
    uuid: Optional[str] = None
    success: bool = Field(True, description="是否成功")
    message: str = Field("上传成功", description="消息")
    id: int = Field(None, description="图片ID")
    filename: Optional[str] = Field(None, description="图片名称")


class ImageItem(BaseModel):
    """图片上传模型"""
    id: str = Field(..., description="图片ID")
    uuid: str
    original_name: str = Field(..., description="图片名称")
    filename: str
    url: str
    file_size: int
    content_type: str
    uploaded_at: datetime


class ImageListResponse(BaseModel):
    """图片列表响应模型"""
    items: List[ImageItem]
    total: int
    page: int
    size: int


from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any


class StrategyCreate(BaseModel):
    # 必填字段
    name: str = Field(..., min_length=1, max_length=100, description="策略名称")
    group_name: str = Field(..., description="策略组别")
    code: str = Field(..., description="策略代码")
    detail: str = Field(..., description="策略详细说明")

    # 可选字段
    icon: Optional[str] = Field(None, description="策略图标")
    introduction: Optional[str] = Field(None, max_length=200, description="策略简介")
    difficulty: Optional[str] = Field("初级", description="策略难度")
    risk_level: Optional[str] = Field("低", description="风险等级")
    expected_return: Optional[float] = Field(None, ge=-100, le=1000, description="预期收益率(%)")
    max_drawdown: Optional[float] = Field(None, ge=0, le=100, description="最大回撤(%)")
    sharpe_ratio: Optional[float] = Field(None, ge=-5, le=10, description="夏普比率")
    win_rate: Optional[float] = Field(None, ge=0, le=100, description="胜率(%)")
    holding_period: Optional[str] = Field("短期", description="持仓周期")

    # 列表字段
    market_conditions: Optional[List[str]] = Field(default_factory=list, description="市场条件")
    required_indicators: Optional[List[str]] = Field(default_factory=list, description="所需技术指标")
    tags: Optional[List[str]] = Field(default_factory=list, description="策略标签")
    # 修改这里：从字典数组改为字符串数组
    result_pic: Optional[List[str]] = Field(default_factory=list, description="结果图片URL列表")
    result_text: Optional[Dict[str, Any]] = Field(default_factory=dict, description="结果数据")

    # 控制字段
    publish: bool = Field(False, description="是否发布")
    review: bool = Field(False, description="是否需要审核")
    version: Optional[str] = Field("1.0", description="版本号")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "趋势跟踪策略",
                "group_name": "趋势类策略",
                "code": "# 策略代码...",
                "detail": "策略详细说明...",
                "icon": "bi-speedometer2",
                "introduction": "这是一个趋势跟踪策略",
                "difficulty": "中级",
                "risk_level": "中",
                "expected_return": 15.5,
                "max_drawdown": 20.5,
                "sharpe_ratio": 1.5,
                "win_rate": 65.0,
                "holding_period": "中期",
                "market_conditions": ["牛市", "震荡市"],
                "required_indicators": ["MA", "MACD"],
                "tags": ["趋势", "量化"],
                # 修改示例：使用字符串数组而不是字典数组
                "result_pic": ["http://example.com/image1.jpg"],
                "result_text": {"年化收益率": "18.7%", "最大回撤": "15.2%"},
                "publish": False,
                "review": False,
                "version": "1.0"
            }
        }

    @validator('difficulty')
    def validate_difficulty(cls, v):
        if v is not None and v not in ['初级', '中级', '高级']:
            raise ValueError('难度必须是初级、中级或高级')
        return v

    @validator('risk_level')
    def validate_risk_level(cls, v):
        if v is not None and v not in ['低', '中', '高']:
            raise ValueError('风险等级必须是低、中或高')
        return v

    @validator('holding_period')
    def validate_holding_period(cls, v):
        if v is not None and v not in ['短期', '中期', '长期']:
            raise ValueError('持仓周期必须是短期、中期或长期')
        return v

class StrategyResponse(BaseModel):
    id: int
    name: str
    group_name: str  # 确保这里是 group_name 而不是 group
    icon: Optional[str] = None
    introduction: Optional[str] = None
    difficulty: Optional[str] = None
    risk_level: Optional[str] = None
    expected_return: Optional[float] = None
    max_drawdown: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    win_rate: Optional[float] = None
    holding_period: Optional[str] = None
    market_conditions: Optional[List[str]] = None
    required_indicators: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    # 修改这里：从字典数组改为字符串数组
    result_pic: Optional[List[str]] = None
    result_text: Optional[Dict[str, Any]] = None
    publish: bool = False
    review: bool = False
    version: Optional[str] = None
    created_at: datetime
    # 如果数据库模型中没有 updated_at，移除这行

    class Config:
        orm_mode = True
