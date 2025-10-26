# admin/users.py
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime, timedelta
import random
import string
from openpyxl import Workbook
from io import BytesIO
from fastapi.responses import StreamingResponse
from tortoise.expressions import Q

from app.deps import get_current_admin
from app.models import User

router = APIRouter(prefix="/admin/api/user-management", tags=["users"])

# ==================== 数据模型 ====================
class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    role: str = Field(..., pattern="^(user|vip|editor|admin)$")
    password: Optional[str] = Field(None, min_length=6)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, pattern="^(user|vip|editor|admin)$")
    password: Optional[str] = Field(None, min_length=6)

class UserStatusUpdate(BaseModel):
    is_active: bool

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: str
    last_login: Optional[str] = None

class UserListResponse(BaseModel):
    items: List[UserOut]
    total: int
    page: int
    page_size: int
    total_pages: int

# ==================== 工具函数 ====================
def generate_password(length=8):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

# ==================== API 接口 ====================

# 🔍 获取用户列表（带分页、搜索、筛选）
@router.get("", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = Query(None, pattern="^(active|disabled)$"),
    role: Optional[str] = Query(None, pattern="^(user|vip|editor|admin)$"),
    current_admin = Depends(get_current_admin)
):
    # 构建查询条件
    query = User.all()
    
    # 搜索条件
    if search:
        query = query.filter(
            Q(username__icontains=search) | Q(email__icontains=search)
        )
    
    # 状态筛选
    if status:
        is_active = status == "active"
        query = query.filter(is_active=is_active)
    
    # 角色筛选
    if role:
        query = query.filter(role=role)
    
    # 计算总数
    total = await query.count()
    
    # 应用分页
    offset = (page - 1) * page_size
    users = await query.offset(offset).limit(page_size)
    
    # 转换为输出格式
    items = []
    for user in users:
        items.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": None  # 真实数据库中可能需要添加last_login字段
        })
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }

# 🔍 获取用户详情
@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, current_admin = Depends(get_current_admin)):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": None
    }

# ➕ 创建用户
@router.post("", response_model=UserOut, status_code=201)
async def create_user(user: UserCreate, current_admin = Depends(get_current_admin)):
    # 检查用户名和邮箱是否已存在
    existing_user = await User.get_or_none(username=user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    existing_email = await User.get_or_none(email=user.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已存在")
    
    # 生成密码（如果未提供）
    password = user.password or generate_password()
    
    # 创建用户
    new_user = await User.create(
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=True,
        password=password
    )
    
    # 返回用户信息
    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role,
        "is_active": new_user.is_active,
        "created_at": new_user.created_at.isoformat() if new_user.created_at else None,
        "last_login": None
    }

# ✏️ 更新用户
@router.put("/{user_id}", response_model=UserOut)
async def update_user(user_id: int, user_data: UserUpdate, current_admin = Depends(get_current_admin)):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查用户名和邮箱是否与其他用户冲突
    if user_data.username and user_data.username != user.username:
        existing_user = await User.get_or_none(username=user_data.username)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=400, detail="用户名已存在")
    
    if user_data.email and user_data.email != user.email:
        existing_email = await User.get_or_none(email=user_data.email)
        if existing_email and existing_email.id != user_id:
            raise HTTPException(status_code=400, detail="邮箱已存在")
    
    # 更新用户信息
    if user_data.username:
        user.username = user_data.username
    if user_data.email:
        user.email = user_data.email
    if user_data.role:
        user.role = user_data.role
    
    # 如果提供了新密码，更新密码
    if user_data.password:
        user.password = user_data.password
    
    await user.save()
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": None
    }

# 🎚️ 更新用户状态（快速切换）
@router.patch("/{user_id}/status", response_model=UserOut)
async def update_user_status(user_id: int, update: UserStatusUpdate, current_admin = Depends(get_current_admin)):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.is_active = update.is_active
    await user.save()
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": None
    }

# ❌ 删除用户
@router.delete("/{user_id}")
async def delete_user(user_id: int, current_admin = Depends(get_current_admin)):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    await user.delete()
    
    return {"message": "用户删除成功"}

# 📥 导出用户为 Excel
@router.get("/export")
async def export_users(
    search: Optional[str] = None,
    status: Optional[str] = Query(None, pattern="^(active|disabled)$"),
    role: Optional[str] = Query(None, pattern="^(user|vip|editor|admin)$"),
    current_admin = Depends(get_current_admin)
):
    # 构建查询条件
    query = User.all()
    
    # 搜索条件
    if search:
        query = query.filter(
            Q(username__icontains=search) | Q(email__icontains=search)
        )
    
    # 状态筛选
    if status:
        is_active = status == "active"
        query = query.filter(is_active=is_active)
    
    # 角色筛选
    if role:
        query = query.filter(role=role)
    
    # 获取所有符合条件的用户
    users = await query.all()

    # 创建 Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "用户列表"

    # 表头
    headers = ["ID", "用户名", "邮箱", "角色", "状态", "注册时间", "最后登录"]
    ws.append(headers)

    # 数据
    for user in users:
        ws.append([
            user.id,
            user.username,
            user.email,
            user.role,
            "活跃" if user.is_active else "禁用",
            user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "",
            "从未登录"  # 真实数据库中可能需要添加last_login字段
        ])

    # 保存到内存
    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)

    filename = f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )