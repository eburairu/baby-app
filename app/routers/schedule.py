"""スケジュール管理ルーター（JSON API専用）"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
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


@router.get("", response_model=ListResponse[ScheduleResponse])
async def list_schedules(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    family: Family = Depends(get_current_family),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("schedule"))
):
    """スケジュール一覧（JSON専用）"""
    schedules = db.query(Schedule).filter(
        Schedule.baby_id == baby.id
    ).order_by(Schedule.scheduled_time.asc()).all()

    # 閲覧可能な赤ちゃんリストを取得（グローバルナビゲーション用）
    baby_ids = [b.id for b in family.babies]
    perms_map = PermissionService.get_user_permissions_batch(
        db, user.id, baby_ids, family.id, "basic_info"
    )
    viewable_babies = [b for b in family.babies if perms_map.get(b.id, False)]

    return ListResponse(
        items=[ScheduleResponse.model_validate(s) for s in schedules],
        baby=BabyBasicInfo.model_validate(baby),
        viewable_babies=[BabyBasicInfo.model_validate(b) for b in viewable_babies]
    )


@router.post("", response_model=ScheduleResponse)
async def create_schedule(
    schedule_data: ScheduleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("schedule"))
):
    """スケジュール作成（JSON専用）"""
    new_schedule = Schedule(
        baby_id=baby.id,
        user_id=user.id,
        **schedule_data.model_dump()
    )

    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)

    return ScheduleResponse.model_validate(new_schedule)


@router.post("/{schedule_id}/toggle", response_model=ScheduleResponse)
async def toggle_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("schedule"))
):
    """スケジュール完了/未完了切り替え（JSON専用）"""
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.baby_id == baby.id
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="スケジュールが見つかりません")

    schedule.is_completed = not schedule.is_completed
    db.commit()
    db.refresh(schedule)

    return ScheduleResponse.model_validate(schedule)


@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
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
    update_data = schedule_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(schedule, key, value)

    db.commit()
    db.refresh(schedule)

    return ScheduleResponse.model_validate(schedule)


@router.delete("/{schedule_id}", response_model=dict)
async def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("schedule"))
):
    """スケジュール削除（JSON専用）"""
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.baby_id == baby.id
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="スケジュールが見つかりません")

    db.delete(schedule)
    db.commit()

    return {"success": True, "message": "削除しました"}
