import asyncio

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q
from app import models, schemas
from app.deps import rate_limiter
from app.utils.code import generate_verification_code
from app.utils.email import send_email
from app.utils.redis_client import set_code, get_code, delete_code
from app.utils.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

# verification_cache = {}

@router.post("/register", response_model=schemas.Token)
@rate_limiter("register", limit=3, ttl=60)
async def register(user: schemas.UserCreate, code: str):
    stored_code = await get_code(email=str(user.email))
    # 验证邮箱
    if not stored_code or stored_code != code:
        raise HTTPException(status_code=400, detail="验证码错误或过期")
    exists = await models.User.filter(email=user.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already exists")

    print(user.email, user.password, user.username)

    user_obj = await models.User.create(
        email=user.email,
        username=user.username,
        hashed_password=hash_password(user.password)
    )

    await delete_code(email=str(user_obj.email))

    token = create_access_token({"sub": str(user_obj.id)})
    return {"access_token": token, "token_type": "bearer"}

# @router.post("/login", response_model=schemas.Token)
# async def login(user: schemas.UserLogin):
#     try:
#         user_obj = await models.User.get(email=str(user.email))
#     except DoesNotExist:
#         raise HTTPException(status_code=400, detail="Invalid credentials")
#
#     if not verify_password(user.password, user_obj.hashed_password):
#         raise HTTPException(status_code=400, detail="Invalid credentials")
#
#     token = create_access_token({"sub": str(user_obj.id)})
#     return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
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
    return {"access_token": token, "token_type": "bearer"}


@router.post("/reset-password")
async def reset_password(email: str, new_password: str, code: str):
    stored_code  = await get_code(email)
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
async def send_code(email: str):
    code = generate_verification_code()
    await set_code(str(email), code)
    asyncio.create_task(send_email(to_email=email, subject="注册验证码", code=code))
    return {"msg": "验证码已发送，请检查邮箱"}
