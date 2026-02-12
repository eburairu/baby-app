"""家族管理ルーター"""
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

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


# ===== JSON API エンドポイント =====

@router.get("/me", response_model=FamilyResponse)
async def get_my_family(
    request: Request,
    family: Family = Depends(get_current_family)
):
    """
    現在の家族情報を取得（JSON対応）

    フロントエンド用
    """
    # JSONリクエストのみ対応
    if not wants_json(request):
        raise HTTPException(status_code=406, detail="JSON only endpoint")

    return FamilyResponse.model_validate(family)


# ===== HTML エンドポイント =====

@router.get("/setup", response_class=HTMLResponse)
async def family_setup_page(
    request: Request,
    user: User = Depends(get_current_user)
):
    """家族の作成または参加を選択するページ"""
    if user.families:
        return RedirectResponse(url="/dashboard", status_code=303)
    
    return templates.TemplateResponse(
        "family/setup.html",
        {"request": request, "user": user}
    )


@router.post("/create")
async def create_family(
    name: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """家族を新規作成"""
    FamilyService.create_family(db, user, name)
    return RedirectResponse(url="/dashboard", status_code=303)


@router.post("/join")
async def join_family(
    request: Request,
    invite_code: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """招待コードで家族に参加"""
    family = FamilyService.join_family(db, user, invite_code.upper())
    if not family:
        # エラー表示（簡易的にクエリパラメータで）
        return RedirectResponse(url="/families/setup?error=invalid_code", status_code=303)
    
    return RedirectResponse(url="/dashboard", status_code=303)


@router.get("/settings", response_class=HTMLResponse)
async def family_settings(
    request: Request,
    user: User = Depends(get_current_user),
    family = Depends(get_current_family),
    db: Session = Depends(get_db)
):
    """家族設定画面（招待コードの確認など）"""
    is_admin = FamilyService.is_admin(db, user.id, family.id)
    
    # 閲覧可能な赤ちゃんのみを抽出
    if is_admin:
        display_babies = family.babies
    else:
        display_babies = [
            b for b in family.babies 
            if PermissionService.can_view_baby_record(db, user.id, family.id, b.id, "basic_info")
        ]

    return templates.TemplateResponse(
        "family/settings.html",
        {
            "request": request,
            "user": user,
            "family": family,
            "is_admin": is_admin,
            "babies": display_babies,
            "members": family.members
        }
    )


@router.get("/members/{target_user_id}/permissions", response_class=HTMLResponse)
async def member_permissions_page(
    request: Request,
    target_user_id: int,
    user: User = Depends(get_current_user),
    family = Depends(get_current_family),
    db: Session = Depends(get_db)
):
    """メンバーの権限設定ページ"""
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
        perms = PermissionService.get_user_permissions(db, target_user_id, baby.id)
        permissions_data.append({
            "baby": baby,
            "permissions": perms
        })

    return templates.TemplateResponse(
        "family/member_permissions.html",
        {
            "request": request,
            "user": user,
            "family": family,
            "target_user": target_fu.user,
            "permissions_data": permissions_data,
            "record_types": {
                "basic_info": "基本情報・表示",
                "feeding": "授乳",
                "sleep": "睡眠",
                "diaper": "おむつ",
                "growth": "成長記録",
                "schedule": "スケジュール",
                "contraction": "陣痛タイマー"
            }
        }
    )


@router.post("/members/{target_user_id}/permissions")
async def update_member_permissions(
    target_user_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    family = Depends(get_current_family),
    db: Session = Depends(get_db)
):
    """メンバーの権限設定を更新"""
    # 管理者チェック
    if not FamilyService.is_admin(db, user.id, family.id):
        raise HTTPException(status_code=403, detail="管理者権限が必要です")

    form_data = await request.form()
    
    # フォームデータから権限を解析
    # キー形式: perm_{baby_id}_{record_type}
    updates = {} # baby_id -> {record_type -> bool}
    
    # まず全赤ちゃん・全タイプのデフォルトをFalseに設定（チェック外れた場合のため）
    for baby in family.babies:
        updates[baby.id] = {
            "feeding": False, "sleep": False, "diaper": False, 
            "growth": False, "schedule": False, "contraction": False, "basic_info": False
        }
        
    for key, _ in form_data.items():
        if key.startswith("perm_"):
            parts = key.split("_", 2)
            if len(parts) == 3:
                try:
                    b_id = int(parts[1])
                    r_type = parts[2]
                    if b_id in updates:
                        updates[b_id][r_type] = True
                except ValueError:
                    continue

    # 更新実行
    for b_id, perms in updates.items():
        PermissionService.update_permissions(db, target_user_id, b_id, perms)

    return RedirectResponse(url="/families/settings", status_code=303)
