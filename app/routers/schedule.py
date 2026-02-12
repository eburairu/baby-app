"""スケジュール管理ルーター"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_current_baby, get_current_family, check_record_permission
from app.models.user import User
from app.models.baby import Baby
from app.models.family import Family
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from app.schemas.responses import ListResponse, BabyBasicInfo
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.get("", response_model=None)
async def list_schedules(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    family: Family = Depends(get_current_family),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("schedule"))
):
    """スケジュール一覧ページ / スケジュール一覧API"""
    schedules = db.query(Schedule).filter(
        Schedule.baby_id == baby.id
    ).order_by(Schedule.scheduled_time.asc()).all()

    # 閲覧可能な赤ちゃんリストを取得（グローバルナビゲーション用）
    baby_ids = [b.id for b in family.babies]
    perms_map = PermissionService.get_user_permissions_batch(
        db, user.id, baby_ids, family.id, "basic_info"
    )
    viewable_babies = [b for b in family.babies if perms_map.get(b.id, False)]

    # JSON リクエストの場合
    if wants_json(request):
        return ListResponse(
            items=[ScheduleResponse.model_validate(s) for s in schedules],
            baby=BabyBasicInfo.model_validate(baby),
            viewable_babies=[BabyBasicInfo.model_validate(b) for b in viewable_babies]
        )

    # HTML レスポンス
    response = templates.TemplateResponse(
        "schedule/list.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "schedules": schedules,
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
async def new_schedule_form(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    family: Family = Depends(get_current_family),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("schedule"))
):
    """新規スケジュールフォーム"""
    # 閲覧可能な赤ちゃんリストを取得（グローバルナビゲーション用）
    baby_ids = [b.id for b in family.babies]
    perms_map = PermissionService.get_user_permissions_batch(
        db, user.id, baby_ids, family.id, "basic_info"
    )
    viewable_babies = [b for b in family.babies if perms_map.get(b.id, False)]

    return templates.TemplateResponse(
        "schedule/form.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "schedule": None,
            "viewable_babies": viewable_babies,
            "current_baby": baby
        }
    )


@router.post("", response_model=None)
async def create_schedule(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    data: ScheduleCreate = None,
    form_data: ScheduleCreate = Depends(ScheduleCreate.as_form),
    _ = Depends(check_record_permission("schedule"))
):
    """スケジュール作成"""
    # JSON または Form データを使用
    schedule_data = data if wants_json(request) else form_data

    new_schedule = Schedule(
        baby_id=baby.id,
        user_id=user.id,
        **schedule_data.model_dump()
    )

    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)

    # JSON リクエストの場合
    if wants_json(request):
        return ScheduleResponse.model_validate(new_schedule)

    # HTML レスポンス
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


@router.post("/{schedule_id}/toggle", response_model=None)
async def toggle_schedule(
    request: Request,
    schedule_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("schedule"))
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

    # JSON リクエストの場合
    if wants_json(request):
        return ScheduleResponse.model_validate(schedule)

    # HTML レスポンス
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
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("schedule"))
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


@router.put("/{schedule_id}", response_model=None)
async def update_schedule_json(
    schedule_id: int,
    data: ScheduleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("schedule"))
):
    """スケジュール更新（JSON専用）"""
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.baby_id == baby.id
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="スケジュールが見つかりません")

    # 更新データを適用
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(schedule, key, value)

    db.commit()
    db.refresh(schedule)

    return ScheduleResponse.model_validate(schedule)


@router.post("/{schedule_id}", response_class=HTMLResponse)
async def update_schedule(
    request: Request,
    schedule_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    form_data: ScheduleUpdate = Depends(ScheduleUpdate.as_form),
    _ = Depends(check_record_permission("schedule"))
):
    """スケジュール更新（HTML用）"""
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


@router.delete("/{schedule_id}", response_model=None)
async def delete_schedule(
    request: Request,
    schedule_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("schedule"))
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

    # JSON リクエストの場合
    if wants_json(request):
        return {"message": "削除しました"}

    # HTML レスポンス
    return ""
