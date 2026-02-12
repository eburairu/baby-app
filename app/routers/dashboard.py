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
    # 統計データ取得 (baby.id を使用)
    feeding_stats = StatisticsService.get_feeding_stats(db, baby.id)
    sleep_stats = StatisticsService.get_sleep_stats(db, baby.id)
    diaper_stats = StatisticsService.get_diaper_stats(db, baby.id)
    latest_growth = StatisticsService.get_latest_growth(db, baby.id)
    recent_records = StatisticsService.get_recent_records(db, baby.id)

    # プレママ期情報
    prenatal_info = None
    if baby and not baby.birthday and baby.due_date:
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
            "all_babies": family.babies,
            "feeding_stats": feeding_stats,
            "sleep_stats": sleep_stats,
            "diaper_stats": diaper_stats,
            "latest_growth": latest_growth,
            "recent_records": recent_records,
            "prenatal_info": prenatal_info
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
    baby: Baby = Depends(get_current_baby)
):
    """統計カード部分（htmx自動更新用）"""
    feeding_stats = StatisticsService.get_feeding_stats(db, baby.id)
    sleep_stats = StatisticsService.get_sleep_stats(db, baby.id)
    diaper_stats = StatisticsService.get_diaper_stats(db, baby.id)
    latest_growth = StatisticsService.get_latest_growth(db, baby.id)

    return templates.TemplateResponse(
        "components/stats_card.html",
        {
            "request": request,
            "baby": baby,
            "feeding_stats": feeding_stats,
            "sleep_stats": sleep_stats,
            "diaper_stats": diaper_stats,
            "latest_growth": latest_growth
        }
    )
