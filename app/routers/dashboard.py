"""ダッシュボードルーター"""
from fastapi import APIRouter, Depends, Request, Response, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional, Any
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user, get_current_family, get_current_baby
from app.models.user import User
from app.models.family import Family
from app.models.baby import Baby
from app.services.statistics_service import StatisticsService
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# ===== レスポンススキーマ =====

class BabyBasicInfo(BaseModel):
    """赤ちゃんの基本情報"""
    id: int
    name: str
    birthday: Optional[date] = None
    due_date: Optional[date] = None

    class Config:
        from_attributes = True


class PrenatalInfo(BaseModel):
    """プレママ期情報"""
    days_remaining: int
    weeks: int
    days: int


class DashboardDataResponse(BaseModel):
    """ダッシュボードデータレスポンス"""
    baby: Optional[BabyBasicInfo] = None
    feeding_stats: Optional[dict[str, Any]] = None
    sleep_stats: Optional[dict[str, Any]] = None
    diaper_stats: Optional[dict[str, Any]] = None
    latest_growth: Optional[dict[str, Any]] = None
    recent_records: Optional[dict[str, Any]] = None
    prenatal_info: Optional[PrenatalInfo] = None
    perms: dict[str, bool]

    class Config:
        from_attributes = True


# ===== JSON API エンドポイント =====

@router.get("/data", response_model=DashboardDataResponse)
def get_dashboard_data(
    request: Request,
    baby_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    family: Family = Depends(get_current_family)
):
    """
    ダッシュボードデータ取得（JSON専用）

    フロントエンド用のダッシュボードデータを返す
    """
    # JSONリクエストのみ対応
    if not wants_json(request):
        from fastapi import HTTPException
        raise HTTPException(status_code=406, detail="JSON only endpoint")

    # baby_idが指定されていない場合は、get_current_babyを使用
    if baby_id is None:
        baby = get_current_baby(request, db, user, family)
    else:
        # 指定されたbaby_idが家族に属しているか確認
        baby = db.query(Baby).filter(
            Baby.id == baby_id,
            Baby.family_id == family.id
        ).first()
        if not baby:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Baby not found")

    # 現在の赤ちゃんの権限を取得
    perms = PermissionService.get_user_permissions(db, user.id, baby.id, family.id)

    # 権限がある項目のみ統計を取得
    feeding_stats = StatisticsService.get_feeding_stats(db, baby.id) if perms['feeding'] else None
    sleep_stats = StatisticsService.get_sleep_stats(db, baby.id) if perms['sleep'] else None
    diaper_stats = StatisticsService.get_diaper_stats(db, baby.id) if perms['diaper'] else None
    latest_growth = StatisticsService.get_latest_growth(db, baby.id) if perms['growth'] else None

    # 最新記録を権限に基づいて選択的に取得
    recent_records = None
    if perms['feeding'] or perms['sleep'] or perms['diaper']:
        recent_records = StatisticsService.get_recent_records_selective(
            db, baby.id,
            include_feeding=perms['feeding'],
            include_sleep=perms['sleep'],
            include_diaper=perms['diaper']
        )

    # プレママ期情報
    prenatal_info = None
    if baby and not baby.birthday and baby.due_date and perms['basic_info']:
        today = date.today()
        days_remaining = (baby.due_date - today).days

        # 妊娠期間計算 (通常280日 = 40週)
        elapsed_days = 280 - days_remaining
        current_week = elapsed_days // 7
        current_day = elapsed_days % 7

        prenatal_info = PrenatalInfo(
            days_remaining=days_remaining,
            weeks=current_week,
            days=current_day
        )

    return DashboardDataResponse(
        baby=BabyBasicInfo.model_validate(baby) if baby else None,
        feeding_stats=feeding_stats,
        sleep_stats=sleep_stats,
        diaper_stats=diaper_stats,
        latest_growth=latest_growth,
        recent_records=recent_records,
        prenatal_info=prenatal_info,
        perms=perms
    )


# ===== HTML エンドポイント =====

@router.get("", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    family: Family = Depends(get_current_family),
    baby: Baby = Depends(get_current_baby)
):
    """ダッシュボードページ"""
    # 閲覧可能な赤ちゃんのみに絞り込む（バッチ取得で最適化）
    baby_ids = [b.id for b in family.babies]
    perms_map = PermissionService.get_user_permissions_batch(
        db, user.id, baby_ids, family.id, "basic_info"
    )
    visible_babies = [b for b in family.babies if perms_map.get(b.id, False)]
    
    # 現在の赤ちゃんの権限を取得
    perms = PermissionService.get_user_permissions(db, user.id, baby.id, family.id)
    
    # 権限がある項目のみ統計を取得
    feeding_stats = StatisticsService.get_feeding_stats(db, baby.id) if perms['feeding'] else None
    sleep_stats = StatisticsService.get_sleep_stats(db, baby.id) if perms['sleep'] else None
    diaper_stats = StatisticsService.get_diaper_stats(db, baby.id) if perms['diaper'] else None
    latest_growth = StatisticsService.get_latest_growth(db, baby.id) if perms['growth'] else None
    
    # 最新記録を権限に基づいて選択的に取得（パフォーマンス最適化）
    recent_records = None
    if perms['feeding'] or perms['sleep'] or perms['diaper']:
        recent_records = StatisticsService.get_recent_records_selective(
            db, baby.id,
            include_feeding=perms['feeding'],
            include_sleep=perms['sleep'],
            include_diaper=perms['diaper']
        )

    # プレママ期情報
    prenatal_info = None
    if baby and not baby.birthday and baby.due_date and perms['basic_info']:
        today = date.today()
        days_remaining = (baby.due_date - today).days
        
        # 妊娠期間計算 (通常280日 = 40週)
        elapsed_days = 280 - days_remaining
        current_week = elapsed_days // 7
        current_day = elapsed_days % 7
        
        prenatal_info = {
            "days_remaining": days_remaining,
            "weeks": current_week,
            "days": current_day
        }

    response = templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "family": family,
            "baby": baby,
            "all_babies": visible_babies,
            "viewable_babies": visible_babies,  # グローバルナビゲーション用
            "current_baby": baby,  # グローバルナビゲーション用
            "feeding_stats": feeding_stats,
            "sleep_stats": sleep_stats,
            "diaper_stats": diaper_stats,
            "latest_growth": latest_growth,
            "recent_records": recent_records,
            "prenatal_info": prenatal_info,
            "perms": perms
        }
    )
    # 選択された赤ちゃんIDをクッキーに保存（7日間有効）
    response.set_cookie(
        key="selected_baby_id",
        value=str(baby.id),
        max_age=7 * 24 * 60 * 60,  # 7日間
        httponly=False,  # JavaScriptからもアクセス可能
        samesite="lax"
    )
    return response


@router.get("/stats", response_class=HTMLResponse)
def dashboard_stats(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    family: Family = Depends(get_current_family),
    baby: Baby = Depends(get_current_baby)
):
    """統計カード部分（htmx自動更新用）"""
    perms = PermissionService.get_user_permissions(db, user.id, baby.id, family.id)
    
    feeding_stats = StatisticsService.get_feeding_stats(db, baby.id) if perms['feeding'] else None
    sleep_stats = StatisticsService.get_sleep_stats(db, baby.id) if perms['sleep'] else None
    diaper_stats = StatisticsService.get_diaper_stats(db, baby.id) if perms['diaper'] else None
    latest_growth = StatisticsService.get_latest_growth(db, baby.id) if perms['growth'] else None

    return templates.TemplateResponse(
        "components/stats_card.html",
        {
            "request": request,
            "baby": baby,
            "feeding_stats": feeding_stats,
            "sleep_stats": sleep_stats,
            "diaper_stats": diaper_stats,
            "latest_growth": latest_growth,
            "perms": perms
        }
    )
