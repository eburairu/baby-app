"""家族管理ルーター（JSON API専用）"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.family import Family
from app.models.family_user import FamilyUser
from app.dependencies import get_current_user, get_current_family, admin_required
from app.services.family_service import FamilyService
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/families", tags=["family"])


# ===== レスポンススキーマ =====

class FamilyResponse(BaseModel):
    """家族情報レスポンス"""
    id: int
    name: str
    invite_code: str

    class Config:
        from_attributes = True


class FamilyCreateRequest(BaseModel):
    """家族作成リクエスト"""
    name: str


class FamilyJoinRequest(BaseModel):
    """家族参加リクエスト"""
    invite_code: str


class MemberResponse(BaseModel):
    """メンバー情報レスポンス"""
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True


class PermissionUpdateRequest(BaseModel):
    """権限更新リクエスト"""
    baby_id: int
    permissions: dict[str, bool]


# ===== JSON API エンドポイント =====

@router.get("/me", response_model=FamilyResponse)
async def get_my_family(
    family: Family = Depends(get_current_family)
):
    """
    現在の家族情報を取得（JSON専用）

    フロントエンド用
    """
    return FamilyResponse.model_validate(family)


@router.post("", response_model=FamilyResponse)
async def create_family(
    family_data: FamilyCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """家族を新規作成（JSON専用）"""
    family = FamilyService.create_family(db, user, family_data.name)
    return FamilyResponse.model_validate(family)


@router.post("/join", response_model=FamilyResponse)
async def join_family(
    join_data: FamilyJoinRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """招待コードで家族に参加（JSON専用）"""
    family = FamilyService.join_family(db, user, join_data.invite_code.upper())
    if not family:
        raise HTTPException(status_code=400, detail="無効な招待コードです")

    return FamilyResponse.model_validate(family)


@router.get("/members", response_model=List[MemberResponse])
async def list_members(
    db: Session = Depends(get_db),
    family: Family = Depends(get_current_family)
):
    """家族メンバー一覧を取得（JSON専用）"""
    members = []
    for fu in family.family_users:
        members.append({
            "id": fu.user.id,
            "username": fu.user.username,
            "role": fu.role
        })
    return members


@router.post("/members/{target_user_id}/permissions", response_model=dict)
async def update_member_permissions(
    target_user_id: int,
    permissions_data: List[PermissionUpdateRequest],
    user: User = Depends(get_current_user),
    family: Family = Depends(get_current_family),
    db: Session = Depends(get_db)
):
    """メンバーの権限設定を更新（JSON専用）"""
    # 管理者チェック
    if not FamilyService.is_admin(db, user.id, family.id):
        raise HTTPException(status_code=403, detail="管理者権限が必要です")

    # 対象ユーザーが同じ家族かチェック
    target_fu = db.query(FamilyUser).filter(
        FamilyUser.family_id == family.id,
        FamilyUser.user_id == target_user_id
    ).first()
    if not target_fu:
        raise HTTPException(status_code=404, detail="メンバーが見つかりません")

    # 更新実行
    for perm_data in permissions_data:
        PermissionService.update_permissions(
            db, target_user_id, perm_data.baby_id, perm_data.permissions
        )

    return {"success": True, "message": "権限を更新しました"}


@router.get("/members/{target_user_id}/permissions", response_model=dict)
async def get_member_permissions(
    target_user_id: int,
    user: User = Depends(get_current_user),
    family: Family = Depends(get_current_family),
    db: Session = Depends(get_db)
):
    """メンバーの権限設定を取得（JSON専用）"""
    # 管理者チェック
    if not FamilyService.is_admin(db, user.id, family.id):
        raise HTTPException(status_code=403, detail="管理者権限が必要です")

    # 対象ユーザーが同じ家族かチェック
    target_fu = db.query(FamilyUser).filter(
        FamilyUser.family_id == family.id,
        FamilyUser.user_id == target_user_id
    ).first()
    if not target_fu:
        raise HTTPException(status_code=404, detail="メンバーが見つかりません")

    # 各赤ちゃんと各記録タイプの権限状況を取得
    permissions_data = []
    for baby in family.babies:
        perms = PermissionService.get_user_permissions(db, target_user_id, baby.id, family.id)
        permissions_data.append({
            "baby_id": baby.id,
            "baby_name": baby.name,
            "permissions": perms
        })

    return {
        "user_id": target_user_id,
        "username": target_fu.user.username,
        "permissions": permissions_data
    }
