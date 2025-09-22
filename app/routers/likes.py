from fastapi import APIRouter, Depends, HTTPException, status
from app.models import Article, Comment, ArticleLike, CommentLike, ArticleFavorite
from app.schemas import ArticleLike_Pydantic, CommentLike_Pydantic, ArticleFavorite_Pydantic
from app.deps import get_current_user

router = APIRouter(prefix="/interactions", tags=["interactions"])

# 点赞文章
@router.post("/article/{article_id}/like")
async def like_article(article_id: int, current_user = Depends(get_current_user)):
    article = await Article.get_or_none(id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    obj, created = await ArticleLike.get_or_create(user=current_user, article=article)
    if not created:
        # 已经点赞 -> 取消点赞
        await obj.delete()
        return {"msg": "取消点赞"}

    return {"msg": "点赞成功"}

# 点赞评论
@router.post("/comment/{comment_id}/like")
async def like_comment(comment_id: int, current_user = Depends(get_current_user)):
    comment = await Comment.get_or_none(id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    obj, created = await CommentLike.get_or_create(user=current_user, comment=comment)
    if not created:
        await obj.delete()
        return {"msg": "取消点赞"}

    return {"msg": "点赞成功"}

# 收藏文章
@router.post("/article/{article_id}/favorite")
async def favorite_article(article_id: int, current_user = Depends(get_current_user)):
    article = await Article.get_or_none(id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    obj, created = await ArticleFavorite.get_or_create(user=current_user, article=article)
    if not created:
        await obj.delete()
        return {"msg": "取消收藏"}

    return {"msg": "收藏成功"}
