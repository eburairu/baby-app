"""ダッシュボードルーター"""
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.utils.templates import templates
from app.dependencies import get_current_user, get_current_family, get_current_baby
from app.models.user import User
from app.models.family import Family
from app.models.baby import Baby
from app.services.statistics_service import StatisticsService
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


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
