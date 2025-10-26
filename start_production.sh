#!/bin/bash

# 生产环境启动脚本 - 使用Gunicorn多进程

# 设置变量
PROJECT_DIR="/var/www/myblog"
VENV_DIR="$PROJECT_DIR/venv"
APP_MODULE="app.main:app"
HOST="0.0.0.0"
PORT="8000"
WORKERS="2"  # 根据CPU核心数调整，通常为CPU核心数*2+1
WORKER_CLASS="uvicorn.workers.UvicornWorker"
WORKER_CONNECTIONS="500"
MAX_REQUESTS="500"
MAX_REQUESTS_JITTER="50"
TIMEOUT="60"
KEEPALIVE="2"

# 激活虚拟环境
source $VENV_DIR/bin/activate

# 启动应用
exec gunicorn $APP_MODULE \
  --bind $HOST:$PORT \
  --workers $WORKERS \
  --worker-class $WORKER_CLASS \
  --worker-connections $WORKER_CONNECTIONS \
  --max-requests $MAX_REQUESTS \
  --max-requests-jitter $MAX_REQUESTS_JITTER \
  --timeout $TIMEOUT \
  --keep-alive $KEEPALIVE \
  --access-logfile - \
  --error-logfile - \
  --log-level info
