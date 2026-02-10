"""ダッシュボードルーター"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services.statistics_service import StatisticsService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """ダッシュボードページ"""
    # 統計データ取得
    feeding_stats = StatisticsService.get_feeding_stats(db, user.id)
    sleep_stats = StatisticsService.get_sleep_stats(db, user.id)
    diaper_stats = StatisticsService.get_diaper_stats(db, user.id)
    latest_growth = StatisticsService.get_latest_growth(db, user.id)
    recent_records = StatisticsService.get_recent_records(db, user.id)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "feeding_stats": feeding_stats,
            "sleep_stats": sleep_stats,
            "diaper_stats": diaper_stats,
            "latest_growth": latest_growth,
            "recent_records": recent_records
        }
    )


@router.get("/stats", response_class=HTMLResponse)
async def dashboard_stats(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """統計カード部分（htmx自動更新用）"""
    feeding_stats = StatisticsService.get_feeding_stats(db, user.id)
    sleep_stats = StatisticsService.get_sleep_stats(db, user.id)
    diaper_stats = StatisticsService.get_diaper_stats(db, user.id)
    latest_growth = StatisticsService.get_latest_growth(db, user.id)

    return templates.TemplateResponse(
        "components/stats_card.html",
        {
            "request": request,
            "feeding_stats": feeding_stats,
            "sleep_stats": sleep_stats,
            "diaper_stats": diaper_stats,
            "latest_growth": latest_growth
        }
    )
