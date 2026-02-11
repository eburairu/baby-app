"""家族管理ルーター"""
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user, get_current_family, admin_required
from app.services.family_service import FamilyService

router = APIRouter(prefix="/families", tags=["family"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/setup", response_class=HTMLResponse)
async def family_setup_page(
    request: Request,
    user: User = Depends(get_current_user)
):
    """家族の作成または参加を選択するページ"""
    if user.families:
        return RedirectResponse(url="/dashboard", status_code=303)
    
    return templates.TemplateResponse(
        "family/setup.html",
        {"request": request, "user": user}
    )


@router.post("/create")
async def create_family(
    name: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """家族を新規作成"""
    FamilyService.create_family(db, user, name)
    return RedirectResponse(url="/dashboard", status_code=303)


@router.post("/join")
async def join_family(
    request: Request,
    invite_code: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """招待コードで家族に参加"""
    family = FamilyService.join_family(db, user, invite_code.upper())
    if not family:
        # エラー表示（簡易的にクエリパラメータで）
        return RedirectResponse(url="/families/setup?error=invalid_code", status_code=303)
    
    return RedirectResponse(url="/dashboard", status_code=303)


@router.get("/settings", response_class=HTMLResponse)
async def family_settings(
    request: Request,
    user: User = Depends(get_current_user),
    family = Depends(get_current_family),
    db: Session = Depends(get_db)
):
    """家族設定画面（招待コードの確認など）"""
    is_admin = FamilyService.is_admin(db, user.id, family.id)
    return templates.TemplateResponse(
        "family/settings.html",
        {
            "request": request,
            "family": family,
            "is_admin": is_admin,
            "members": family.members
        }
    )
