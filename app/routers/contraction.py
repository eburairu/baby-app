"""陣痛タイマールーター"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.utils.time import get_now_naive

from app.database import get_db
from app.dependencies import get_current_user, get_current_baby
from app.models.user import User
from app.models.baby import Baby
from app.models.contraction import Contraction
from app.services.contraction_service import ContractionService

router = APIRouter(prefix="/contractions", tags=["contractions"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def contraction_timer(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby)
):
    """陣痛タイマーページ"""
    # 継続中の陣痛を取得
    ongoing_contraction = db.query(Contraction).filter(
        Contraction.baby_id == baby.id,
        Contraction.end_time == None
    ).first()

    # 陣痛記録一覧（最新20件）
    contractions = db.query(Contraction).filter(
        Contraction.baby_id == baby.id
    ).order_by(Contraction.start_time.desc()).limit(20).all()

    # 直近1時間の統計
    stats = ContractionService.get_statistics(db, baby.id, hours=1)

    return templates.TemplateResponse(
        "contraction/timer.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "ongoing_contraction": ongoing_contraction,
            "contractions": contractions,
            "stats": stats
        }
    )


@router.post("/start", response_class=HTMLResponse)
async def start_contraction(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby)
):
    """陣痛開始"""
    # 既に継続中の陣痛があるかチェック
    ongoing = db.query(Contraction).filter(
        Contraction.baby_id == baby.id,
        Contraction.end_time == None
    ).first()

    if ongoing:
        raise HTTPException(
            status_code=400,
            detail="既に陣痛が継続中です"
        )

    # 前回からの間隔を計算
    interval_seconds = ContractionService.calculate_interval(db, baby.id)

    # 新しい陣痛記録を作成
    new_contraction = Contraction(
        baby_id=baby.id,
        user_id=user.id,
        start_time=get_now_naive(),
        interval_seconds=interval_seconds
    )

    db.add(new_contraction)
    db.commit()
    db.refresh(new_contraction)

    # ページ全体を再レンダリング
    contractions = db.query(Contraction).filter(
        Contraction.baby_id == baby.id
    ).order_by(Contraction.start_time.desc()).limit(20).all()

    stats = ContractionService.get_statistics(db, baby.id, hours=1)

    return templates.TemplateResponse(
        "contraction/timer.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "ongoing_contraction": new_contraction,
            "contractions": contractions,
            "stats": stats
        }
    )


@router.post("/{contraction_id}/end", response_class=HTMLResponse)
async def end_contraction(
    request: Request,
    contraction_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby)
):
    """陣痛終了"""
    contraction = db.query(Contraction).filter(
        Contraction.id == contraction_id,
        Contraction.baby_id == baby.id
    ).first()

    if not contraction:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    if contraction.end_time:
        raise HTTPException(
            status_code=400,
            detail="この陣痛は既に終了しています"
        )

    # 終了時刻と持続時間を設定
    end_time = get_now_naive()
    contraction.end_time = end_time
    contraction.duration_seconds = ContractionService.calculate_duration(
        contraction.start_time,
        end_time
    )

    db.commit()
    db.refresh(contraction)

    # ページ全体を再レンダリング
    contractions = db.query(Contraction).filter(
        Contraction.baby_id == baby.id
    ).order_by(Contraction.start_time.desc()).limit(20).all()

    stats = ContractionService.get_statistics(db, baby.id, hours=1)

    return templates.TemplateResponse(
        "contraction/timer.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "ongoing_contraction": None,
            "contractions": contractions,
            "stats": stats
        }
    )


@router.get("/list", response_class=HTMLResponse)
async def contraction_list(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby)
):
    """陣痛記録一覧（htmx自動更新用）"""
    contractions = db.query(Contraction).filter(
        Contraction.baby_id == baby.id
    ).order_by(Contraction.start_time.desc()).limit(20).all()

    stats = ContractionService.get_statistics(db, baby.id, hours=1)

    return templates.TemplateResponse(
        "contraction/list.html",
        {
            "request": request,
            "baby": baby,
            "contractions": contractions,
            "stats": stats
        }
    )


@router.delete("/{contraction_id}", response_class=HTMLResponse)
async def delete_contraction(
    contraction_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby)
):
    """陣痛記録削除"""
    contraction = db.query(Contraction).filter(
        Contraction.id == contraction_id,
        Contraction.baby_id == baby.id
    ).first()

    if not contraction:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    db.delete(contraction)
    db.commit()

    return ""
