import os
from dotenv import load_dotenv

load_dotenv()

# MySQL数据库
DB_URL = os.getenv("DB_URL", "mysql://root:root@localhost:3306/mydb")

# JWT配置
JWT_SECRET = os.getenv("JWT_SECRET", "mysecret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60*24))

# 邮件配置
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER", "noreply@example.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "password")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
VERIFICATION_CODE_TTL = int(os.getenv("VERIFICATION_CODE_TTL", 60*5))

TORTOISE_ORM = {
    "connections" : {"default": DB_URL},
    "apps" : {
        "models" : {
            "models" : ["app.models", "aerich.models"],
            "default_connection" : "default"
        }
    }
}