from typing import List
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Depends, HTTPException, status, Request, Path
from pathlib import Path as LibPath
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from fastapi import Depends
from datetime import datetime, timedelta
import random
from app import models
from app.deps import get_current_admin
from app.models import User, Article, Category, Tag, Article_Pydantic, Category_Pydantic, Tag_Pydantic, Comment, \
    Comment_Pydantic, User_Pydantic
from app.schemas import UserOut
from tortoise.expressions import Q
from app.core.templates import templates

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

@router.get("/verify")
async def verify_admin(current_admin = Depends(get_current_admin)):
    return {"message": "Authorized", "user_id": current_admin.id, "role": current_admin.role}

@router.get("/")
async def admin_page(request: Request):
    # ✅ 不再校验权限，直接返回 HTML 页面
    # 前端 JS 会在加载后自动校验 /admin/verify
    return templates.TemplateResponse("admin/admin.html", {"request": request})

# ———————————————— 模拟统计数据接口 ————————————————
@router.get("/api/stats")
async def get_admin_stats(current_admin = Depends(get_current_admin)):
    """
    返回后台概览统计数据（模拟）
    """
    # 模拟最近7天用户增长数据
    today = datetime.today()
    user_growth = []
    for i in range(6, -1, -1):  # 最近7天
        date_str = (today - timedelta(days=i)).strftime("%m-%d")
        count = random.randint(10, 30)
        user_growth.append({"date": date_str, "count": count})

    return {
        "total_users": 1250,
        "total_articles": 89,
        "active_admins": 3,
        "pending_articles": 5,
        "user_growth_last_7_days": user_growth
    }

# ———————————————— 模拟操作日志接口 ————————————————
@router.get("/api/recent-logs")
async def get_recent_logs(current_admin = Depends(get_current_admin)):
    """
    返回最近操作日志（模拟）
    """
    now = datetime.now()
    return [
        {
            "action": "发布了新文章《FastAPI 最佳实践》",
            "user": "admin",
            "timestamp": (now - timedelta(hours=1)).isoformat()
        },
        {
            "action": "审核通过用户注册申请",
            "user": "editor",
            "timestamp": (now - timedelta(hours=3)).isoformat()
        },
        {
            "action": "禁用违规用户账号",
            "user": "moderator",
            "timestamp": (now - timedelta(hours=5)).isoformat()
        },
        {
            "action": "更新系统配置",
            "user": "superadmin",
            "timestamp": (now - timedelta(days=1, hours=2)).isoformat()
        },
        {
            "action": "备份数据库",
            "user": "system",
            "timestamp": (now - timedelta(days=1, hours=4)).isoformat()
        },
    ]
@router.get("/users_page")
async def admin_users(request: Request):
    users = await models.User.all()
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "title": "用户管理", "users": users}
    )

@router.get("/articles_page")
async def admin_articles(request: Request):
    articles = await models.Article.all().prefetch_related("author")
    return templates.TemplateResponse(
        "articles.html",
        {"request": request, "title": "文章管理", "articles": articles}
    )

# ------------------ 用户管理 ------------------
@router.get("/users", response_model=list[UserOut])
async def list_users(skip: int = 0, limit: int = 20):
    users = await User.all().offset(skip).limit(limit)
    return users

@router.post("/users/{user_id}/block")
async def block_user(user_id: int):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.is_active = False
    await user.save()
    return {"msg": f"用户 {user.username} 已被封禁"}

@router.post("/users/{user_id}/unblock")
async def unblock_user(user_id: int):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.is_active = True
    await user.save()
    return {"msg": f"用户 {user.username} 已被解封"}

# ------------------ 文章管理 ------------------
@router.get("/articles")
async def list_articles(skip: int = 0, limit: int = 20):
    articles = await Article.all().offset(skip).limit(limit)
    return [await Article_Pydantic.from_tortoise_orm(a) for a in articles]

@router.post("/articles/{article_id}/publish")
async def publish_article(article_id: int):
    article = await Article.get_or_none(id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    article.is_published = True
    await article.save()
    return {"msg": f"文章 '{article.title}' 已发布"}

@router.post("/articles/{article_id}/unpublish")
async def unpublish_article(article_id: int):
    article = await Article.get_or_none(id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    article.is_published = False
    await article.save()
    return {"msg": f"文章 '{article.title}' 已下架"}

# ------------------ 分类管理 ------------------
@router.get("/categories")
async def list_categories():
    categories = await Category.all()
    return [await Category_Pydantic.from_tortoise_orm(c) for c in categories]

@router.post("/categories")
async def create_category(name: str):
    category = await Category.create(name=name)
    return await Category_Pydantic.from_tortoise_orm(category)

# ------------------ 标签管理 ------------------
@router.get("/tags")
async def list_tags():
    tags = await Tag.all()
    return [await Tag_Pydantic.from_tortoise_orm(t) for t in tags]

@router.post("/tags")
async def create_tag(name: str):
    tag = await Tag.create(name=name)
    return await Tag_Pydantic.from_tortoise_orm(tag)

# ------------------ 评论管理 ------------------
@router.get("/comments")
async def list_comments(skip: int = 0, limit: int = 20, pending_only: bool = False):
    """
    列出评论
    - pending_only: True 只显示待审核评论
    """
    query = Comment.all().offset(skip).limit(limit)
    if pending_only:
        query = query.filter(is_approved=False)
    comments = await query
    return [await Comment_Pydantic.from_tortoise_orm(c) for c in comments]

@router.post("/comments/{comment_id}/approve")
async def approve_comment(comment_id: int = Path(..., description="评论ID")):
    comment = await Comment.get_or_none(id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    comment.is_approved = True
    await comment.save()
    return {"msg": "评论已审核通过"}

@router.post("/comments/{comment_id}/block")
async def block_comment(comment_id: int = Path(..., description="评论ID")):
    comment = await Comment.get_or_none(id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    comment.is_visible = False
    await comment.save()
    return {"msg": "评论已屏蔽"}

@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: int = Path(..., description="评论ID")):
    comment = await Comment.get_or_none(id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    await comment.delete()
    return {"msg": "评论已删除"}

# 获取所有用户信息
@router.get("/users", response_model=List[User_Pydantic])
async def get_all_users():
    users = await User.all()
    return await User_Pydantic.from_queryset(users)

# 禁用用户
@router.post("/users/{user_id}/disable")
async def disable_user(user_id: int):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.is_active = False
    await user.save()
    return {"msg": f"用户 {user.username} 已禁用"}
# 启用用户
@router.post("/users/{user_id}/enable")
async def enable_user(user_id: int):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.is_active = True
    await user.save()
    return {"msg": f"用户 {user.username} 已启用"}

