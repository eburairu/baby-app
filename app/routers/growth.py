"""成長記録ルーター"""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.growth import Growth

router = APIRouter(prefix="/growths", tags=["growths"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def list_growths(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """成長記録一覧ページ"""
    growths = db.query(Growth).filter(
        Growth.user_id == user.id
    ).order_by(Growth.measurement_date.desc()).all()

    return templates.TemplateResponse(
        "growth/list.html",
        {"request": request, "user": user, "growths": growths}
    )


@router.get("/chart", response_class=HTMLResponse)
async def growth_chart(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """成長グラフページ"""
    growths = db.query(Growth).filter(
        Growth.user_id == user.id
    ).order_by(Growth.measurement_date.asc()).all()

    return templates.TemplateResponse(
        "growth/chart.html",
        {"request": request, "user": user, "growths": growths}
    )


@router.get("/new", response_class=HTMLResponse)
async def new_growth_form(
    request: Request,
    user: User = Depends(get_current_user)
):
    """新規成長記録フォーム"""
    return templates.TemplateResponse(
        "growth/form.html",
        {"request": request, "user": user, "growth": None}
    )


@router.post("", response_class=HTMLResponse)
async def create_growth(
    request: Request,
    measurement_date: str = Form(...),
    weight_kg: float = Form(None),
    height_cm: float = Form(None),
    head_circumference_cm: float = Form(None),
    notes: str = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """成長記録作成"""
    try:
        measurement_date_obj = date.fromisoformat(measurement_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="無効な日付形式です")

    new_growth = Growth(
        user_id=user.id,
        measurement_date=measurement_date_obj,
        weight_kg=weight_kg if weight_kg else None,
        height_cm=height_cm if height_cm else None,
        head_circumference_cm=head_circumference_cm if head_circumference_cm else None,
        notes=notes if notes else None
    )

    db.add(new_growth)
    db.commit()
    db.refresh(new_growth)

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "growth/item.html",
            {"request": request, "growth": new_growth}
        )

    growths = db.query(Growth).filter(
        Growth.user_id == user.id
    ).order_by(Growth.measurement_date.desc()).all()

    return templates.TemplateResponse(
        "growth/list.html",
        {"request": request, "user": user, "growths": growths}
    )


@router.get("/{growth_id}/edit", response_class=HTMLResponse)
async def edit_growth_form(
    request: Request,
    growth_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """成長記録編集フォーム"""
    growth = db.query(Growth).filter(
        Growth.id == growth_id,
        Growth.user_id == user.id
    ).first()

    if not growth:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    return templates.TemplateResponse(
        "growth/form.html",
        {"request": request, "user": user, "growth": growth}
    )


@router.post("/{growth_id}", response_class=HTMLResponse)
async def update_growth(
    request: Request,
    growth_id: int,
    measurement_date: str = Form(...),
    weight_kg: float = Form(None),
    height_cm: float = Form(None),
    head_circumference_cm: float = Form(None),
    notes: str = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """成長記録更新"""
    growth = db.query(Growth).filter(
        Growth.id == growth_id,
        Growth.user_id == user.id
    ).first()

    if not growth:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    try:
        growth.measurement_date = date.fromisoformat(measurement_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="無効な日付形式です")

    growth.weight_kg = weight_kg if weight_kg else None
    growth.height_cm = height_cm if height_cm else None
    growth.head_circumference_cm = head_circumference_cm if head_circumference_cm else None
    growth.notes = notes if notes else None

    db.commit()
    db.refresh(growth)

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "growth/item.html",
            {"request": request, "growth": growth}
        )

    growths = db.query(Growth).filter(
        Growth.user_id == user.id
    ).order_by(Growth.measurement_date.desc()).all()

    return templates.TemplateResponse(
        "growth/list.html",
        {"request": request, "user": user, "growths": growths}
    )


@router.delete("/{growth_id}", response_class=HTMLResponse)
async def delete_growth(
    growth_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """成長記録削除"""
    growth = db.query(Growth).filter(
        Growth.id == growth_id,
        Growth.user_id == user.id
    ).first()

    if not growth:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    db.delete(growth)
    db.commit()

    return ""
