from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.templates import templates
from app.deps import get_current_user_from_cookie

router = APIRouter(tags=["error"])

@router.get("/error", response_class=HTMLResponse)
async def error_page(
    request: Request,
    status: int = Query(...),
    message: str = Query(...),
    current_user=Depends(get_current_user_from_cookie)
):
    """
    显示错误页面
    """
    if current_user:
        return templates.TemplateResponse(
            "public/error.html",
            {
                "request": request,
                "status_code": status,
                "message": message,
                "current_user": current_user
            }
        )
    else:
        return templates.TemplateResponse(
            "public/error.html",
            {
                "request": request,
                "status_code": status,
                "message": message
            }
        )