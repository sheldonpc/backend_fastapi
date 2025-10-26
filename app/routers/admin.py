from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request, Path
from fastapi import Depends
from datetime import datetime, timedelta
import random
import asyncio
from tortoise.expressions import Q
from app import models
from app.deps import get_current_admin, get_current_user, require_admin_cookie, oauth2_scheme
from app.exceptions import PermissionDenied
from app.models import User, Article, Category, Tag, Article_Pydantic, Category_Pydantic, Tag_Pydantic, Comment, \
    Comment_Pydantic, User_Pydantic
from app.schemas import UserOut
from app.core.templates import templates
from app.routers import admin_messages
from app.services.market_data_service import fetch_eastmoney_history_market_data, crawl_llm_insight, news_ai_summary
import psutil

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

@router.get("/verify")
async def verify_admin(current_admin = Depends(get_current_admin)):
    return {"message": "Authorized", "user_id": current_admin.id, "role": current_admin.role}


@router.get("/verify-cookie")
async def verify_admin_cookie(current_admin = Depends(require_admin_cookie)):
    """基于Cookie的管理员权限验证接口"""
    return {"message": "Authorized", "user_id": current_admin.id, "role": current_admin.role}

@router.get("/")
async def admin_page(
    request: Request,
    current_user = Depends(require_admin_cookie)  # 使用页面管理员验证
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="您没有管理员权限"
        )
    return templates.TemplateResponse("admin/admin.html", {"request": request, "current_user": current_user})

# ———————————————— 系统概览数据接口 ————————————————
@router.get("/api/overview")
async def get_overview_stats(current_admin = Depends(get_current_admin)):
    """
    返回后台概览统计数据（从数据库获取）
    """
    # 获取总用户数
    total_users = await User.all().count()
    
    # 获取文章总数（使用Article2模型）
    total_articles = await models.Article2.all().count()
    
    # 获取活跃管理员数（角色为admin或superadmin的用户）
    active_admins = await User.filter(role__in=["admin", "superadmin"], is_active=True).count()
    
    # 获取待审核文章数（状态为draft的文章）
    pending_articles = await models.Article2.filter(status="draft").count()
    
    # 获取最近7天用户增长数据
    today = datetime.today()
    user_growth = []
    for i in range(6, -1, -1):  # 最近7天
        date_str = (today - timedelta(days=i)).strftime("%m-%d")
        start_date = today - timedelta(days=i)
        end_date = start_date + timedelta(days=1)
        # 计算当天注册的用户数
        count = await User.filter(
            created_at__gte=start_date,
            created_at__lt=end_date
        ).count()
        user_growth.append({"date": date_str, "count": count})

    return {
        "total_users": total_users,
        "total_articles": total_articles,
        "active_admins": active_admins,
        "pending_articles": pending_articles,
        "user_growth_last_7_days": user_growth
    }

@router.get("/api/overview/logs")
async def get_overview_logs(current_admin = Depends(get_current_admin)):
    """
    返回最近操作日志（从数据库获取）
    """
    logs = []
    
    # 获取最近发布的文章
    recent_articles = await models.Article2.all().order_by("-created_at").limit(3)
    for article in recent_articles:
        # 获取作者信息
        author = await article.author if article.author else None
        author_name = author.username if author else "未知"
        
        # 根据文章状态确定操作类型
        action = f"创建了文章《{article.title}》"
        if article.status == "published":
            action = f"发布了文章《{article.title}》"
        elif article.status == "draft":
            action = f"创建了草稿《{article.title}》"
            
        logs.append({
            "action": action,
            "user": author_name,
            "timestamp": article.created_at.isoformat() if article.created_at else None
        })
    
    # 获取最近注册的用户
    recent_users = await User.all().order_by("-created_at").limit(2)
    for user in recent_users:
        logs.append({
            "action": f"用户 {user.username} 注册",
            "user": "系统",
            "timestamp": user.created_at.isoformat() if user.created_at else None
        })
    
    # 按时间戳排序
    logs.sort(key=lambda x: x["timestamp"] if x["timestamp"] else "", reverse=True)
    
    return logs[:5]  # 只返回最新的5条记录
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

@router.get("/statistics_page")
async def admin_statistics(request: Request, current_user = Depends(require_admin_cookie)):
    """
    数据统计页面
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="您没有管理员权限"
        )
    return templates.TemplateResponse(
        "admin/statistics.html",
        {"request": request, "current_user": current_user, "title": "数据统计"}
    )

# ------------------ 用户管理 ------------------
@router.get("/users/simple", response_model=list[UserOut])
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


@router.get("/articles/new")
async def new_article(request: Request):
    return templates.TemplateResponse(
        "admin/article_edit.html",
        {"request": request, "title": "新建文章"}
    )

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

# 获取用户列表（支持分页和搜索）
@router.get("/api/users")
async def get_users_with_pagination(
    page: int = 1,
    page_size: int = 10,
    search: str = None,
    current_admin = Depends(get_current_admin)
):
    """
    获取用户列表，支持分页和搜索功能
    用于用户选择模态框
    """
    # 构建查询条件
    query = User.all()
    
    # 如果有搜索条件，添加搜索过滤
    if search:
        query = query.filter(
            Q(username__icontains=search) | Q(email__icontains=search)
        )
    
    # 计算总数
    total = await query.count()
    
    # 应用分页
    offset = (page - 1) * page_size
    users = await query.offset(offset).limit(page_size)
    
    # 转换为字典格式
    user_list = []
    for user in users:
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        user_list.append(user_dict)
    
    return {
        "items": user_list,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }

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

# 引入消息管理路由


# ———————————————— 系统状态监控接口 ————————————————

@router.get("/api/system-status")
async def get_system_status(current_admin = Depends(get_current_admin)):
    """
    返回系统资源状态信息
    """
    import psutil
    import platform
    from datetime import datetime
    
    try:
        # CPU信息
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # 内存信息
        memory = psutil.virtual_memory()
        
        # 磁盘信息
        disk = psutil.disk_usage('/')
        
        # 网络信息 - 获取当前网络IO数据
        network = psutil.net_io_counters()
        
        # 系统信息
        boot_time = psutil.boot_time()
        boot_time_datetime = datetime.fromtimestamp(boot_time)
        
        # 系统负载
        load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
        
        # 获取上一次的网络数据（用于计算速率）
        # 这里使用简单的全局变量存储，实际应用中应使用数据库或缓存
        current_time = datetime.now()
        
        if not hasattr(get_system_status, 'last_network_data'):
            # 第一次调用，初始化数据
            get_system_status.last_network_data = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'timestamp': current_time
            }
            bytes_sent_per_sec = 0
            bytes_recv_per_sec = 0
        else:
            last_data = get_system_status.last_network_data
            time_diff = (current_time - last_data['timestamp']).total_seconds()
            
            # 确保时间差至少为1秒，避免除零错误
            if time_diff >= 1:
                bytes_sent_per_sec = (network.bytes_sent - last_data['bytes_sent']) / time_diff
                bytes_recv_per_sec = (network.bytes_recv - last_data['bytes_recv']) / time_diff
            else:
                # 时间间隔太短，使用上一次的值
                bytes_sent_per_sec = getattr(get_system_status, 'last_bytes_sent_per_sec', 0)
                bytes_recv_per_sec = getattr(get_system_status, 'last_bytes_recv_per_sec', 0)
                
            # 更新上一次的数据
            get_system_status.last_network_data = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'timestamp': current_time
            }
            
            # 保存上一次的速率值
            get_system_status.last_bytes_sent_per_sec = bytes_sent_per_sec
            get_system_status.last_bytes_recv_per_sec = bytes_recv_per_sec
        
        return {
            "cpu": {
                "percent": cpu_percent,
                "cores": cpu_count,
                "frequency": f"{cpu_freq.current:.2f} MHz" if cpu_freq else "N/A"
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "bytes_sent_per_sec": bytes_sent_per_sec,
                "bytes_recv_per_sec": bytes_recv_per_sec,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            },
            "system": {
                "os": platform.platform(),
                "architecture": platform.architecture()[0],
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "uptime": str(datetime.now() - boot_time_datetime).split('.')[0],
                "boot_time": boot_time
            },
            "load": {
                "load_1m": load_avg[0],
                "load_5m": load_avg[1],
                "load_15m": load_avg[2]
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"获取系统状态失败: {str(e)}"}


@router.get("/api/api-status")
async def get_api_status(
    current_admin = Depends(get_current_admin), 
    request: Request = None,
    token: str = Depends(oauth2_scheme)
):
    """
    返回各个API接口状态
    """
    from datetime import datetime, timedelta
    import asyncio
    import time
    import httpx
    
    # API接口列表
    api_endpoints = [
        {"name": "用户管理", "path": "/admin/api/users", "method": "GET"},
        {"name": "文章管理", "path": "/admin/api/articles", "method": "GET"},
        {"name": "系统配置", "path": "/admin/api/config", "method": "GET"},
        {"name": "财经数据", "path": "/api/index", "method": "GET"},
        {"name": "市场状态", "path": "/financial/market/status", "method": "GET"},
        {"name": "调度器状态", "path": "/financial/scheduler/status", "method": "GET"},
    ]
    
    # 获取当前请求的基础URL
    base_url = str(request.base_url) if request else "http://localhost:8000"
    
    # 检查API状态
    api_status = []
    
    # 创建HTTP客户端
    timeout = httpx.Timeout(5.0)  # 5秒超时
    async with httpx.AsyncClient(timeout=timeout) as client:
        for api in api_endpoints:
            try:
                # 记录开始时间
                start_time = time.time()
                
                # 构建完整URL，避免双斜杠问题
                # 如果base_url以斜杠结尾且api['path']以斜杠开头，需要去掉一个斜杠
                if base_url.endswith('/') and api['path'].startswith('/'):
                    url = f"{base_url[:-1]}{api['path']}"
                elif not base_url.endswith('/') and not api['path'].startswith('/'):
                    url = f"{base_url}/{api['path']}"
                else:
                    url = f"{base_url}{api['path']}"
                
                # 发送真实请求到接口
                headers = {"Authorization": f"Bearer {token}"}
                
                if api["method"] == "GET":
                    response = await client.get(url, headers=headers)
                elif api["method"] == "POST":
                    response = await client.post(url, headers=headers)
                else:
                    response = await client.request(api["method"], url, headers=headers)
                
                # 计算响应时间（毫秒）
                response_time = round((time.time() - start_time) * 1000, 2)
                
                # 根据HTTP状态码确定接口状态
                if response.status_code < 400:
                    status = "healthy"
                elif response.status_code < 500:
                    status = "warning"
                else:
                    status = "error"
                    
            except Exception as e:
                # 请求异常
                status = "error"
                response_time = 9999  # 表示超时或连接错误
                print(f"API检查错误 {api['path']}: {str(e)}")
            
            api_status.append({
                "name": api["name"],
                "path": api["path"],
                "method": api["method"],
                "status": status,
                "response_time": response_time,
                "last_check": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    
    return {
        "apis": api_status,
        "total_count": len(api_status),
        "healthy_count": sum(1 for api in api_status if api["status"] == "healthy"),
        "timestamp": datetime.now().isoformat()
    }


@router.get("/api/system-load")
async def get_system_load_history(current_admin = Depends(get_current_admin)):
    """
    返回系统负载历史数据
    """
    import psutil
    from datetime import datetime, timedelta
    import random
    
    # 生成过去24小时的负载数据（每小时的模拟数据）
    load_history = []
    now = datetime.now()
    
    for i in range(24):
        hour_time = now - timedelta(hours=i)
        # 模拟CPU和内存使用率
        cpu_usage = 20 + random.random() * 60  # 20-80%之间
        memory_usage = 40 + random.random() * 40  # 40-80%之间
        
        load_history.append({
            "timestamp": hour_time.isoformat(),
            "cpu_percent": round(cpu_usage, 2),
            "memory_percent": round(memory_usage, 2)
        })
    
    # 反转列表，使时间从早到晚
    load_history.reverse()
    
    return load_history


# ———————————————— 手动定时任务API ————————————————

@router.post("/api/tasks/run/{task_name}")
async def run_scheduled_task(task_name: str, current_admin = Depends(get_current_admin)):
    """
    手动执行指定的定时任务
    """
    task_functions = {
        "fetch_eastmoney_history_market_data": fetch_eastmoney_history_market_data,
        "crawl_llm_insight": crawl_llm_insight,
        "news_ai_summary": news_ai_summary
    }
    
    if task_name not in task_functions:
        raise HTTPException(status_code=404, detail=f"任务 '{task_name}' 不存在")
    
    try:
        # 执行任务
        await task_functions[task_name]()
        return {
            "success": True,
            "message": f"任务 '{task_name}' 执行成功",
            "task_name": task_name,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"任务 '{task_name}' 执行失败: {str(e)}",
            "task_name": task_name,
            "timestamp": datetime.now().isoformat()
        }


@router.post("/api/tasks/run-all")
async def run_all_scheduled_tasks(current_admin = Depends(get_current_admin)):
    """
    按顺序执行所有定时任务，包含随机延迟
    """
    tasks = [
        ("fetch_eastmoney_history_market_data", fetch_eastmoney_history_market_data),
        ("crawl_llm_insight", crawl_llm_insight),
        ("news_ai_summary", news_ai_summary)
    ]
    
    results = []
    
    try:
        # 执行第一个任务
        task_name, task_func = tasks[0]
        await task_func()
        results.append({
            "task_name": task_name,
            "success": True,
            "message": f"任务 '{task_name}' 执行成功"
        })
        
        # 第一个延迟：5-10秒
        delay1 = random.uniform(5, 10)
        await asyncio.sleep(delay1)
        
        # 执行第二个任务
        task_name, task_func = tasks[1]
        await task_func()
        results.append({
            "task_name": task_name,
            "success": True,
            "message": f"任务 '{task_name}' 执行成功",
            "previous_delay": round(delay1, 2)
        })
        
        # 第二个延迟：30-60秒
        delay2 = random.uniform(30, 60)
        await asyncio.sleep(delay2)
        
        # 执行第三个任务
        task_name, task_func = tasks[2]
        await task_func()
        results.append({
            "task_name": task_name,
            "success": True,
            "message": f"任务 '{task_name}' 执行成功",
            "previous_delay": round(delay2, 2)
        })
        
        return {
            "success": True,
            "message": "所有定时任务执行完成",
            "results": results,
            "total_tasks": len(tasks),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        # 记录失败的任务
        failed_task = tasks[len(results)] if len(results) < len(tasks) else None
        if failed_task:
            results.append({
                "task_name": failed_task[0],
                "success": False,
                "message": f"任务 '{failed_task[0]}' 执行失败: {str(e)}"
            })
        
        return {
            "success": False,
            "message": f"定时任务执行过程中出错: {str(e)}",
            "results": results,
            "total_tasks": len(tasks),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/api/tasks/status")
async def get_tasks_status(current_admin = Depends(get_current_admin)):
    """
    获取定时任务状态信息
    """
    # 这里可以添加更复杂的任务状态跟踪逻辑
    # 目前返回基本状态信息
    return {
        "tasks": [
            {
                "name": "fetch_eastmoney_history_market_data",
                "display_name": "获取东方财富历史数据",
                "description": "从东方财富获取历史市场数据"
            },
            {
                "name": "crawl_llm_insight",
                "display_name": "LLM洞察分析",
                "description": "获取最新新闻和指数数据生成模板"
            },
            {
                "name": "news_ai_summary",
                "display_name": "新闻AI摘要",
                "description": "通过Dify API获取新闻摘要"
            }
        ],
        "total_count": 3,
        "timestamp": datetime.now().isoformat()
    }


# ———————————————— 数据统计API ————————————————

@router.get("/api/statistics")
async def get_statistics(current_admin = Depends(get_current_admin)):
    """
    获取数据统计信息
    """
    # 获取当前时间
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # 统计用户数据
    total_users = await User.all().count()
    new_users_this_month = await User.filter(created_at__gte=month_start).count()
    active_users_this_month = await User.filter(
        created_at__lt=now,
        is_active=True
    ).count()
    
    # 统计文章数据
    total_articles = await models.Article2.all().count()
    new_articles_this_month = await models.Article2.filter(created_at__gte=month_start).count()
    active_articles_this_month = await models.Article2.filter(
        created_at__lt=now,
        status="published"
    ).count()
    
    # 统计策略数据
    total_strategies = await models.Strategy.all().count()
    new_strategies_this_month = await models.Strategy.filter(created_at__gte=month_start).count()
    active_strategies_this_month = await models.Strategy.filter(
        created_at__lt=now,
        publish=True
    ).count()
    
    # 统计评论数据
    total_comments = await Comment.all().count()
    new_comments_this_month = await Comment.filter(created_at__gte=month_start).count()
    active_comments_this_month = await Comment.filter(
        created_at__lt=now
    ).count()
    
    # 获取用户增长趋势数据（最近7天）
    user_trend = {
        "labels": [],
        "new_users": [],
        "active_users": []
    }
    
    for i in range(6, -1, -1):  # 最近7天
        date_str = (now - timedelta(days=i)).strftime("%m-%d")
        start_date = now - timedelta(days=i)
        end_date = start_date + timedelta(days=1)
        
        # 当天新增用户数
        new_count = await User.filter(
            created_at__gte=start_date,
            created_at__lt=end_date
        ).count()
        
        # 当天活跃用户数（这里简化为当天有活动的用户，实际应用中可能需要更复杂的逻辑）
        active_count = await User.filter(
            created_at__lt=end_date,
            is_active=True
        ).count()
        
        user_trend["labels"].append(date_str)
        user_trend["new_users"].append(new_count)
        user_trend["active_users"].append(active_count)
    
    return {
        "users": {
            "total": total_users,
            "new_this_month": new_users_this_month,
            "active_this_month": active_users_this_month
        },
        "articles": {
            "total": total_articles,
            "new_this_month": new_articles_this_month,
            "active_this_month": active_articles_this_month
        },
        "strategies": {
            "total": total_strategies,
            "new_this_month": new_strategies_this_month,
            "active_this_month": active_strategies_this_month
        },
        "comments": {
            "total": total_comments,
            "new_this_month": new_comments_this_month,
            "active_this_month": active_comments_this_month
        },
        "user_trend": user_trend,
        "timestamp": now.isoformat()
    }


@router.get("/api/statistics/user_trend")
async def get_user_trend(period: int = 30, current_admin = Depends(get_current_admin)):
    """
    获取用户增长趋势数据
    """
    now = datetime.now()
    user_trend = {
        "labels": [],
        "new_users": [],
        "active_users": []
    }
    
    # 根据period参数确定时间范围
    if period <= 7:
        # 按天统计
        for i in range(period-1, -1, -1):
            date_str = (now - timedelta(days=i)).strftime("%m-%d")
            start_date = now - timedelta(days=i)
            end_date = start_date + timedelta(days=1)
            
            new_count = await User.filter(
                created_at__gte=start_date,
                created_at__lt=end_date
            ).count()
            
            active_count = await User.filter(
                created_at__lt=end_date,
                is_active=True
            ).count()
            
            user_trend["labels"].append(date_str)
            user_trend["new_users"].append(new_count)
            user_trend["active_users"].append(active_count)
    else:
        # 按周统计
        weeks = period // 7
        for i in range(weeks-1, -1, -1):
            week_start = now - timedelta(weeks=i+1)
            week_end = now - timedelta(weeks=i)
            week_str = f"{week_start.strftime('%m-%d')}~{week_end.strftime('%m-%d')}"
            
            new_count = await User.filter(
                created_at__gte=week_start,
                created_at__lt=week_end
            ).count()
            
            active_count = await User.filter(
                created_at__lt=week_end,
                is_active=True
            ).count()
            
            user_trend["labels"].append(week_str)
            user_trend["new_users"].append(new_count)
            user_trend["active_users"].append(active_count)
    
    return user_trend


