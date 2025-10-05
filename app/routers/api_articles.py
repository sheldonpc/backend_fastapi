from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from flask import Response
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from sqlalchemy.dialects.mssql.information_schema import views

from app.deps import get_current_admin, get_current_user
from app.models import Article2, Category2, Tag2
from app.schemas import Article2In, Article2Out

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
async def get_articles(current_admin=Depends(get_current_admin)):
    """获取文章列表"""
    return {"items": articles_data, "total": len(articles_data)}

@router.post("/", status_code=201)
async def create_article(article_data: Article2In, current_admin=Depends(get_current_admin)):
    # 获取分类
    category = await Category2.filter(cn_name=article_data.category).first()

    # 处理标签：确保所有标签都存在
    tag_instances = []
    for tag_name in article_data.tags:
        tag = await Tag2.filter(name=tag_name).first()
        if not tag:
            tag = await Tag2.create(name=tag_name)
        tag_instances.append(tag)

    # 生成唯一的slug
    base_slug = article_data.title.lower().replace(" ", "-")
    slug = base_slug
    counter = 1
    while await Article2.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    try:
        # 创建文章，完全不设置 tags
        article_obj = Article2(
            title=article_data.title,
            slug=slug,
            content=article_data.content,
            content_type=article_data.contentType,
            summary=article_data.summary,
            status=article_data.status,
            views=0,
            likes=0,
            is_top=False,
            is_featured=False,
            cover=article_data.cover,
            published_at=datetime.now(),
            comment_count=0,
            author=current_admin,
            category=category
            # 完全不包含 tags 字段
        )
        await article_obj.save()

        # 使用多对多管理器添加标签
        for tag in tag_instances:
            await article_obj.tags.add(tag)

        return Response({"message": "文章创建成功"})
    except Exception as e:
        print(f"Error occurred: {type(e).__name__}: {str(e)}")
        raise


@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
        article_id: str,
        article: ArticleUpdate,
        current_admin=Depends(get_current_admin)
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
async def delete_article(article_id: str, current_admin=Depends(get_current_admin)):
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
