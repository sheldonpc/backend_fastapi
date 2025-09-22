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

from app.deps import get_current_admin

router = APIRouter(prefix="/admin/api/users", tags=["users"])

# ==================== 模拟数据库 ====================
# 🔥 重启服务数据会丢失，生产环境请替换为真实数据库
_users_db = []
_user_id_counter = 1

def init_mock_users():
    global _users_db, _user_id_counter
    if _users_db:
        return
    roles = ["user", "vip", "editor"]
    statuses = ["active", "disabled"]
    for i in range(1, 51):  # 50个模拟用户
        _users_db.append({
            "id": i,
            "username": f"user{i:02d}",
            "email": f"user{i:02d}@example.com",
            "role": random.choice(roles),
            "status": random.choice(statuses),
            "created_at": (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat(),
            "last_login": (datetime.now() - timedelta(hours=random.randint(1, 720))).isoformat() if random.random() > 0.3 else None
        })
    _user_id_counter = 51

init_mock_users()

# ==================== 数据模型 ====================
class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    role: str = Field(..., pattern="^(user|vip|editor)$")
    status: str = Field(..., pattern="^(active|disabled)$")
    password: Optional[str] = Field(None, min_length=6)

class UserUpdate(UserCreate):
    pass

class UserStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(active|disabled)$")

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    status: str
    created_at: str
    last_login: Optional[str] = None

class UserListResponse(BaseModel):
    items: List[UserOut]
    total: int
    page: int
    page_size: int
    total_pages: int

# ==================== 工具函数 ====================
def find_user_by_id(user_id: int):
    return next((u for u in _users_db if u["id"] == user_id), None)

def generate_password(length=8):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

# ==================== API 接口 ====================

# 🔍 获取用户列表（带分页、搜索、筛选）
@router.get("/", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = Query(None, pattern="^(active|disabled)$"),
    role: Optional[str] = Query(None, pattern="^(user|vip|editor)$"),
    current_admin = Depends(get_current_admin)  # 假设你有这个依赖
):
    # 过滤
    filtered = _users_db

    if search:
        search_lower = search.lower()
        filtered = [u for u in filtered if
                   search_lower in u["username"].lower() or
                   search_lower in u["email"].lower()]

    if status:
        filtered = [u for u in filtered if u["status"] == status]

    if role:
        filtered = [u for u in filtered if u["role"] == role]

    total = len(filtered)
    total_pages = (total + page_size - 1) // page_size
    start = (page - 1) * page_size
    end = start + page_size
    items = filtered[start:end]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }

# ➕ 创建用户
@router.post("/", response_model=UserOut, status_code=201)
async def create_user(user: UserCreate, current_admin = Depends(get_current_admin)):
    global _user_id_counter

    # 检查用户名或邮箱是否已存在
    if any(u["username"] == user.username for u in _users_db):
        raise HTTPException(status_code=400, detail="用户名已存在")
    if any(u["email"] == user.email for u in _users_db):
        raise HTTPException(status_code=400, detail="邮箱已存在")

    new_user = {
        "id": _user_id_counter,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "status": user.status,
        "created_at": datetime.now().isoformat(),
        "last_login": None
    }
    _users_db.append(new_user)
    _user_id_counter += 1

    # 如果提供了密码，这里可以 hash 并存储（模拟）
    if user.password:
        print(f"🔐 为用户 {user.username} 设置密码: {user.password}")

    return new_user

# ✏️ 更新用户
@router.put("/{user_id}", response_model=UserOut)
async def update_user(user_id: int, user: UserUpdate, current_admin = Depends(get_current_admin)):
    existing = find_user_by_id(user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 检查用户名/邮箱冲突（排除自己）
    if any(u["username"] == user.username and u["id"] != user_id for u in _users_db):
        raise HTTPException(status_code=400, detail="用户名已存在")
    if any(u["email"] == user.email and u["id"] != user_id for u in _users_db):
        raise HTTPException(status_code=400, detail="邮箱已存在")

    existing.update({
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "status": user.status
    })

    # 如果提供了密码，模拟更新
    if user.password:
        print(f"🔐 更新用户 {user.username} 的密码")

    return existing

# 🎚️ 更新用户状态（快速切换）
@router.patch("/{user_id}/status", response_model=UserOut)
async def update_user_status(user_id: int, update: UserStatusUpdate, current_admin = Depends(get_current_admin)):
    user = find_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user["status"] = update.status
    return user

# ❌ 删除用户
@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, current_admin = Depends(get_current_admin)):
    global _users_db
    user = find_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    _users_db = [u for u in _users_db if u["id"] != user_id]
    return None

# 📥 导出用户为 Excel
@router.get("/export")
async def export_users(
    search: Optional[str] = None,
    status: Optional[str] = Query(None, pattern="^(active|disabled)$"),
    role: Optional[str] = Query(None, pattern="^(user|vip|editor)$"),
    current_admin = Depends(get_current_admin)
):
    # 复用过滤逻辑
    filtered = _users_db
    if search:
        search_lower = search.lower()
        filtered = [u for u in filtered if
                   search_lower in u["username"].lower() or
                   search_lower in u["email"].lower()]
    if status:
        filtered = [u for u in filtered if u["status"] == status]
    if role:
        filtered = [u for u in filtered if u["role"] == role]

    # 创建 Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "用户列表"

    # 表头
    headers = ["ID", "用户名", "邮箱", "角色", "状态", "注册时间", "最后登录"]
    ws.append(headers)

    # 数据
    for user in filtered:
        ws.append([
            user["id"],
            user["username"],
            user["email"],
            user["role"],
            user["status"],
            user["created_at"],
            user["last_login"] or "从未登录"
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