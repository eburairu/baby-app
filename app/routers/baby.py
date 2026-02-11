"""赤ちゃん管理ルーター"""
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.models.baby import Baby
from app.dependencies import get_current_user, get_current_family, admin_required

router = APIRouter(prefix="/babies", tags=["baby"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/new", response_class=HTMLResponse)
async def new_baby_page(
    request: Request,
    user = Depends(get_current_user),
    family = Depends(get_current_family)
):
    """赤ちゃん登録ページ"""
    return templates.TemplateResponse(
        "baby/form.html",
        {"request": request, "family": family}
    )


@router.post("/create")
async def create_baby(
    name: str = Form(...),
    birthday: date = Form(None),
    due_date: date = Form(None),
    db: Session = Depends(get_db),
    family = Depends(get_current_family),
    _ = Depends(admin_required)  # 管理者のみ可能
):
    """赤ちゃんを登録"""
    baby = Baby(
        family_id=family.id,
        name=name,
        birthday=birthday,
        due_date=due_date
    )
    db.add(baby)
    db.commit()
    return RedirectResponse(url="/dashboard", status_code=303)
