from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import datetime

from app.deps import get_current_user
from app.models import User, Article2, Strategy, Comment2


router = APIRouter(prefix="/api", tags=["用户中心"])


# 用户相关接口
@router.get("/user/profile")
async def get_user_profile(request: Request, current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")

    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "pen_name": current_user.pen_name,
        "avatar_url": current_user.avatar_url,
        "role": current_user.role,
        "created_at": current_user.created_at.isoformat(),
        "bio": "这个人很懒，还没有填写个人简介..."  # 可以从用户模型中添加bio字段
    }


@router.put("/user/profile")
async def update_user_profile(
        request: Request,
        current_user: User = Depends(get_current_user)
):
    """更新用户信息"""
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")

    data = await request.json()

    # 更新用户信息
    if "pen_name" in data:
        current_user.pen_name = data["pen_name"]
    # if "email" in data:
    #     current_user.email = data["email"]
    if "avatar_url" in data:
        current_user.avatar_url = data["avatar_url"]

    await current_user.save()

    return {"message": "个人信息更新成功"}


# 文章相关接口
@router.get("/user/articles")
async def get_user_articles(
        request: Request,
        page: int = 1,
        limit: int = 10,
        current_user: User = Depends(get_current_user)
):
    """获取用户文章列表"""
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")

    # 获取用户文章总数
    total = await Article2.filter(author_id=current_user.id).count()

    # 分页获取文章
    offset = (page - 1) * limit
    articles = await Article2.filter(author_id=current_user.id).offset(offset).limit(limit).order_by("-created_at")

    # 转换为字典格式
    articles_data = []
    for article in articles:
        articles_data.append({
            "id": article.id,
            "title": article.title,
            "slug": article.slug,
            "summary": article.summary,
            "content": article.content[:200] + "..." if len(article.content) > 200 else article.content,
            "status": article.status,
            "views": article.views,
            "likes": article.likes,
            "comment_count": article.comment_count,
            "created_at": article.created_at.isoformat(),
            "updated_at": article.updated_at.isoformat()
        })

    return {
        "items": articles_data,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.delete("/articles/{article_id}")
async def delete_article(
        article_id: int,
        request: Request,
        current_user: User = Depends(get_current_user)
):
    """删除文章"""
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")

    # 查找文章
    article = await Article2.filter(id=article_id, author_id=current_user.id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在或无权限删除")

    # 删除文章
    await article.delete()

    return {"message": "文章删除成功"}


# 策略相关接口
@router.get("/user/strategies")
async def get_user_strategies(
        request: Request,
        page: int = 1,
        limit: int = 10,
        current_user: User = Depends(get_current_user)
):
    """获取用户策略列表"""
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")

    # 获取用户策略总数
    total = await Strategy.filter(author_id=current_user.id).count()

    # 分页获取策略
    offset = (page - 1) * limit
    strategies = await Strategy.filter(author_id=current_user.id).offset(offset).limit(limit).order_by("-created_at")

    # 转换为字典格式
    strategies_data = []
    for strategy in strategies:
        strategies_data.append({
            "id": strategy.id,
            "name": strategy.name,
            "group_name": strategy.group_name,
            "introduction": strategy.introduction,
            "icon": strategy.icon,
            "publish": strategy.publish,
            "review": strategy.review,
            "view_count": strategy.view_count,
            "like_count": strategy.like_count,
            "created_at": strategy.created_at.isoformat(),
            "published_at": strategy.published_at.isoformat() if strategy.published_at else None
        })

    return {
        "items": strategies_data,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.delete("/strategies/{strategy_id}")
async def delete_strategy(
        strategy_id: int,
        request: Request,
        current_user: User = Depends(get_current_user)
):
    """删除策略"""
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")

    # 查找策略
    strategy = await Strategy.filter(id=strategy_id, author_id=current_user.id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在或无权限删除")

    # 删除策略
    await strategy.delete()

    return {"message": "策略删除成功"}


# 评论相关接口
@router.get("/user/comments")
async def get_user_comments(
        request: Request,
        page: int = 1,
        limit: int = 10,
        current_user: User = Depends(get_current_user)
):
    """获取用户评论列表"""
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")

    # 获取用户评论总数
    total = await Comment2.filter(author_id=current_user.id).count()

    # 分页获取评论
    offset = (page - 1) * limit
    comments = await Comment2.filter(author_id=current_user.id).offset(offset).limit(limit).order_by(
        "-created_at").prefetch_related("article")

    # 转换为字典格式
    article_id = None
    comments_data = []
    for comment in comments:
        article_title = "已删除的文章"
        if comment.article:
            article_title = comment.article.title
            article_id = comment.article.id

        comments_data.append({
            "id": comment.id,
            "content": comment.content,
            "article": {
                "id": article_id,
                "title": article_title
            } if comment.article else None,
            "is_approved": comment.is_approved,
            "created_at": comment.created_at.isoformat(),
            "updated_at": comment.updated_at.isoformat()
        })

    return {
        "items": comments_data,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/comments/{comment_id}")
async def get_comment(
        comment_id: int,
        request: Request,
        current_user: User = Depends(get_current_user)
):
    """获取单个评论详情"""
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")

    # 查找评论
    comment = await Comment2.filter(id=comment_id, author_id=current_user.id).first().prefetch_related("article")
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在或无权限访问")

    article_title = "已删除的文章"
    article_id = None
    if comment.article:
        article_title = comment.article.title
        article_id = comment.article.id

    return {
        "id": comment.id,
        "content": comment.content,
        "article": {
            "id": article_id,
            "title": article_title
        } if comment.article else None,
        "is_approved": comment.is_approved,
        "created_at": comment.created_at.isoformat(),
        "updated_at": comment.updated_at.isoformat()
    }


@router.put("/comments/{comment_id}")
async def update_comment(
        comment_id: int,
        request: Request,
        current_user: User = Depends(get_current_user)
):
    """更新评论"""
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")

    # 查找评论
    comment = await Comment2.filter(id=comment_id, author_id=current_user.id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在或无权限修改")

    # 获取更新数据
    data = await request.json()
    if "content" not in data or not data["content"].strip():
        raise HTTPException(status_code=400, detail="评论内容不能为空")

    # 更新评论
    comment.content = data["content"]
    comment.updated_at = datetime.now()
    await comment.save()

    return {"message": "评论更新成功"}


@router.delete("/comments/{comment_id}")
async def delete_comment(
        comment_id: int,
        request: Request,
        current_user: User = Depends(get_current_user)
):
    """删除评论"""
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")

    # 查找评论
    comment = await Comment2.filter(id=comment_id, author_id=current_user.id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在或无权限删除")

    # 删除评论
    await comment.delete()

    return {"message": "评论删除成功"}