from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from app.deps import get_current_admin

# 模拟数据存储（内存中，非持久化）
configs_data = [
    {
        "id": str(uuid.uuid4()),
        "key": "site_title",
        "value": "我的博客",
        "description": "站点标题",
        "group": "site",
        "updated_at": "2025-09-22T10:00:00Z"
    },
    {
        "id": str(uuid.uuid4()),
        "key": "seo_keywords",
        "value": "博客,技术分享",
        "description": "SEO关键词",
        "group": "seo",
        "updated_at": "2025-09-22T09:00:00Z"
    }
]


# Pydantic 模型定义
class ConfigCreate(BaseModel):
    key: str
    value: str
    description: Optional[str] = ""
    group: str


class ConfigUpdate(BaseModel):
    key: Optional[str] = None
    value: Optional[str] = None
    description: Optional[str] = None
    group: Optional[str] = None


class ConfigResponse(BaseModel):
    id: str
    key: str
    value: str
    description: str
    group: str
    updated_at: str

    class Config:
        from_attributes = True


class ConfigListResponse(BaseModel):
    items: List[ConfigResponse]
    total: int


# 路由器定义
router = APIRouter(prefix="/admin/api/config", tags=["api_config"])

# Token 验证依赖（复用之前的verify_token）
security = HTTPBearer()


# async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     token = credentials.credentials
#     if not token:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="未授权",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     # 模拟验证
#     if token != "your_sample_token":
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="无效 Token",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     return token


@router.get("/", response_model=ConfigListResponse)
async def get_configs(current_admin = Depends(get_current_admin)):
    """获取配置列表"""
    return {"items": configs_data, "total": len(configs_data)}


@router.post("/", response_model=ConfigResponse, status_code=201)
async def create_config(config: ConfigCreate, current_admin = Depends(get_current_admin)):
    """创建配置"""
    if not config.key or not config.value:
        raise HTTPException(status_code=400, detail="缺少必填字段")

    # 检查键是否重复
    if any(c["key"] == config.key for c in configs_data):
        raise HTTPException(status_code=400, detail="配置键已存在")

    new_config = {
        "id": str(uuid.uuid4()),
        "key": config.key,
        "value": config.value,
        "description": config.description,
        "group": config.group,
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }
    configs_data.append(new_config)
    return new_config


@router.put("/{config_id}", response_model=ConfigResponse)
async def update_config(
        config_id: str,
        config: ConfigUpdate,
        current_admin = Depends(get_current_admin)
):
    """更新配置"""
    for item in configs_data:
        if item["id"] == config_id:
            if config.value is not None:
                item["value"] = config.value
            if config.description is not None:
                item["description"] = config.description
            if config.group is not None:
                item["group"] = config.group
            item["updated_at"] = datetime.utcnow().isoformat() + "Z"
            return item

    raise HTTPException(status_code=404, detail="配置不存在")

# 注意：未添加DELETE，因为配置通常不直接删除，可通过编辑value为空实现