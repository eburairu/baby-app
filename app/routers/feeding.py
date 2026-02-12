"""授乳記録ルーター"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.templates import templates
from app.dependencies import get_current_user, get_current_baby
from app.models.user import User
from app.models.baby import Baby
from app.models.feeding import Feeding, FeedingType
from app.schemas.feeding import FeedingResponse, FeedingCreate, FeedingUpdate

router = APIRouter(prefix="/feedings", tags=["feedings"])


@router.get("", response_class=HTMLResponse)
async def list_feedings(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
):
    """授乳記録一覧ページ"""
    feedings = db.query(Feeding).filter(
        Feeding.baby_id == baby.id
    ).order_by(Feeding.feeding_time.desc()).limit(50).all()

    return templates.TemplateResponse(
        "feeding/list.html",
        {"request": request, "user": user, "baby": baby, "feedings": feedings}
    )


@router.get("/new", response_class=HTMLResponse)
async def new_feeding_form(
    request: Request,
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby)
):
    """新規授乳記録フォーム"""
    return templates.TemplateResponse(
        "feeding/form.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "feeding": None,
            "feeding_types": FeedingType
        }
    )


@router.post("", response_class=HTMLResponse)
async def create_feeding(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    form_data: FeedingCreate = Depends(FeedingCreate.as_form)
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
    user: User = Depends(get_current_user)
):
    """授乳記録編集フォーム"""
    feeding = db.query(Feeding).filter(
        Feeding.id == feeding_id,
        Feeding.user_id == user.id
    ).first()

    if not feeding:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    return templates.TemplateResponse(
        "feeding/form.html",
        {
            "request": request,
            "user": user,
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
    form_data: FeedingUpdate = Depends(FeedingUpdate.as_form)
):
    """授乳記録更新"""
    feeding = db.query(Feeding).filter(
        Feeding.id == feeding_id,
        Feeding.user_id == user.id
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
    user: User = Depends(get_current_user)
):
    """授乳記録削除"""
    feeding = db.query(Feeding).filter(
        Feeding.id == feeding_id,
        Feeding.user_id == user.id
    ).first()

    if not feeding:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    db.delete(feeding)
    db.commit()

    return ""
