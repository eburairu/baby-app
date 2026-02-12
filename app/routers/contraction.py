"""陣痛タイマールーター（JSON API専用）"""
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
from app.models.contraction import Contraction
from app.schemas.contraction import ContractionUpdate, ContractionCreate, ContractionResponse
from app.schemas.responses import BabyBasicInfo
from app.services.contraction_service import ContractionService
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/contractions", tags=["contractions"])


@router.get("", response_model=dict)
async def contraction_timer(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    family: Family = Depends(get_current_family),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("contraction"))
):
    """陣痛タイマーページ / 陣痛一覧API（JSON専用）"""
    # 継続中の陣痛を取得
    ongoing_contraction = db.query(Contraction).filter(
        Contraction.baby_id == baby.id,
        Contraction.end_time == None
    ).first()

    # 陣痛記録一覧（最新20件）
    contractions = db.query(Contraction).filter(
        Contraction.baby_id == baby.id
    ).order_by(Contraction.start_time.desc()).limit(20).all()

    # 直近1時間の統計
    stats = ContractionService.get_statistics(db, baby.id, hours=1)

    # 閲覧可能な赤ちゃんリストを取得（グローバルナビゲーション用）
    baby_ids = [b.id for b in family.babies]
    perms_map = PermissionService.get_user_permissions_batch(
        db, user.id, baby_ids, family.id, "basic_info"
    )
    viewable_babies = [b for b in family.babies if perms_map.get(b.id, False)]

    return {
        "items": [ContractionResponse.model_validate(c) for c in contractions],
        "ongoing": ContractionResponse.model_validate(ongoing_contraction) if ongoing_contraction else None,
        "stats": stats,
        "baby": BabyBasicInfo.model_validate(baby),
        "viewable_babies": [BabyBasicInfo.model_validate(b) for b in viewable_babies]
    }


@router.post("/start", response_model=ContractionResponse)
async def start_contraction(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("contraction"))
):
    """陣痛開始（JSON専用）"""
    # 既に継続中の陣痛があるかチェック
    ongoing = db.query(Contraction).filter(
        Contraction.baby_id == baby.id,
        Contraction.end_time == None
    ).first()

    if ongoing:
        raise HTTPException(
            status_code=400,
            detail="既に陣痛が継続中です"
        )

    # 前回からの間隔を計算
    interval_seconds = ContractionService.calculate_interval(db, baby.id)

    # 新しい陣痛記録を作成
    new_contraction = Contraction(
        baby_id=baby.id,
        user_id=user.id,
        start_time=get_now_naive(),
        interval_seconds=interval_seconds
    )

    db.add(new_contraction)
    db.commit()
    db.refresh(new_contraction)

    return ContractionResponse.model_validate(new_contraction)


@router.post("/{contraction_id}/end", response_model=ContractionResponse)
async def end_contraction(
    contraction_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("contraction"))
):
    """陣痛終了（JSON専用）"""
    contraction = db.query(Contraction).filter(
        Contraction.id == contraction_id,
        Contraction.baby_id == baby.id
    ).first()

    if not contraction:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    if contraction.end_time:
        raise HTTPException(
            status_code=400,
            detail="この陣痛は既に終了しています"
        )

    # 終了時刻と持続時間を設定
    end_time = get_now_naive()
    contraction.end_time = end_time
    contraction.duration_seconds = ContractionService.calculate_duration(
        contraction.start_time,
        end_time
    )

    db.commit()
    db.refresh(contraction)

    return ContractionResponse.model_validate(contraction)


@router.get("/list", response_model=dict)
async def contraction_list(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("contraction"))
):
    """陣痛記録一覧（自動更新用、JSON専用）"""
    contractions = db.query(Contraction).filter(
        Contraction.baby_id == baby.id
    ).order_by(Contraction.start_time.desc()).limit(20).all()

    stats = ContractionService.get_statistics(db, baby.id, hours=1)

    return {
        "items": [ContractionResponse.model_validate(c) for c in contractions],
        "stats": stats
    }


@router.post("", response_model=ContractionResponse)
async def create_contraction(
    data: ContractionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("contraction"))
):
    """陣痛記録を手動で作成（JSON専用）"""
    # 前回からの間隔を計算
    interval_seconds = ContractionService.calculate_interval(db, baby.id)

    new_contraction = Contraction(
        baby_id=baby.id,
        user_id=user.id,
        start_time=data.start_time,
        interval_seconds=interval_seconds,
        notes=data.notes
    )

    db.add(new_contraction)
    db.commit()
    db.refresh(new_contraction)

    return ContractionResponse.model_validate(new_contraction)


@router.put("/{contraction_id}", response_model=ContractionResponse)
async def update_contraction(
    contraction_id: int,
    data: ContractionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("contraction"))
):
    """陣痛記録更新（JSON専用）"""
    contraction = db.query(Contraction).filter(
        Contraction.id == contraction_id,
        Contraction.baby_id == baby.id
    ).first()

    if not contraction:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    # 更新データを適用
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(contraction, key, value)

    # 持続時間を再計算
    if contraction.end_time:
        contraction.duration_seconds = ContractionService.calculate_duration(
            contraction.start_time,
            contraction.end_time
        )
    else:
        contraction.duration_seconds = None

    db.commit()

    # 全ての間隔を再計算（開始時間が前後する可能性があるため）
    all_contractions = db.query(Contraction).filter(
        Contraction.baby_id == baby.id
    ).order_by(Contraction.start_time.asc()).all()

    prev_end = None
    for c in all_contractions:
        if prev_end:
            c.interval_seconds = int((c.start_time - prev_end).total_seconds())
        else:
            c.interval_seconds = None
        prev_end = c.end_time

    db.commit()
    db.refresh(contraction)

    return ContractionResponse.model_validate(contraction)


@router.delete("/{contraction_id}", response_model=dict)
async def delete_contraction(
    contraction_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("contraction"))
):
    """陣痛記録削除（JSON専用）"""
    contraction = db.query(Contraction).filter(
        Contraction.id == contraction_id,
        Contraction.baby_id == baby.id
    ).first()

    if not contraction:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    db.delete(contraction)
    db.commit()

    return {"success": True, "message": "削除しました"}
