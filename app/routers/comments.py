from fastapi import APIRouter, Depends, HTTPException
from app import models, schemas
from app.deps import get_current_user

router = APIRouter(prefix="/comments", tags=["comments"])

# 发表评论
@router.post("/")
async def create_comment(
    data: schemas.CommentIn_Pydantic,
    current_user = Depends(get_current_user)
):
    comment = await models.Comment.create(
        content=data.content,
        author=current_user,
        article_id=data.article_id
    )
    return await schemas.Comment_Pydantic.from_tortoise_orm(comment)

# 获取文章评论（单级，分页）
@router.get("/article/{article_id}")
async def get_article_comments(article_id: int, skip: int = 0, limit: int = 20):
    comments = await models.Comment.filter(
        article_id=article_id,
        is_visible=True
    ).offset(skip).limit(limit)
    return await schemas.Comment_Pydantic.from_queryset(comments)
