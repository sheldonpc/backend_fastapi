from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
import asyncio
from app import models, schemas
from app.deps import get_current_user, rate_limiter
from app.utils.code import generate_verification_code
from app.utils.email import send_email
from app.utils.redis_client import set_code, get_code, delete_code
from app.utils.security import verify_password, hash_password
from app.utils.user_utils import save_avatar

router = APIRouter(prefix="/users", tags=["users"])

# 用户信息查询接口（登录用户）
@router.get("/me")
async def read_current_user(current_user = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "is_admin": current_user.role == "admin",
    }

# 用户信息更新接口
@router.put("/me")
async def update_me(
        username: str = Form(None),
        avatar: UploadFile = File(None),
        current_user = Depends(get_current_user)
):
    if username:
        current_user.username = username

    if avatar:
        avatar_url = await save_avatar(avatar)
        current_user.avatar_url = avatar_url

    await current_user.save()
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "avatar_url": current_user.avatar_url
    }

@router.get("/me/avtar")
async def upload_avtar(file: UploadFile = File(...), current_user = Depends(get_current_user)):
    file_path = f"static/avtars/{current_user.id}_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"msg": "Avatar uploaded", "path": file_path}

# 修改密码
@router.post("/change_password")
@rate_limiter("change_password", limit=3, ttl=60)
async def change_password_request(
        data: schemas.PasswordChangeRequest,
        current_user = Depends(get_current_user)
):
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect old password"
        )

    code = generate_verification_code()
    await set_code((str(current_user.email)), code)

    asyncio.create_task(send_email(to_email=current_user.email, subject="重置密码", code=code, template_filename="email_changepwd.html"))
    return {"msg": "重置密码-验证码已发送，请检查邮箱"}

@router.post("/confirm_password")
async def change_password_confirm(
        data: schemas.PasswordChangeConfirm,
        current_user = Depends(get_current_user)
):
    stored_code = await get_code(current_user.email)
    if not stored_code or stored_code != data.code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="验证码错误或过期"
        )
    current_user.hashed_password = hash_password(data.new_password)
    await current_user.save()

    await delete_code(current_user.email)

    return {"msg": "密码修改成功"}

@router.post("/forget_password")
@rate_limiter("forget_password", limit=3, ttl=60)
async def forget_password(
        email: str = Form(...)
):
    user = await models.User.filter(email=email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邮箱不存在，请核对并重新输入"
        )

    code = generate_verification_code()
    await set_code((str(email)), code)

    asyncio.create_task(send_email(to_email=email, subject="重置密码", code=code, template_filename="email_changepwd.html"))
    return {"msg": "重置密码-验证码已发送，请检查邮箱"}

@router.post("/forget_password/confirm")
async def forget_password_confirm(
        data: schemas.PasswordResetRequest,
):
    stored_code = await get_code(data.email)
    if not stored_code or stored_code != data.code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="验证码错误或过期"
        )
    user = await models.User.filter(email=data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邮箱不存在，请核对并重新输入"
        )
    user.hashed_password = hash_password(data.new_password)
    await user.save()
    await delete_code(data.email)
    return {"msg": "密码重置成功"}
