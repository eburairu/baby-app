"""睡眠記録ルーター"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.utils.time import get_now_naive

from app.database import get_db
from app.utils.templates import templates
from app.dependencies import get_current_user, get_current_baby, check_record_permission
from app.models.user import User
from app.models.baby import Baby
from app.models.sleep import Sleep
from app.schemas.sleep import SleepCreate, SleepUpdate

router = APIRouter(prefix="/sleeps", tags=["sleeps"])


@router.get("", response_class=HTMLResponse)
async def list_sleeps(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠記録一覧ページ"""
    sleeps = db.query(Sleep).filter(
        Sleep.baby_id == baby.id
    ).order_by(Sleep.start_time.desc()).limit(50).all()

    # 継続中の睡眠を取得
    ongoing_sleep = db.query(Sleep).filter(
        Sleep.baby_id == baby.id,
        Sleep.end_time == None
    ).first()

    response = templates.TemplateResponse(
        "sleep/list.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "sleeps": sleeps,
            "ongoing_sleep": ongoing_sleep
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


@router.post("/start", response_class=HTMLResponse)
async def start_sleep(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠開始"""
    # 既に継続中の睡眠があるかチェック
    ongoing_sleep = db.query(Sleep).filter(
        Sleep.baby_id == baby.id,
        Sleep.end_time == None
    ).first()

    if ongoing_sleep:
        raise HTTPException(
            status_code=400,
            detail="既に睡眠が継続中です"
        )

    # 新しい睡眠記録を作成
    new_sleep = Sleep(
        baby_id=baby.id,
        user_id=user.id,
        start_time=get_now_naive()
    )

    db.add(new_sleep)
    db.commit()
    db.refresh(new_sleep)

    # 一覧ページの内容を返す
    sleeps = db.query(Sleep).filter(
        Sleep.baby_id == baby.id
    ).order_by(Sleep.start_time.desc()).limit(50).all()

    return templates.TemplateResponse(
        "sleep/list.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "sleeps": sleeps,
            "ongoing_sleep": new_sleep
        }
    )


@router.post("/{sleep_id}/end", response_class=HTMLResponse)
async def end_sleep(
    request: Request,
    sleep_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠終了"""
    sleep = db.query(Sleep).filter(
        Sleep.id == sleep_id,
        Sleep.baby_id == baby.id
    ).first()

    if not sleep:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    if sleep.end_time:
        raise HTTPException(
            status_code=400,
            detail="この睡眠は既に終了しています"
        )

    sleep.end_time = get_now_naive()
    db.commit()
    db.refresh(sleep)

    # 一覧ページの内容を返す
    sleeps = db.query(Sleep).filter(
        Sleep.baby_id == baby.id
    ).order_by(Sleep.start_time.desc()).limit(50).all()

    return templates.TemplateResponse(
        "sleep/list.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "sleeps": sleeps,
            "ongoing_sleep": None
        }
    )


@router.post("", response_class=HTMLResponse)
async def create_sleep(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    form_data: SleepCreate = Depends(SleepCreate.as_form),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠記録作成（手動入力）"""
    new_sleep = Sleep(
        baby_id=baby.id,
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
        Sleep.baby_id == baby.id
    ).order_by(Sleep.start_time.desc()).limit(50).all()

    ongoing_sleep = db.query(Sleep).filter(
        Sleep.baby_id == baby.id,
        Sleep.end_time == None
    ).first()

    return templates.TemplateResponse(
        "sleep/list.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "sleeps": sleeps,
            "ongoing_sleep": ongoing_sleep
        }
    )


@router.get("/{sleep_id}/edit", response_class=HTMLResponse)
async def edit_sleep_form(
    request: Request,
    sleep_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠記録編集フォーム"""
    sleep = db.query(Sleep).filter(
        Sleep.id == sleep_id,
        Sleep.baby_id == baby.id
    ).first()

    if not sleep:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    return templates.TemplateResponse(
        "sleep/form.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "sleep": sleep
        }
    )


@router.post("/{sleep_id}", response_class=HTMLResponse)
async def update_sleep(
    request: Request,
    sleep_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    form_data: SleepUpdate = Depends(SleepUpdate.as_form),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠記録更新"""
    sleep = db.query(Sleep).filter(
        Sleep.id == sleep_id,
        Sleep.baby_id == baby.id
    ).first()

    if not sleep:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    # 更新データを適用
    update_data = form_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(sleep, key, value)

    db.commit()
    db.refresh(sleep)

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "sleep/item.html",
            {"request": request, "sleep": sleep}
        )

    sleeps = db.query(Sleep).filter(
        Sleep.baby_id == baby.id
    ).order_by(Sleep.start_time.desc()).limit(50).all()

    ongoing_sleep = db.query(Sleep).filter(
        Sleep.baby_id == baby.id,
        Sleep.end_time == None
    ).first()

    return templates.TemplateResponse(
        "sleep/list.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "sleeps": sleeps,
            "ongoing_sleep": ongoing_sleep
        }
    )


@router.delete("/{sleep_id}", response_class=HTMLResponse)
async def delete_sleep(
    sleep_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠記録削除"""
    sleep = db.query(Sleep).filter(
        Sleep.id == sleep_id,
        Sleep.baby_id == baby.id
    ).first()

    if not sleep:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    db.delete(sleep)
    db.commit()

    return ""
