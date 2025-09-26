# app/core/templates.py
from fastapi.templating import Jinja2Templates

# 统一模板目录（对应你最终采用的结构）
templates = Jinja2Templates(directory="app/templates")