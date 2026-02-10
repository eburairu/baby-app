"""おむつ交換記録ルーター"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.diaper import Diaper, DiaperType

router = APIRouter(prefix="/diapers", tags=["diapers"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def list_diapers(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """おむつ交換記録一覧ページ"""
    diapers = db.query(Diaper).filter(
        Diaper.user_id == user.id
    ).order_by(Diaper.change_time.desc()).limit(50).all()

    return templates.TemplateResponse(
        "diaper/list.html",
        {"request": request, "user": user, "diapers": diapers}
    )


@router.post("/quick", response_class=HTMLResponse)
async def quick_diaper(
    request: Request,
    diaper_type: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """ワンタップでおむつ交換記録"""
    new_diaper = Diaper(
        user_id=user.id,
        change_time=datetime.utcnow(),
        diaper_type=DiaperType(diaper_type)
    )

    db.add(new_diaper)
    db.commit()
    db.refresh(new_diaper)

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "diaper/item.html",
            {"request": request, "diaper": new_diaper}
        )

    diapers = db.query(Diaper).filter(
        Diaper.user_id == user.id
    ).order_by(Diaper.change_time.desc()).limit(50).all()

    return templates.TemplateResponse(
        "diaper/list.html",
        {"request": request, "user": user, "diapers": diapers}
    )


@router.get("/new", response_class=HTMLResponse)
async def new_diaper_form(
    request: Request,
    user: User = Depends(get_current_user)
):
    """新規おむつ交換記録フォーム"""
    return templates.TemplateResponse(
        "diaper/form.html",
        {
            "request": request,
            "user": user,
            "diaper": None,
            "diaper_types": DiaperType
        }
    )


@router.post("", response_class=HTMLResponse)
async def create_diaper(
    request: Request,
    change_time: str = Form(...),
    diaper_type: str = Form(...),
    notes: str = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """おむつ交換記録作成"""
    try:
        change_datetime = datetime.fromisoformat(change_time)
    except ValueError:
        raise HTTPException(status_code=400, detail="無効な日時形式です")

    new_diaper = Diaper(
        user_id=user.id,
        change_time=change_datetime,
        diaper_type=DiaperType(diaper_type),
        notes=notes if notes else None
    )

    db.add(new_diaper)
    db.commit()
    db.refresh(new_diaper)

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "diaper/item.html",
            {"request": request, "diaper": new_diaper}
        )

    diapers = db.query(Diaper).filter(
        Diaper.user_id == user.id
    ).order_by(Diaper.change_time.desc()).limit(50).all()

    return templates.TemplateResponse(
        "diaper/list.html",
        {"request": request, "user": user, "diapers": diapers}
    )


@router.delete("/{diaper_id}", response_class=HTMLResponse)
async def delete_diaper(
    diaper_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """おむつ交換記録削除"""
    diaper = db.query(Diaper).filter(
        Diaper.id == diaper_id,
        Diaper.user_id == user.id
    ).first()

    if not diaper:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    db.delete(diaper)
    db.commit()

    return ""
