# admin/roles.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.deps import get_current_admin

router = APIRouter(prefix="/admin/api/roles", tags=["roles"])

# ==================== 模拟数据库 ====================
_roles_db = [
    {
        "id": 1,
        "name": "管理员",
        "description": "拥有所有权限",
        "permissions": ["user_view", "user_edit", "user_delete", "user_create", "article_view", "article_edit", "article_delete", "article_create", "article_publish", "system_config", "role_manage", "log_view"],
        "created_at": "2025-01-01T00:00:00",
        "user_count": 3  # 模拟数据
    },
    {
        "id": 2,
        "name": "编辑",
        "description": "内容编辑人员",
        "permissions": ["article_view", "article_edit", "article_create", "article_publish"],
        "created_at": "2025-01-02T00:00:00",
        "user_count": 15
    },
    {
        "id": 3,
        "name": "普通用户",
        "description": "只能查看内容",
        "permissions": ["article_view"],
        "created_at": "2025-01-03T00:00:00",
        "user_count": 200
    }
]

_role_id_counter = 4

# ==================== 数据模型 ====================
class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    permissions: List[str]

class RoleOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    permissions: List[str]
    created_at: str
    user_count: int

class RoleListResponse(BaseModel):
    items: List[RoleOut]

# ==================== API 接口 ====================

# 🔍 获取角色列表
@router.get("/", response_model=RoleListResponse)
async def get_roles(current_admin = Depends(get_current_admin)):
    return {"items": _roles_db}

# ➕ 创建角色
@router.post("/", response_model=RoleOut, status_code=201)
async def create_role(role: RoleCreate, current_admin = Depends(get_current_admin)):
    global _role_id_counter

    # 检查角色名是否已存在
    if any(r["name"] == role.name for r in _roles_db):
        raise HTTPException(status_code=400, detail="角色名称已存在")

    new_role = {
        "id": _role_id_counter,
        "name": role.name,
        "description": role.description,
        "permissions": role.permissions,
        "created_at": datetime.now().isoformat(),
        "user_count": 0  # 新角色暂无用户
    }
    _roles_db.append(new_role)
    _role_id_counter += 1

    return new_role

# ✏️ 更新角色
@router.put("/{role_id}", response_model=RoleOut)
async def update_role(role_id: int, role: RoleCreate, current_admin = Depends(get_current_admin)):
    existing = next((r for r in _roles_db if r["id"] == role_id), None)
    if not existing:
        raise HTTPException(status_code=404, detail="角色不存在")

    # 检查角色名冲突（排除自己）
    if any(r["name"] == role.name and r["id"] != role_id for r in _roles_db):
        raise HTTPException(status_code=400, detail="角色名称已存在")

    existing.update({
        "name": role.name,
        "description": role.description,
        "permissions": role.permissions
    })

    return existing

# ❌ 删除角色
@router.delete("/{role_id}", status_code=204)
async def delete_role(role_id: int, current_admin = Depends(get_current_admin)):
    global _roles_db

    role = next((r for r in _roles_db if r["id"] == role_id), None)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    if role["name"] == "管理员":
        raise HTTPException(status_code=400, detail="管理员角色不可删除")

    if role["user_count"] > 0:
        raise HTTPException(status_code=400, detail=f"该角色已被 {role['user_count']} 名用户使用，无法删除")

    _roles_db = [r for r in _roles_db if r["id"] != role_id]
    return None