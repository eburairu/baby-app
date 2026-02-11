"""スケジュール管理ルーター"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate

router = APIRouter(prefix="/schedules", tags=["schedules"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def list_schedules(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """スケジュール一覧ページ"""
    schedules = db.query(Schedule).filter(
        Schedule.user_id == user.id
    ).order_by(Schedule.scheduled_time.asc()).all()

    return templates.TemplateResponse(
        "schedule/list.html",
        {"request": request, "user": user, "schedules": schedules}
    )


@router.get("/new", response_class=HTMLResponse)
async def new_schedule_form(
    request: Request,
    user: User = Depends(get_current_user)
):
    """新規スケジュールフォーム"""
    return templates.TemplateResponse(
        "schedule/form.html",
        {"request": request, "user": user, "schedule": None}
    )


@router.post("", response_class=HTMLResponse)
async def create_schedule(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    form_data: ScheduleCreate = Depends(ScheduleCreate.as_form)
):
    """スケジュール作成"""
    new_schedule = Schedule(
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
        Schedule.user_id == user.id
    ).order_by(Schedule.scheduled_time.asc()).all()

    return templates.TemplateResponse(
        "schedule/list.html",
        {"request": request, "user": user, "schedules": schedules}
    )


@router.post("/{schedule_id}/toggle", response_class=HTMLResponse)
async def toggle_schedule(
    request: Request,
    schedule_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """スケジュール完了/未完了切り替え"""
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.user_id == user.id
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
        Schedule.user_id == user.id
    ).order_by(Schedule.scheduled_time.asc()).all()

    return templates.TemplateResponse(
        "schedule/list.html",
        {"request": request, "user": user, "schedules": schedules}
    )


@router.delete("/{schedule_id}", response_class=HTMLResponse)
async def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """スケジュール削除"""
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.user_id == user.id
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="スケジュールが見つかりません")

    db.delete(schedule)
    db.commit()

    return ""
