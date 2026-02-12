"""赤ちゃん管理ルーター（JSON API専用）"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app.models.baby import Baby
from app.models.family import Family
from app.dependencies import get_current_user, get_current_family, admin_required
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/babies", tags=["baby"])


# ===== レスポンススキーマ =====

class BabyResponse(BaseModel):
    """赤ちゃん情報レスポンス"""
    id: int
    name: str
    birthday: date | None = None
    due_date: date | None = None

    class Config:
        from_attributes = True


class BabiesListResponse(BaseModel):
    """赤ちゃん一覧レスポンス"""
    babies: List[BabyResponse]
    family_id: int
    family_name: str


class BabyCreateRequest(BaseModel):
    """赤ちゃん作成リクエスト"""
    name: str
    birthday: date | None = None
    due_date: date | None = None


class BabyBornRequest(BaseModel):
    """出生記録リクエスト"""
    birthday: date


# ===== JSON API エンドポイント =====

@router.get("", response_model=BabiesListResponse)
async def list_babies(
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
    family: Family = Depends(get_current_family)
):
    """
    赤ちゃん一覧を取得（JSON専用）

    フロントエンドの赤ちゃんセレクター用
    """
    # 閲覧可能な赤ちゃんのみに絞り込む
    baby_ids = [b.id for b in family.babies]
    perms_map = PermissionService.get_user_permissions_batch(
        db, user.id, baby_ids, family.id, "basic_info"
    )
    visible_babies = [b for b in family.babies if perms_map.get(b.id, False)]

    return BabiesListResponse(
        babies=[BabyResponse.model_validate(b) for b in visible_babies],
        family_id=family.id,
        family_name=family.name
    )


@router.post("", response_model=BabyResponse)
async def create_baby(
    baby_data: BabyCreateRequest,
    db: Session = Depends(get_db),
    family = Depends(get_current_family),
    _ = Depends(admin_required)
):
    """赤ちゃんを登録（JSON専用）"""
    baby = Baby(
        family_id=family.id,
        name=baby_data.name,
        birthday=baby_data.birthday,
        due_date=baby_data.due_date
    )
    db.add(baby)
    db.commit()
    db.refresh(baby)
    return BabyResponse.model_validate(baby)


@router.post("/{baby_id}/born", response_model=BabyResponse)
async def baby_born(
    baby_id: int,
    born_data: BabyBornRequest,
    db: Session = Depends(get_db),
    family = Depends(get_current_family),
    _ = Depends(admin_required)
):
    """赤ちゃんが生まれたことを記録（誕生日設定、JSON専用）"""
    baby = db.query(Baby).filter(Baby.id == baby_id, Baby.family_id == family.id).first()
    if not baby:
        raise HTTPException(status_code=404, detail="Baby not found")

    baby.birthday = born_data.birthday
    db.commit()
    db.refresh(baby)

    return BabyResponse.model_validate(baby)


@router.delete("/{baby_id}", response_model=dict)
async def delete_baby(
    baby_id: int,
    db: Session = Depends(get_db),
    family = Depends(get_current_family),
    _ = Depends(admin_required)
):
    """赤ちゃんを削除（JSON専用）"""
    baby = db.query(Baby).filter(Baby.id == baby_id, Baby.family_id == family.id).first()
    if not baby:
        raise HTTPException(status_code=404, detail="Baby not found")

    db.delete(baby)
    db.commit()

    return {"success": True, "message": "削除しました"}
