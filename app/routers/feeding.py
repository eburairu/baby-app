"""授乳記録ルーター"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.feeding import Feeding, FeedingType
from app.schemas.feeding import FeedingResponse

router = APIRouter(prefix="/feedings", tags=["feedings"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def list_feedings(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """授乳記録一覧ページ"""
    feedings = db.query(Feeding).filter(
        Feeding.user_id == user.id
    ).order_by(Feeding.feeding_time.desc()).limit(50).all()

    return templates.TemplateResponse(
        "feeding/list.html",
        {"request": request, "user": user, "feedings": feedings}
    )


@router.get("/new", response_class=HTMLResponse)
async def new_feeding_form(
    request: Request,
    user: User = Depends(get_current_user)
):
    """新規授乳記録フォーム"""
    return templates.TemplateResponse(
        "feeding/form.html",
        {
            "request": request,
            "user": user,
            "feeding": None,
            "feeding_types": FeedingType
        }
    )


@router.post("", response_class=HTMLResponse)
async def create_feeding(
    request: Request,
    feeding_time: str = Form(...),
    feeding_type: str = Form(...),
    amount_ml: float = Form(None),
    duration_minutes: int = Form(None),
    notes: str = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """授乳記録作成"""
    # 日時のパース
    try:
        feeding_datetime = datetime.fromisoformat(feeding_time)
    except ValueError:
        raise HTTPException(status_code=400, detail="無効な日時形式です")

    # 新しい記録を作成
    new_feeding = Feeding(
        user_id=user.id,
        feeding_time=feeding_datetime,
        feeding_type=FeedingType(feeding_type),
        amount_ml=amount_ml if amount_ml else None,
        duration_minutes=duration_minutes if duration_minutes else None,
        notes=notes if notes else None
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
            "feedings": db.query(Feeding).filter(
                Feeding.user_id == user.id
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
    feeding_time: str = Form(...),
    feeding_type: str = Form(...),
    amount_ml: float = Form(None),
    duration_minutes: int = Form(None),
    notes: str = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """授乳記録更新"""
    feeding = db.query(Feeding).filter(
        Feeding.id == feeding_id,
        Feeding.user_id == user.id
    ).first()

    if not feeding:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    # 更新
    try:
        feeding.feeding_time = datetime.fromisoformat(feeding_time)
    except ValueError:
        raise HTTPException(status_code=400, detail="無効な日時形式です")

    feeding.feeding_type = FeedingType(feeding_type)
    feeding.amount_ml = amount_ml if amount_ml else None
    feeding.duration_minutes = duration_minutes if duration_minutes else None
    feeding.notes = notes if notes else None

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
            "feedings": db.query(Feeding).filter(
                Feeding.user_id == user.id
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
