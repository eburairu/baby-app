"""睡眠記録ルーター（JSON API専用）"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.time import get_now_naive

from app.database import get_db
from app.dependencies import get_current_user, get_current_baby, get_current_family, check_record_permission
from app.models.user import User
from app.models.baby import Baby
from app.models.family import Family
from app.models.sleep import Sleep
from app.schemas.sleep import SleepCreate, SleepUpdate, SleepResponse
from app.schemas.responses import ListResponse, BabyBasicInfo
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/sleeps", tags=["sleeps"])


@router.get("", response_model=ListResponse[SleepResponse])
async def list_sleeps(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    family: Family = Depends(get_current_family),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠記録一覧（JSON専用）"""
    sleeps = db.query(Sleep).filter(
        Sleep.baby_id == baby.id
    ).order_by(Sleep.start_time.desc()).limit(50).all()

    # 継続中の睡眠を取得
    ongoing_sleep = db.query(Sleep).filter(
        Sleep.baby_id == baby.id,
        Sleep.end_time == None
    ).first()

    # 閲覧可能な赤ちゃんリストを取得（グローバルナビゲーション用）
    baby_ids = [b.id for b in family.babies]
    perms_map = PermissionService.get_user_permissions_batch(
        db, user.id, baby_ids, family.id, "basic_info"
    )
    viewable_babies = [b for b in family.babies if perms_map.get(b.id, False)]

    return ListResponse(
        items=[SleepResponse.model_validate(s) for s in sleeps],
        baby=BabyBasicInfo.model_validate(baby) if baby else None,
        viewable_babies=[BabyBasicInfo.model_validate(b) for b in viewable_babies],
        ongoing_sleep=SleepResponse.model_validate(ongoing_sleep) if ongoing_sleep else None,
    )


@router.post("/start", response_model=SleepResponse)
async def start_sleep(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠開始（JSON専用）"""
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

    return SleepResponse.model_validate(new_sleep)


@router.post("/{sleep_id}/end", response_model=SleepResponse)
async def end_sleep(
    sleep_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠終了（JSON専用）"""
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

    return SleepResponse.model_validate(sleep)


@router.post("", response_model=SleepResponse)
async def create_sleep(
    sleep_data: SleepCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠記録作成（手動入力、JSON専用）"""
    new_sleep = Sleep(
        baby_id=baby.id,
        user_id=user.id,
        **sleep_data.model_dump()
    )

    db.add(new_sleep)
    db.commit()
    db.refresh(new_sleep)

    return SleepResponse.model_validate(new_sleep)


@router.get("/{sleep_id}", response_model=SleepResponse)
async def get_sleep(
    sleep_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠記録詳細取得（JSON専用）"""
    sleep = db.query(Sleep).filter(
        Sleep.id == sleep_id,
        Sleep.baby_id == baby.id
    ).first()

    if not sleep:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    return SleepResponse.model_validate(sleep)


@router.put("/{sleep_id}", response_model=SleepResponse)
async def update_sleep(
    sleep_id: int,
    sleep_data: SleepUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠記録更新（JSON専用）"""
    sleep = db.query(Sleep).filter(
        Sleep.id == sleep_id,
        Sleep.baby_id == baby.id
    ).first()

    if not sleep:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    # 更新データを適用
    update_dict = sleep_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(sleep, key, value)

    db.commit()
    db.refresh(sleep)

    return SleepResponse.model_validate(sleep)


@router.delete("/{sleep_id}", response_model=dict)
async def delete_sleep(
    sleep_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠記録削除（JSON専用）"""
    sleep = db.query(Sleep).filter(
        Sleep.id == sleep_id,
        Sleep.baby_id == baby.id
    ).first()

    if not sleep:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    db.delete(sleep)
    db.commit()

    return {"success": True, "message": "削除しました"}
