"""睡眠記録ルーター"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.sleep import Sleep
from app.schemas.sleep import SleepCreate

router = APIRouter(prefix="/sleeps", tags=["sleeps"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def list_sleeps(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """睡眠記録一覧ページ"""
    sleeps = db.query(Sleep).filter(
        Sleep.user_id == user.id
    ).order_by(Sleep.start_time.desc()).limit(50).all()

    # 継続中の睡眠を取得
    ongoing_sleep = db.query(Sleep).filter(
        Sleep.user_id == user.id,
        Sleep.end_time == None
    ).first()

    return templates.TemplateResponse(
        "sleep/list.html",
        {
            "request": request,
            "user": user,
            "sleeps": sleeps,
            "ongoing_sleep": ongoing_sleep
        }
    )


@router.post("/start", response_class=HTMLResponse)
async def start_sleep(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """睡眠開始"""
    # 既に継続中の睡眠があるかチェック
    ongoing_sleep = db.query(Sleep).filter(
        Sleep.user_id == user.id,
        Sleep.end_time == None
    ).first()

    if ongoing_sleep:
        raise HTTPException(
            status_code=400,
            detail="既に睡眠が継続中です"
        )

    # 新しい睡眠記録を作成
    new_sleep = Sleep(
        user_id=user.id,
        start_time=datetime.utcnow()
    )

    db.add(new_sleep)
    db.commit()
    db.refresh(new_sleep)

    # 一覧ページにリダイレクト（htmxの場合は部分更新）
    sleeps = db.query(Sleep).filter(
        Sleep.user_id == user.id
    ).order_by(Sleep.start_time.desc()).limit(50).all()

    return templates.TemplateResponse(
        "sleep/list.html",
        {
            "request": request,
            "user": user,
            "sleeps": sleeps,
            "ongoing_sleep": new_sleep
        }
    )


@router.post("/{sleep_id}/end", response_class=HTMLResponse)
async def end_sleep(
    request: Request,
    sleep_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """睡眠終了"""
    sleep = db.query(Sleep).filter(
        Sleep.id == sleep_id,
        Sleep.user_id == user.id
    ).first()

    if not sleep:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    if sleep.end_time:
        raise HTTPException(
            status_code=400,
            detail="この睡眠は既に終了しています"
        )

    sleep.end_time = datetime.utcnow()
    db.commit()
    db.refresh(sleep)

    # 一覧ページにリダイレクト
    sleeps = db.query(Sleep).filter(
        Sleep.user_id == user.id
    ).order_by(Sleep.start_time.desc()).limit(50).all()

    return templates.TemplateResponse(
        "sleep/list.html",
        {
            "request": request,
            "user": user,
            "sleeps": sleeps,
            "ongoing_sleep": None
        }
    )


@router.get("/new", response_class=HTMLResponse)
async def new_sleep_form(
    request: Request,
    user: User = Depends(get_current_user)
):
    """新規睡眠記録フォーム（手動入力）"""
    return templates.TemplateResponse(
        "sleep/form.html",
        {"request": request, "user": user, "sleep": None}
    )


@router.post("", response_class=HTMLResponse)
async def create_sleep(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    form_data: SleepCreate = Depends(SleepCreate.as_form)
):
    """睡眠記録作成（手動入力）"""
    new_sleep = Sleep(
        user_id=user.id,
        **form_data.model_dump()
    )

    db.add(new_sleep)
    db.commit()
    db.refresh(new_sleep)

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "sleep/item.html",
            {"request": request, "sleep": new_sleep}
        )

    sleeps = db.query(Sleep).filter(
        Sleep.user_id == user.id
    ).order_by(Sleep.start_time.desc()).limit(50).all()

    ongoing_sleep = db.query(Sleep).filter(
        Sleep.user_id == user.id,
        Sleep.end_time == None
    ).first()

    return templates.TemplateResponse(
        "sleep/list.html",
        {
            "request": request,
            "user": user,
            "sleeps": sleeps,
            "ongoing_sleep": ongoing_sleep
        }
    )


@router.delete("/{sleep_id}", response_class=HTMLResponse)
async def delete_sleep(
    sleep_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """睡眠記録削除"""
    sleep = db.query(Sleep).filter(
        Sleep.id == sleep_id,
        Sleep.user_id == user.id
    ).first()

    if not sleep:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    db.delete(sleep)
    db.commit()

    return ""
