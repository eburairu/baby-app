"""授乳記録ルーター"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.templates import templates
from app.dependencies import get_current_user, get_current_baby, get_current_family, check_record_permission
from app.models.user import User
from app.models.baby import Baby
from app.models.family import Family
from app.models.feeding import Feeding, FeedingType
from app.schemas.feeding import FeedingResponse, FeedingCreate, FeedingUpdate
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/feedings", tags=["feedings"])


@router.get("", response_class=HTMLResponse)
async def list_feedings(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    family: Family = Depends(get_current_family),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("feeding"))
):
    """授乳記録一覧ページ"""
    feedings = db.query(Feeding).filter(
        Feeding.baby_id == baby.id
    ).order_by(Feeding.feeding_time.desc()).limit(50).all()

    # 閲覧可能な赤ちゃんリストを取得（グローバルナビゲーション用）
    baby_ids = [b.id for b in family.babies]
    perms_map = PermissionService.get_user_permissions_batch(
        db, user.id, baby_ids, family.id, "basic_info"
    )
    viewable_babies = [b for b in family.babies if perms_map.get(b.id, False)]

    response = templates.TemplateResponse(
        "feeding/list.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "feedings": feedings,
            "viewable_babies": viewable_babies,
            "current_baby": baby
        }
    )

    # 選択された赤ちゃんIDをクッキーに保存
    response.set_cookie(
        key="selected_baby_id",
        value=str(baby.id),
        max_age=7 * 24 * 60 * 60,
        httponly=False,
        samesite="lax"
    )
    return response


@router.get("/new", response_class=HTMLResponse)
async def new_feeding_form(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    family: Family = Depends(get_current_family),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("feeding"))
):
    """新規授乳記録フォーム"""
    # 閲覧可能な赤ちゃんリストを取得（グローバルナビゲーション用）
    baby_ids = [b.id for b in family.babies]
    perms_map = PermissionService.get_user_permissions_batch(
        db, user.id, baby_ids, family.id, "basic_info"
    )
    viewable_babies = [b for b in family.babies if perms_map.get(b.id, False)]

    return templates.TemplateResponse(
        "feeding/form.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "feeding": None,
            "feeding_types": FeedingType,
            "viewable_babies": viewable_babies,
            "current_baby": baby
        }
    )


@router.post("", response_class=HTMLResponse)
async def create_feeding(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    form_data: FeedingCreate = Depends(FeedingCreate.as_form),
    _ = Depends(check_record_permission("feeding"))
):
    """授乳記録作成"""
    # 新しい記録を作成
    new_feeding = Feeding(
        user_id=user.id,
        baby_id=baby.id,
        **form_data.model_dump()
    )

    db.add(new_feeding)
    db.commit()
    db.refresh(new_feeding)

    # htmxリクエストの場合は部分HTMLを返す
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "feeding/item.html",
            {"request": request, "feeding": new_feeding}
        )

    return templates.TemplateResponse(
        "feeding/list.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "feedings": db.query(Feeding).filter(
                Feeding.baby_id == baby.id
            ).order_by(Feeding.feeding_time.desc()).limit(50).all()
        }
    )


@router.get("/{feeding_id}/edit", response_class=HTMLResponse)
async def edit_feeding_form(
    request: Request,
    feeding_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("feeding"))
):
    """授乳記録編集フォーム"""
    feeding = db.query(Feeding).filter(
        Feeding.id == feeding_id,
        Feeding.baby_id == baby.id
    ).first()

    if not feeding:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    return templates.TemplateResponse(
        "feeding/form.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "feeding": feeding,
            "feeding_types": FeedingType
        }
    )


@router.post("/{feeding_id}", response_class=HTMLResponse)
async def update_feeding(
    request: Request,
    feeding_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    form_data: FeedingUpdate = Depends(FeedingUpdate.as_form),
    _ = Depends(check_record_permission("feeding"))
):
    """授乳記録更新"""
    feeding = db.query(Feeding).filter(
        Feeding.id == feeding_id,
        Feeding.baby_id == baby.id
    ).first()

    if not feeding:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    # 更新データを適用
    update_data = form_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(feeding, key, value)

    db.commit()
    db.refresh(feeding)

    # htmxリクエストの場合は部分HTMLを返す
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "feeding/item.html",
            {"request": request, "feeding": feeding}
        )

    return templates.TemplateResponse(
        "feeding/list.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "feedings": db.query(Feeding).filter(
                Feeding.baby_id == baby.id
            ).order_by(Feeding.feeding_time.desc()).limit(50).all()
        }
    )


@router.delete("/{feeding_id}", response_class=HTMLResponse)
async def delete_feeding(
    feeding_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("feeding"))
):
    """授乳記録削除"""
    feeding = db.query(Feeding).filter(
        Feeding.id == feeding_id,
        Feeding.baby_id == baby.id
    ).first()

    if not feeding:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    db.delete(feeding)
    db.commit()

    return ""
