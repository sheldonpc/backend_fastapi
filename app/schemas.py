from typing import Optional, Annotated

from pydantic import BaseModel, EmailStr, constr, Field
from tortoise.contrib.pydantic import pydantic_model_creator

from app.models import Comment, ArticleLike, CommentLike, ArticleFavorite, FinancialNews, SentimentAnalysis, IndexData


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

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
