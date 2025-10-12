import logging
import os
from logging.handlers import RotatingFileHandler

# 创建日志目录
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 配置日志文件路径
APP_LOG_FILE = os.path.join(LOG_DIR, "app.log")
ERROR_LOG_FILE = os.path.join(LOG_DIR, "error.log")

# 创建主logger
logger = logging.getLogger("myblog")
logger.setLevel(logging.INFO)


def init_logger(console_output=True):
    """初始化日志系统

    Args:
        console_output (bool): 是否输出到控制台，默认True
    """
    # 清除现有的handler
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # 创建格式化器
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 应用日志文件处理器 (轮转日志)
    app_file_handler = RotatingFileHandler(
        APP_LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    app_file_handler.setLevel(logging.INFO)
    app_file_handler.setFormatter(formatter)
    logger.addHandler(app_file_handler)

    # 错误日志文件处理器
    error_file_handler = RotatingFileHandler(
        ERROR_LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding="utf-8"
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    logger.addHandler(error_file_handler)

    # 控制台输出
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # 配置 uvicorn 日志（简化）
    setup_uvicorn_logging()

    logger.info("Logger initialized successfully")


def setup_uvicorn_logging():
    """配置Uvicorn日志 - 简化版本"""
    # 禁用 uvicorn 的默认访问日志，避免格式错误
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.handlers.clear()
    uvicorn_access.propagate = True  # 让 uvicorn 日志传播到我们的主 logger

    uvicorn_error = logging.getLogger("uvicorn.error")
    uvicorn_error.handlers.clear()
    uvicorn_error.propagate = True


def get_logger(name=None):
    """获取logger实例"""
    if name:
        return logging.getLogger(f"myblog.{name}")
    return logger

# 默认初始化（开发环境）
# init_logger(console_output=True)  # 这行可以注释掉，因为在main.py中会初始化