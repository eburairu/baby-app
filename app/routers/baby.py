"""赤ちゃん管理ルーター"""
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from app.database import get_db
from app.models.baby import Baby
from app.models.family import Family
from app.dependencies import get_current_user, get_current_family, admin_required
from app.services.permission_service import PermissionService
from pydantic import BaseModel

router = APIRouter(prefix="/babies", tags=["baby"])


# ===== レスポンススキーマ =====

class BabyResponse(BaseModel):
    """赤ちゃん情報レスポンス"""
    id: int
    name: str
    birthday: date | None = None
    due_date: date | None = None

    class Config:
        from_attributes = True


class BabiesListResponse(BaseModel):
    """赤ちゃん一覧レスポンス"""
    babies: List[BabyResponse]
    family_id: int
    family_name: str


# ===== JSON API エンドポイント =====

@router.get("", response_model=BabiesListResponse)
async def list_babies(
    request: Request,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
    family: Family = Depends(get_current_family)
):
    """
    赤ちゃん一覧を取得（JSON対応）

    フロントエンドの赤ちゃんセレクター用
    """
    # JSONリクエストのみ対応（HTMLは不要）
    if not wants_json(request):
        raise HTTPException(status_code=406, detail="JSON only endpoint")

    # 閲覧可能な赤ちゃんのみに絞り込む
    baby_ids = [b.id for b in family.babies]
    perms_map = PermissionService.get_user_permissions_batch(
        db, user.id, baby_ids, family.id, "basic_info"
    )
    visible_babies = [b for b in family.babies if perms_map.get(b.id, False)]

    return BabiesListResponse(
        babies=[BabyResponse.model_validate(b) for b in visible_babies],
        family_id=family.id,
        family_name=family.name
    )


# ===== HTML エンドポイント =====

@router.post("/{baby_id}/delete")
async def delete_baby(
    baby_id: int,
    db: Session = Depends(get_db),
    family = Depends(get_current_family),
    _ = Depends(admin_required)
):
    """赤ちゃんを削除"""
    baby = db.query(Baby).filter(Baby.id == baby_id, Baby.family_id == family.id).first()
    if not baby:
        raise HTTPException(status_code=404, detail="Baby not found")
    
    db.delete(baby)
    db.commit()
    
    return RedirectResponse(url="/families/settings", status_code=303)


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


@router.post("/{baby_id}/born")
async def baby_born(
    baby_id: int,
    birthday: date = Form(...),
    db: Session = Depends(get_db),
    family = Depends(get_current_family),
    _ = Depends(admin_required)
):
    """赤ちゃんが生まれたことを記録（誕生日設定）"""
    baby = db.query(Baby).filter(Baby.id == baby_id, Baby.family_id == family.id).first()
    if not baby:
        raise HTTPException(status_code=404, detail="Baby not found")
    
    baby.birthday = birthday
    db.commit()
    
    return RedirectResponse(url="/dashboard", status_code=303)
