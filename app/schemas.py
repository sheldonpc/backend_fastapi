from typing import Optional, Annotated

from pydantic import BaseModel, EmailStr, constr, Field
from tortoise.contrib.pydantic import pydantic_model_creator

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

class ArticleCreate(BaseModel):
    title: TitleStr
    content: str
    is_published: Optional[bool] = True

class ArticleUpdate(BaseModel):
    title: Optional[constr(min_length=1, max_length=255)]
    content: Optional[str]
    is_published: Optional[bool]

class ArticleOut(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    is_published: bool
    created_at: str
    updated_at: str

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