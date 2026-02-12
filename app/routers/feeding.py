"""授乳記録ルーター（JSON API専用）"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_current_baby, get_current_family, check_record_permission
from app.models.user import User
from app.models.baby import Baby
from app.models.family import Family
from app.models.feeding import Feeding
from app.schemas.feeding import FeedingResponse, FeedingCreate, FeedingUpdate
from app.schemas.responses import ListResponse, BabyBasicInfo
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/feedings", tags=["feedings"])


@router.get("", response_model=ListResponse[FeedingResponse])
async def list_feedings(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    family: Family = Depends(get_current_family),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("feeding"))
):
    """授乳記録一覧API"""
    feedings = db.query(Feeding).filter(
        Feeding.baby_id == baby.id
    ).order_by(Feeding.feeding_time.desc()).limit(50).all()

    # 閲覧可能な赤ちゃんリストを取得
    baby_ids = [b.id for b in family.babies]
    perms_map = PermissionService.get_user_permissions_batch(
        db, user.id, baby_ids, family.id, "basic_info"
    )
    viewable_babies = [b for b in family.babies if perms_map.get(b.id, False)]

    return ListResponse(
        items=[FeedingResponse.model_validate(f) for f in feedings],
        baby=BabyBasicInfo.model_validate(baby),
        viewable_babies=[BabyBasicInfo.model_validate(b) for b in viewable_babies]
    )


@router.post("", response_model=FeedingResponse)
async def create_feeding(
    data: FeedingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("feeding"))
):
    """授乳記録作成API"""
    new_feeding = Feeding(
        user_id=user.id,
        baby_id=baby.id,
        **data.model_dump()
    )

    db.add(new_feeding)
    db.commit()
    db.refresh(new_feeding)

    return FeedingResponse.model_validate(new_feeding)


@router.get("/{feeding_id}", response_model=FeedingResponse)
async def get_feeding(
    feeding_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("feeding"))
):
    """授乳記録詳細取得API"""
    feeding = db.query(Feeding).filter(
        Feeding.id == feeding_id,
        Feeding.baby_id == baby.id
    ).first()

    if not feeding:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    return FeedingResponse.model_validate(feeding)


@router.put("/{feeding_id}", response_model=FeedingResponse)
async def update_feeding(
    feeding_id: int,
    data: FeedingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("feeding"))
):
    """授乳記録更新API"""
    feeding = db.query(Feeding).filter(
        Feeding.id == feeding_id,
        Feeding.baby_id == baby.id
    ).first()

    if not feeding:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    # 更新データを適用
    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(feeding, key, value)

    db.commit()
    db.refresh(feeding)

    return FeedingResponse.model_validate(feeding)


@router.delete("/{feeding_id}")
async def delete_feeding(
    feeding_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("feeding"))
):
    """授乳記録削除API"""
    feeding = db.query(Feeding).filter(
        Feeding.id == feeding_id,
        Feeding.baby_id == baby.id
    ).first()

    if not feeding:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    db.delete(feeding)
    db.commit()

    return {"message": "削除しました"}
