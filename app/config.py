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

# 爬虫配置
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "chromedriver.exe")
CRAWLER_HEADLESS = os.getenv("CRAWLER_HEADLESS", "true").lower() == "true"
CRAWLER_INTERVAL_SECONDS = int(os.getenv("CRAWLER_INTERVAL_SECONDS", 300))

# TORTOISE_ORM = {
#     "connections" : {"default": DB_URL},
#     "apps" : {
#         "models" : {
#             "models" : ["app.models", "aerich.models"],
#             "default_connection" : "default"
#         }
#     }
# }

TORTOISE_ORM = {
    "connections" : {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", 3306)),
                "user": os.getenv("DB_USER", "root"),
                "password": os.getenv("DB_PASSWORD", "root"),
                "database": os.getenv("DB_NAME", "mydb"),
                "charset": "utf8mb4"
                # 移除不支持的timezone参数
            }
        }
    },
    "apps" : {
        "models" : {
            "models" : ["app.models", "aerich.models"],
            "default_connection" : "default"
        }
    },
    "use_tz": True,  # 启用时区支持
    "timezone": "Asia/Shanghai"  # 设置默认时区为北京时间
}

def _load_financial_targets():
    targets = []
    symbols = [
        "SHANGHAI", "SHENZHEN", "CHINEXT", "BEIJING", "HUSHEN300",
        "DOWJONES", "NASDAQ", "SP500", "GOLD_NY", "SILVER_NY"
    ]

    for symbol in symbols:
        url = os.getenv(f"{symbol}_URL")
        if url:
            name = symbol.replace("_", "")
            if symbol == "HUSHEN300":
                name = "HuShen300"
            elif symbol == "CHINEXT":
                name = "ChiNext"
            elif symbol == "SP500":
                name = "S&P500"
            elif symbol == "GOLD_NY":
                name = "Gold_NY"
            elif symbol == "SILVER_NY":
                name = "Silver_NY"
            else:
                name = symbol.capitalize()

            target = {
                "name": name,
                "url": url,
                "type": os.getenv(f"{symbol}_TYPE", "unknown"),
                "display_name": os.getenv(f"{symbol}_NAME", name),
                "data_type": os.getenv(f"{symbol}_DATA_TYPE", "index"),
                "market_region": os.getenv(f"{symbol}_REGION", "Unknown")
            }
            targets.append(target)
    return targets

FINANCIAL_TARGETS = _load_financial_targets()