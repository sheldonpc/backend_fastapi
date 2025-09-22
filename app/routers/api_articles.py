from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from app.deps import get_current_admin

# 模拟数据存储（内存中，非持久化）
articles_data = [
    {
        "id": str(uuid.uuid4()),
        "title": "前端开发最佳实践",
        "author": "张三",
        "category": "技术分享",
        "status": "published",
        "tags": ["前端", "JavaScript"],
        "content": "这是一篇关于前端开发的文章内容...",
        "created_at": "2025-09-22T10:00:00Z",
        "views": 150
    },
    {
        "id": str(uuid.uuid4()),
        "title": "React Hooks 详解",
        "author": "李四",
        "category": "技术分享",
        "status": "draft",
        "tags": ["React"],
        "content": "React Hooks的详细解释...",
        "created_at": "2025-09-21T14:30:00Z",
        "views": 0
    }
]


# Pydantic 模型定义
class ArticleCreate(BaseModel):
    title: str
    author: str
    category: str
    status: str  # "draft" or "published"
    tags: Optional[List[str]] = []
    content: str


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    content: Optional[str] = None


class ArticleResponse(BaseModel):
    id: str
    title: str
    author: str
    category: str
    status: str
    tags: List[str]
    content: str
    created_at: str
    views: int

    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    items: List[ArticleResponse]
    total: int


# 路由器定义
router = APIRouter(prefix="/admin/api/articles", tags=["api_articles"])

# 简单 Token 验证依赖（模拟，实际应使用 JWT 等）
security = HTTPBearer()



@router.get("/", response_model=ArticleListResponse)
async def get_articles(current_admin = Depends(get_current_admin)):
    """获取文章列表"""
    return {"items": articles_data, "total": len(articles_data)}


@router.post("/", response_model=ArticleResponse, status_code=201)
async def create_article(article: ArticleCreate,current_admin = Depends(get_current_admin)):
    """创建文章"""
    if not article.title or not article.author or not article.category or not article.content:
        raise HTTPException(
            status_code=400,
            detail="缺少必填字段"
        )

    new_article = {
        "id": str(uuid.uuid4()),
        "title": article.title,
        "author": article.author,
        "category": article.category,
        "status": article.status,
        "tags": article.tags,
        "content": article.content,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "views": 0
    }
    articles_data.append(new_article)
    return new_article


@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
        article_id: str,
        article: ArticleUpdate,
        current_admin = Depends(get_current_admin)
):
    """更新文章"""
    for item in articles_data:
        if item["id"] == article_id:
            if article.title is not None:
                item["title"] = article.title
            if article.author is not None:
                item["author"] = article.author
            if article.category is not None:
                item["category"] = article.category
            if article.status is not None:
                item["status"] = article.status
            if article.tags is not None:
                item["tags"] = article.tags
            if article.content is not None:
                item["content"] = article.content
            return item

    raise HTTPException(status_code=404, detail="文章不存在")


@router.delete("/{article_id}", status_code=204)
async def delete_article(article_id: str, current_admin = Depends(get_current_admin)):
    """删除文章"""
    for index, item in enumerate(articles_data):
        if item["id"] == article_id:
            if item["status"] == "published":
                raise HTTPException(
                    status_code=400,
                    detail="发布中的文章不可删除"
                )
            articles_data.pop(index)
            return None
    raise HTTPException(status_code=404, detail="文章不存在")