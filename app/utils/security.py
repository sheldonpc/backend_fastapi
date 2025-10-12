from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from app import config
from app.models import User

# 使用Argon2作为主要哈希算法，bcrypt作为备选
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    使用Argon2哈希密码，没有长度限制
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    使用Argon2验证密码，没有长度限制
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, TypeError) as e:
        print(f"密码验证错误: {e}")
        return False

def create_access_token(data: dict, expires_delta: int = config.JWT_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

async def authenticate_user(email: str, password: str):
    user = await User.get_or_none(email=email)
    if not user:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user