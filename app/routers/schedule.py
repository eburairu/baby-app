"""スケジュール管理ルーター"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_current_baby
from app.utils.templates import templates
from app.models.user import User
from app.models.baby import Baby
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.get("", response_class=HTMLResponse)
async def list_schedules(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby)
):
    """スケジュール一覧ページ"""
    schedules = db.query(Schedule).filter(
        Schedule.baby_id == baby.id
    ).order_by(Schedule.scheduled_time.asc()).all()

    response = templates.TemplateResponse(
        "schedule/list.html",
        {"request": request, "user": user, "baby": baby, "schedules": schedules}
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
async def new_schedule_form(
    request: Request,
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby)
):
    """新規スケジュールフォーム"""
    return templates.TemplateResponse(
        "schedule/form.html",
        {"request": request, "user": user, "baby": baby, "schedule": None}
    )


@router.post("", response_class=HTMLResponse)
async def create_schedule(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    form_data: ScheduleCreate = Depends(ScheduleCreate.as_form)
):
    """スケジュール作成"""
    new_schedule = Schedule(
        baby_id=baby.id,
        user_id=user.id,
        **form_data.model_dump()
    )

    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "schedule/item.html",
            {"request": request, "schedule": new_schedule}
        )

    schedules = db.query(Schedule).filter(
        Schedule.baby_id == baby.id
    ).order_by(Schedule.scheduled_time.asc()).all()

    return templates.TemplateResponse(
        "schedule/list.html",
        {"request": request, "user": user, "baby": baby, "schedules": schedules}
    )


@router.post("/{schedule_id}/toggle", response_class=HTMLResponse)
async def toggle_schedule(
    request: Request,
    schedule_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby)
):
    """スケジュール完了/未完了切り替え"""
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.baby_id == baby.id
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="スケジュールが見つかりません")

    schedule.is_completed = not schedule.is_completed
    db.commit()
    db.refresh(schedule)

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "schedule/item.html",
            {"request": request, "schedule": schedule}
        )

    schedules = db.query(Schedule).filter(
        Schedule.baby_id == baby.id
    ).order_by(Schedule.scheduled_time.asc()).all()

    return templates.TemplateResponse(
        "schedule/list.html",
        {"request": request, "user": user, "baby": baby, "schedules": schedules}
    )


@router.get("/{schedule_id}/edit", response_class=HTMLResponse)
async def edit_schedule_form(
    request: Request,
    schedule_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby)
):
    """スケジュール編集フォーム"""
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.baby_id == baby.id
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="スケジュールが見つかりません")

    return templates.TemplateResponse(
        "schedule/form.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "schedule": schedule
        }
    )


@router.post("/{schedule_id}", response_class=HTMLResponse)
async def update_schedule(
    request: Request,
    schedule_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    form_data: ScheduleUpdate = Depends(ScheduleUpdate.as_form)
):
    """スケジュール更新"""
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.baby_id == baby.id
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="スケジュールが見つかりません")

    # 更新データを適用
    update_data = form_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(schedule, key, value)

    db.commit()
    db.refresh(schedule)

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "schedule/item.html",
            {"request": request, "schedule": schedule}
        )

    schedules = db.query(Schedule).filter(
        Schedule.baby_id == baby.id
    ).order_by(Schedule.scheduled_time.asc()).all()

    return templates.TemplateResponse(
        "schedule/list.html",
        {"request": request, "user": user, "baby": baby, "schedules": schedules}
    )


@router.delete("/{schedule_id}", response_class=HTMLResponse)
async def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby)
):
    """スケジュール削除"""
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.baby_id == baby.id
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="スケジュールが見つかりません")

    db.delete(schedule)
    db.commit()

    return ""
