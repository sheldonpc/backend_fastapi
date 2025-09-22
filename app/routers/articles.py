from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from tortoise.expressions import Q

from app import schemas, models
from app.deps import get_current_user

router = APIRouter(prefix="/articles", tags=["article"])

# 创建文章
@router.post("/", response_model=schemas.ArticleOut)
async def create_article(article: schemas.ArticleCreate, current_user = Depends(get_current_user)):
    article_obj = await models.Article.create(
        title=article.title,
        content=article.content,
        author_id=current_user.id,
        is_published=article.is_published
    )
    return await schemas.ArticleOut.from_tortoise_orm(article_obj)

# 修改文章
@router.put("/{article_id}", response_model=schemas.ArticleOut)
async def update_article(article_id: int, article: schemas.ArticleUpdate, current_user = Depends(get_current_user)):
    article_obj = await models.Article.get_or_none(id=article_id, author_id=current_user.id)
    if not article_obj:
        raise HTTPException(status_code=404, detail="Article not found")
    article_data = article.dict(exclude_unset=True)
    for key, value in article_data.items():
        setattr(article_obj, key, value)
    await article_obj.save()
    return await schemas.ArticleOut.from_tortoise_orm(article_obj)

# 删除文章
@router.delete("/{article_id}")
async def delete_article(article_id: int, current_user = Depends(get_current_user)):
    article_obj = await models.Article.get_or_none(id=article_id, author_id=current_user.id)
    if not article_obj:
        raise HTTPException(status_code=404, detail="Article not found")
    await article_obj.delete()
    return {"msg": "Article deleted successfully"}

# 列表分页
@router.get("/", response_model=List[schemas.ArticleOut])
async def list_articles(page: int = 1, limit: int = 10):
    offset = (page - 1) * limit
    articles = await models.Article.all().offset(offset).limit(limit).order_by("-created_at")
    return await schemas.ArticleOut.from_queryset(articles)

# 查看文章详情
@router.get("/{article_id}", response_model=schemas.ArticleOut)
async def get_article(article_id: int):
    article_obj = await models.Article.get_or_none(id=article_id)
    if not article_obj:
        raise HTTPException(status_code=404, detail="Article not found")
    return await schemas.ArticleOut.from_tortoise_orm(article_obj)

@router.get("/search", response_model=List[models.Article_Pydantic])
async def search_articles(query: str=Query(..., min_length=3, max_length=50, description="搜索关键字")):
    articles = await models.Article.filter(
        Q(title__contains=query) | Q(content__contains=query),
        is_published=True
    )
    if not articles:
        raise HTTPException(status_code=404, detail="No articles found")
    else:
        return await models.Article_Pydantic.from_queryset(articles)
    #         Returns a serializable pydantic model instance that contains a list of models,
    #         from the provided queryset.