"""おむつ交換記録ルーター（JSON API専用）"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.time import get_now_naive

from app.database import get_db
from app.dependencies import get_current_user, get_current_baby, get_current_family, check_record_permission
from app.models.user import User
from app.models.baby import Baby
from app.models.family import Family
from app.models.diaper import Diaper, DiaperType
from app.schemas.diaper import DiaperCreate, DiaperUpdate, DiaperResponse, QuickDiaperRequest
from app.schemas.responses import ListResponse, BabyBasicInfo
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/diapers", tags=["diapers"])


@router.get("", response_model=ListResponse[DiaperResponse])
async def list_diapers(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    family: Family = Depends(get_current_family),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("diaper"))
):
    """おむつ交換記録一覧（JSON専用）"""
    diapers = db.query(Diaper).filter(
        Diaper.baby_id == baby.id
    ).order_by(Diaper.change_time.desc()).limit(50).all()

    # 閲覧可能な赤ちゃんリストを取得（グローバルナビゲーション用）
    baby_ids = [b.id for b in family.babies]
    perms_map = PermissionService.get_user_permissions_batch(
        db, user.id, baby_ids, family.id, "basic_info"
    )
    viewable_babies = [b for b in family.babies if perms_map.get(b.id, False)]

    return ListResponse(
        items=[DiaperResponse.model_validate(d) for d in diapers],
        baby=BabyBasicInfo.model_validate(baby),
        viewable_babies=[BabyBasicInfo.model_validate(b) for b in viewable_babies]
    )


@router.post("/quick", response_model=DiaperResponse)
async def quick_diaper(
    quick_data: QuickDiaperRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("diaper"))
):
    """ワンタップでおむつ交換記録（JSON専用）"""
    new_diaper = Diaper(
        baby_id=baby.id,
        user_id=user.id,
        change_time=get_now_naive(),
        diaper_type=DiaperType(quick_data.diaper_type)
    )

    db.add(new_diaper)
    db.commit()
    db.refresh(new_diaper)

    return DiaperResponse.model_validate(new_diaper)


@router.post("", response_model=DiaperResponse)
async def create_diaper(
    diaper_data: DiaperCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("diaper"))
):
    """おむつ交換記録作成（JSON専用）"""
    new_diaper = Diaper(
        baby_id=baby.id,
        user_id=user.id,
        **diaper_data.model_dump()
    )

    db.add(new_diaper)
    db.commit()
    db.refresh(new_diaper)

    return DiaperResponse.model_validate(new_diaper)


@router.get("/{diaper_id}", response_model=DiaperResponse)
async def get_diaper(
    diaper_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("diaper"))
):
    """おむつ交換記録詳細取得（JSON専用）"""
    diaper = db.query(Diaper).filter(
        Diaper.id == diaper_id,
        Diaper.baby_id == baby.id
    ).first()

    if not diaper:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    return DiaperResponse.model_validate(diaper)


@router.put("/{diaper_id}", response_model=DiaperResponse)
async def update_diaper(
    diaper_id: int,
    diaper_data: DiaperUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("diaper"))
):
    """おむつ交換記録更新（JSON専用）"""
    diaper = db.query(Diaper).filter(
        Diaper.id == diaper_id,
        Diaper.baby_id == baby.id
    ).first()

    if not diaper:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    # 更新データを適用
    update_dict = diaper_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(diaper, key, value)

    db.commit()
    db.refresh(diaper)

    return DiaperResponse.model_validate(diaper)


@router.delete("/{diaper_id}", response_model=dict)
async def delete_diaper(
    diaper_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("diaper"))
):
    """おむつ交換記録削除（JSON専用）"""
    diaper = db.query(Diaper).filter(
        Diaper.id == diaper_id,
        Diaper.baby_id == baby.id
    ).first()

    if not diaper:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    db.delete(diaper)
    db.commit()

    return {"success": True, "message": "削除しました"}
