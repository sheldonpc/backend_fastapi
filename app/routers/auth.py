import asyncio
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends, status, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q
from app import models, schemas
from app.deps import rate_limiter
from app.utils.code import generate_verification_code
from app.utils.email import send_email
from app.utils.redis_client import set_code, get_code, delete_code
from app.utils.security import hash_password, verify_password, create_access_token
from app.core.templates import templates

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})


@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("admin/register.html", {"request": request})


@router.post("/register", response_model=schemas.Token)
@rate_limiter("register", limit=3, ttl=60)
async def register(user: schemas.UserCreate, response: Response):
    stored_code = await get_code(email=str(user.email))
    code = user.code
    if not stored_code or stored_code != code:
        raise HTTPException(status_code=400, detail="验证码错误或过期")
    exists = await models.User.filter(email=user.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already exists")

    user_obj = await models.User.create(
        email=user.email,
        username=user.username,
        hashed_password=hash_password(user.password)
    )

    await delete_code(email=str(user_obj.email))

    token = create_access_token({"sub": str(user_obj.id)})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=timedelta(days=7).total_seconds()
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), response: Response = None):
    identifier = form_data.username
    password = form_data.password
    db_user = await models.User.filter(
        Q(email=identifier) | Q(username=identifier)
    ).first()

    if not db_user or not verify_password(password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误，请重试"
        )
    token = create_access_token({"sub": str(db_user.id)})

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=timedelta(days=7).total_seconds()
    )

    return {"access_token": token, "token_type": "bearer"}


@router.post("/reset-password")
async def reset_password(email: str, new_password: str, code: str):
    stored_code = await get_code(email)
    if not stored_code or stored_code != code:
        raise HTTPException(status_code=400, detail="验证码错误或过期")

    try:
        user_obj = await models.User.get(email=email)
    except DoesNotExist:
        raise HTTPException(status_code=400, detail="Email not found")

    user_obj.password = hash_password(new_password)
    await user_obj.save()
    await delete_code(str(email))
    return {"msg": "密码已重置成功"}


@router.post("/send-code")
async def send_code(request: schemas.SendCodeRequest):
    email = request.email

    # 检查邮箱是否已被占用
    user = await models.User.filter(email=email).first()
    if user:
        # 不再抛出异常，而是直接返回一个表示失败的JSON对象
        return {"success": False, "msg": "邮箱已被占用，请更换"}

    # 如果邮箱未被占用，则继续执行发送验证码的逻辑
    code = generate_verification_code()
    await set_code(str(email), code)
    asyncio.create_task(send_email(to_email=email, subject="注册验证码", code=code))

    # 返回一个表示成功的JSON对象
    return {"success": True, "msg": "验证码已发送，请检查邮箱"}


@router.get("/logout")
async def logout(response: Response):
    # 创建重定向响应
    redirect = RedirectResponse(url="/")

    # 在重定向响应中删除后端 httpOnly cookie
    redirect.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,
        samesite="lax",
        path="/"
    )

    # 同时删除前端可能存储的 token（非 httponly）
    redirect.delete_cookie(
        key="token",  # 您前端设置的 cookie
        path="/"
    )

    return redirect
