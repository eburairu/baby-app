"""陣痛タイマールーター"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.utils.time import get_now_naive

from app.database import get_db
from app.utils.templates import templates
from app.dependencies import get_current_user, get_current_baby, check_record_permission
from app.models.user import User
from app.models.baby import Baby
from app.models.contraction import Contraction
from app.schemas.contraction import ContractionUpdate
from app.services.contraction_service import ContractionService

router = APIRouter(prefix="/contractions", tags=["contractions"])


@router.get("", response_class=HTMLResponse)
async def contraction_timer(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("contraction"))
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

    response = templates.TemplateResponse(
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

    # 選択された赤ちゃんIDをクッキーに保存
    response.set_cookie(
        key="selected_baby_id",
        value=str(baby.id),
        max_age=7 * 24 * 60 * 60,
        httponly=False,
        samesite="lax"
    )
    return response


@router.post("/start", response_class=HTMLResponse)
async def start_contraction(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("contraction"))
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
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("contraction"))
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
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("contraction"))
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


@router.get("/{contraction_id}/edit", response_class=HTMLResponse)
async def edit_contraction_form(
    request: Request,
    contraction_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("contraction"))
):
    """陣痛記録編集フォーム"""
    contraction = db.query(Contraction).filter(
        Contraction.id == contraction_id,
        Contraction.baby_id == baby.id
    ).first()

    if not contraction:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    return templates.TemplateResponse(
        "contraction/form.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "contraction": contraction
        }
    )


@router.post("/{contraction_id}", response_class=HTMLResponse)
async def update_contraction(
    request: Request,
    contraction_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    form_data: ContractionUpdate = Depends(ContractionUpdate.as_form),
    _ = Depends(check_record_permission("contraction"))
):
    """陣痛記録更新"""
    contraction = db.query(Contraction).filter(
        Contraction.id == contraction_id,
        Contraction.baby_id == baby.id
    ).first()

    if not contraction:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    # 更新データを適用
    update_data = form_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(contraction, key, value)

    # 持続時間を再計算
    if contraction.end_time:
        contraction.duration_seconds = ContractionService.calculate_duration(
            contraction.start_time,
            contraction.end_time
        )
    else:
        contraction.duration_seconds = None

    db.commit()
    
    # 全ての間隔を再計算（開始時間が前後する可能性があるため）
    # シンプルにするため、この赤ちゃんの全記録を取得して間隔を再設定
    all_contractions = db.query(Contraction).filter(
        Contraction.baby_id == baby.id
    ).order_by(Contraction.start_time.asc()).all()

    prev_end = None
    for c in all_contractions:
        if prev_end:
            c.interval_seconds = int((c.start_time - prev_end).total_seconds())
        else:
            c.interval_seconds = None
        prev_end = c.end_time

    db.commit()
    db.refresh(contraction)

    if request.headers.get("HX-Request"):
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

    return await contraction_timer(request, db, user, baby)


@router.delete("/{contraction_id}", response_class=HTMLResponse)
async def delete_contraction(
    contraction_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("contraction"))
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
