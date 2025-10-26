from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from app.deps import get_current_admin, get_current_user, get_current_registered_user
from app.models import Article2, Category2, Tag2, User
from app.schemas import Article2In, Article2Out
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.queryset import QuerySet

# 创建Article2的Pydantic模型
Article2_Pydantic = pydantic_model_creator(Article2, name="Article2", exclude=["author", "category", "tags"])
Article2_Pydantic_List = pydantic_model_creator(Article2, name="Article2List", exclude=["author", "category", "tags", "content"])

# 创建自定义响应模型，包含关联数据
class ArticleResponse(BaseModel):
    id: int
    title: str
    slug: str
    content: str
    content_type: str
    summary: Optional[str]
    status: str
    views: int
    likes: int
    is_top: bool
    is_featured: bool
    cover: Optional[str]
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    comment_count: int
    author: Optional[str]
    category: Optional[str]
    tags: List[str]

class ArticleListResponse(BaseModel):
    items: List[ArticleResponse]
    total: int
    page: int
    size: int


# 路由器定义
router = APIRouter(prefix="/admin/api/articles", tags=["api_articles"])

# 简单 Token 验证依赖（模拟，实际应使用 JWT 等）
security = HTTPBearer()


@router.get("/", response_model=ArticleListResponse)
async def get_articles(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="文章状态筛选"),
    category: Optional[str] = Query(None, description="分类筛选"),
    current_admin=Depends(get_current_admin)
):
    """获取文章列表"""
    # 构建查询
    query = Article2.all().prefetch_related('author', 'category', 'tags')
    
    # 应用筛选条件
    if status:
        query = query.filter(status=status)
    if category:
        query = query.filter(category__cn_name=category)
    
    # 计算总数
    total = await query.count()
    
    # 分页查询
    offset = (page - 1) * size
    articles = await query.offset(offset).limit(size)
    
    # 构建返回数据
    result = []
    for article in articles:
        # 获取标签列表
        tag_list = [tag.name for tag in await article.tags.all()]
        
        # 创建响应对象
        article_response = ArticleResponse(
            id=article.id,
            title=article.title,
            slug=article.slug,
            content=article.content,
            content_type=article.content_type,
            summary=article.summary,
            status=article.status,
            views=article.views,
            likes=article.likes,
            is_top=article.is_top,
            is_featured=article.is_featured,
            cover=article.cover,
            created_at=article.created_at,
            updated_at=article.updated_at,
            published_at=article.published_at,
            comment_count=article.comment_count,
            author=article.author.username if article.author else None,
            category=article.category.cn_name if article.category else None,
            tags=tag_list
        )
        result.append(article_response)
    
    return ArticleListResponse(
        items=result,
        total=total,
        page=page,
        size=size
    )

@router.post("/", response_model=dict)
async def create_article(article_data: Article2In, current_admin=Depends(get_current_registered_user)):
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
            status="draft",
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

        # 获取标签列表
        tag_list = [tag.name for tag in await article_obj.tags.all()]
        
        # 创建响应对象
        article_response = ArticleResponse(
            id=article_obj.id,
            title=article_obj.title,
            slug=article_obj.slug,
            content=article_obj.content,
            content_type=article_obj.content_type,
            summary=article_obj.summary,
            status=article_obj.status,
            views=article_obj.views,
            likes=article_obj.likes,
            is_top=article_obj.is_top,
            is_featured=article_obj.is_featured,
            cover=article_obj.cover,
            created_at=article_obj.created_at,
            updated_at=article_obj.updated_at,
            published_at=article_obj.published_at,
            comment_count=article_obj.comment_count,
            author=article_obj.author.username if article_obj.author else None,
            category=article_obj.category.cn_name if article_obj.category else None,
            tags=tag_list
        )
        
        return {"message": "文章创建成功", "article": article_response}
    except Exception as e:
        print(f"Error occurred: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建文章失败: {str(e)}")


@router.put("/{article_id}", response_model=dict)
async def update_article(
        article_id: int,
        article_data: Article2In,
        current_admin=Depends(get_current_admin)
):
    """更新文章"""
    # 查找文章
    article = await Article2.get_or_none(id=article_id).prefetch_related('author', 'category', 'tags')
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 获取分类
    category = await Category2.filter(cn_name=article_data.category).first()
    
    # 处理标签：确保所有标签都存在
    tag_instances = []
    for tag_name in article_data.tags:
        tag = await Tag2.filter(name=tag_name).first()
        if not tag:
            tag = await Tag2.create(name=tag_name)
        tag_instances.append(tag)
    
    try:
        # 更新文章字段
        article.title = article_data.title
        article.content = article_data.content
        article.content_type = article_data.contentType
        article.summary = article_data.summary
        article.status = article_data.status
        article.cover = article_data.cover
        article.category = category
        
        # 如果状态从draft变为published，设置发布时间
        if article.status == "published" and not article.published_at:
            article.published_at = datetime.now()
        
        await article.save()
        
        # 更新标签
        await article.tags.clear()
        for tag in tag_instances:
            await article.tags.add(tag)
        
        # 获取标签列表
        tag_list = [tag.name for tag in await article.tags.all()]
        
        # 创建响应对象
        article_response = ArticleResponse(
            id=article.id,
            title=article.title,
            slug=article.slug,
            content=article.content,
            content_type=article.content_type,
            summary=article.summary,
            status=article.status,
            views=article.views,
            likes=article.likes,
            is_top=article.is_top,
            is_featured=article.is_featured,
            cover=article.cover,
            created_at=article.created_at,
            updated_at=article.updated_at,
            published_at=article.published_at,
            comment_count=article.comment_count,
            author=article.author.username if article.author else None,
            category=article.category.cn_name if article.category else None,
            tags=tag_list
        )
        
        return {"message": "文章更新成功", "article": article_response}
    except Exception as e:
        print(f"Error occurred: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新文章失败: {str(e)}")


@router.delete("/{article_id}", response_model=dict)
async def delete_article(article_id: int, current_admin=Depends(get_current_admin)):
    """删除文章"""
    # 查找文章
    article = await Article2.get_or_none(id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 检查文章状态
    if article.status == "published":
        raise HTTPException(
            status_code=400,
            detail="发布中的文章不可删除"
        )
    
    try:
        # 删除文章
        await article.delete()
        return {"message": "文章删除成功"}
    except Exception as e:
        print(f"Error occurred: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除文章失败: {str(e)}")
