import logging

from fastapi import APIRouter, Request

from app.core.templates import templates

router = APIRouter(prefix="/admin/strategy", tags=["strategy"])

from app.utils.logger import get_logger

logger = get_logger("strategy")

@router.get("/new")
async def strategy(request: Request):
    """
    策略页面
    """
    return templates.TemplateResponse("admin/strategy_edit.html", {"request": request})
