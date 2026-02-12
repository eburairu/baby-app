"""成長記録ルーター（JSON API専用）"""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_current_baby, get_current_family, check_record_permission
from app.models.user import User
from app.models.baby import Baby
from app.models.family import Family
from app.models.growth import Growth
from app.schemas.growth import GrowthCreate, GrowthUpdate, GrowthResponse
from app.schemas.responses import ListResponse, BabyBasicInfo
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/growths", tags=["growths"])


@router.get("", response_model=ListResponse[GrowthResponse])
async def list_growths(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    family: Family = Depends(get_current_family),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("growth"))
):
    """成長記録一覧（JSON専用）"""
    growths = db.query(Growth).filter(
        Growth.baby_id == baby.id
    ).order_by(Growth.measurement_date.desc()).all()

    # 閲覧可能な赤ちゃんリストを取得（グローバルナビゲーション用）
    baby_ids = [b.id for b in family.babies]
    perms_map = PermissionService.get_user_permissions_batch(
        db, user.id, baby_ids, family.id, "basic_info"
    )
    viewable_babies = [b for b in family.babies if perms_map.get(b.id, False)]

    return ListResponse(
        items=[GrowthResponse.model_validate(g) for g in growths],
        baby=BabyBasicInfo.model_validate(baby),
        viewable_babies=[BabyBasicInfo.model_validate(b) for b in viewable_babies]
    )


@router.post("", response_model=GrowthResponse)
async def create_growth(
    growth_data: GrowthCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("growth"))
):
    """成長記録作成（JSON専用）"""
    new_growth = Growth(
        baby_id=baby.id,
        user_id=user.id,
        **growth_data.model_dump()
    )

    db.add(new_growth)
    db.commit()
    db.refresh(new_growth)

    return GrowthResponse.model_validate(new_growth)


@router.get("/{growth_id}", response_model=GrowthResponse)
async def get_growth(
    growth_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("growth"))
):
    """成長記録詳細取得（JSON専用）"""
    growth = db.query(Growth).filter(
        Growth.id == growth_id,
        Growth.baby_id == baby.id
    ).first()

    if not growth:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    return GrowthResponse.model_validate(growth)


@router.put("/{growth_id}", response_model=GrowthResponse)
async def update_growth(
    growth_id: int,
    growth_data: GrowthUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("growth"))
):
    """成長記録更新（JSON専用）"""
    growth = db.query(Growth).filter(
        Growth.id == growth_id,
        Growth.baby_id == baby.id
    ).first()

    if not growth:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    # 更新データを適用
    update_dict = growth_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(growth, key, value)

    db.commit()
    db.refresh(growth)

    return GrowthResponse.model_validate(growth)


@router.delete("/{growth_id}", response_model=dict)
async def delete_growth(
    growth_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("growth"))
):
    """成長記録削除（JSON専用）"""
    growth = db.query(Growth).filter(
        Growth.id == growth_id,
        Growth.baby_id == baby.id
    ).first()

    if not growth:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    db.delete(growth)
    db.commit()

    return {"success": True, "message": "削除しました"}
