"""睡眠記録ルーター"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.utils.time import get_now_naive

from app.database import get_db
from app.dependencies import get_current_user, get_current_baby, get_current_family, check_record_permission
from app.models.user import User
from app.models.baby import Baby
from app.models.family import Family
from app.models.sleep import Sleep
from app.schemas.sleep import SleepCreate, SleepUpdate, SleepResponse
from app.schemas.responses import ListResponse, BabyBasicInfo
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/sleeps", tags=["sleeps"])


@router.get("", response_model=None)
async def list_sleeps(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    family: Family = Depends(get_current_family),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠記録一覧ページ（HTML/JSON Content Negotiation）"""
    sleeps = db.query(Sleep).filter(
        Sleep.baby_id == baby.id
    ).order_by(Sleep.start_time.desc()).limit(50).all()

    # 継続中の睡眠を取得
    ongoing_sleep = db.query(Sleep).filter(
        Sleep.baby_id == baby.id,
        Sleep.end_time == None
    ).first()

    # 閲覧可能な赤ちゃんリストを取得（グローバルナビゲーション用）
    baby_ids = [b.id for b in family.babies]
    perms_map = PermissionService.get_user_permissions_batch(
        db, user.id, baby_ids, family.id, "basic_info"
    )
    viewable_babies = [b for b in family.babies if perms_map.get(b.id, False)]

    # JSONリクエストの場合
    if wants_json(request):
        return {
            "items": [SleepResponse.model_validate(s) for s in sleeps],
            "baby": BabyBasicInfo.model_validate(baby) if baby else None,
            "viewable_babies": [BabyBasicInfo.model_validate(b) for b in viewable_babies],
            "ongoing_sleep": SleepResponse.model_validate(ongoing_sleep) if ongoing_sleep else None,
        }

    # HTMLリクエストの場合
    response = templates.TemplateResponse(
        "sleep/list.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "sleeps": sleeps,
            "ongoing_sleep": ongoing_sleep,
            "viewable_babies": viewable_babies,
            "current_baby": baby
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


@router.get("/new", response_class=HTMLResponse)
async def new_sleep_form(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    family: Family = Depends(get_current_family),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("sleep"))
):
    """新規睡眠記録フォーム"""
    # 閲覧可能な赤ちゃんリストを取得（グローバルナビゲーション用）
    baby_ids = [b.id for b in family.babies]
    perms_map = PermissionService.get_user_permissions_batch(
        db, user.id, baby_ids, family.id, "basic_info"
    )
    viewable_babies = [b for b in family.babies if perms_map.get(b.id, False)]

    return templates.TemplateResponse(
        "sleep/form.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "sleep": None,
            "viewable_babies": viewable_babies,
            "current_baby": baby
        }
    )


@router.post("/start", response_model=None)
async def start_sleep(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠開始（HTML/JSON Content Negotiation）"""
    # 既に継続中の睡眠があるかチェック
    ongoing_sleep = db.query(Sleep).filter(
        Sleep.baby_id == baby.id,
        Sleep.end_time == None
    ).first()

    if ongoing_sleep:
        raise HTTPException(
            status_code=400,
            detail="既に睡眠が継続中です"
        )

    # 新しい睡眠記録を作成
    new_sleep = Sleep(
        baby_id=baby.id,
        user_id=user.id,
        start_time=get_now_naive()
    )

    db.add(new_sleep)
    db.commit()
    db.refresh(new_sleep)

    # JSONリクエストの場合
    if wants_json(request):
        return SleepResponse.model_validate(new_sleep)

    # HTMLリクエストの場合 - 一覧ページの内容を返す
    sleeps = db.query(Sleep).filter(
        Sleep.baby_id == baby.id
    ).order_by(Sleep.start_time.desc()).limit(50).all()

    return templates.TemplateResponse(
        "sleep/list.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "sleeps": sleeps,
            "ongoing_sleep": new_sleep
        }
    )


@router.post("/{sleep_id}/end", response_model=None)
async def end_sleep(
    request: Request,
    sleep_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠終了（HTML/JSON Content Negotiation）"""
    sleep = db.query(Sleep).filter(
        Sleep.id == sleep_id,
        Sleep.baby_id == baby.id
    ).first()

    if not sleep:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    if sleep.end_time:
        raise HTTPException(
            status_code=400,
            detail="この睡眠は既に終了しています"
        )

    sleep.end_time = get_now_naive()
    db.commit()
    db.refresh(sleep)

    # JSONリクエストの場合
    if wants_json(request):
        return SleepResponse.model_validate(sleep)

    # HTMLリクエストの場合 - 一覧ページの内容を返す
    sleeps = db.query(Sleep).filter(
        Sleep.baby_id == baby.id
    ).order_by(Sleep.start_time.desc()).limit(50).all()

    return templates.TemplateResponse(
        "sleep/list.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "sleeps": sleeps,
            "ongoing_sleep": None
        }
    )


@router.post("", response_model=None)
async def create_sleep(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠記録作成（手動入力・HTML/JSON Content Negotiation）"""
    # JSONリクエストの場合
    if wants_json(request):
        body = await request.json()
        form_data = SleepCreate(**body)
    else:
        # HTMLフォームの場合
        form = await request.form()
        form_data = SleepCreate(
            start_time=datetime.fromisoformat(form.get("start_time")),
            end_time=datetime.fromisoformat(form.get("end_time")) if form.get("end_time") else None,
            notes=form.get("notes") or None
        )

    new_sleep = Sleep(
        baby_id=baby.id,
        user_id=user.id,
        **form_data.model_dump()
    )

    db.add(new_sleep)
    db.commit()
    db.refresh(new_sleep)

    # JSONリクエストの場合
    if wants_json(request):
        return SleepResponse.model_validate(new_sleep)

    # htmxリクエストの場合
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "sleep/item.html",
            {"request": request, "sleep": new_sleep}
        )

    # 通常のHTMLリクエストの場合
    sleeps = db.query(Sleep).filter(
        Sleep.baby_id == baby.id
    ).order_by(Sleep.start_time.desc()).limit(50).all()

    ongoing_sleep = db.query(Sleep).filter(
        Sleep.baby_id == baby.id,
        Sleep.end_time == None
    ).first()

    return templates.TemplateResponse(
        "sleep/list.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "sleeps": sleeps,
            "ongoing_sleep": ongoing_sleep
        }
    )


@router.get("/{sleep_id}", response_model=SleepResponse)
async def get_sleep(
    sleep_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠記録詳細取得（JSON専用）"""
    if not wants_json(request):
        raise HTTPException(status_code=406, detail="JSON only endpoint")

    sleep = db.query(Sleep).filter(
        Sleep.id == sleep_id,
        Sleep.baby_id == baby.id
    ).first()

    if not sleep:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    return SleepResponse.model_validate(sleep)


@router.get("/{sleep_id}/edit", response_class=HTMLResponse)
async def edit_sleep_form(
    request: Request,
    sleep_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠記録編集フォーム"""
    sleep = db.query(Sleep).filter(
        Sleep.id == sleep_id,
        Sleep.baby_id == baby.id
    ).first()

    if not sleep:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    return templates.TemplateResponse(
        "sleep/form.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "sleep": sleep
        }
    )


@router.post("/{sleep_id}", response_class=HTMLResponse)
async def update_sleep(
    request: Request,
    sleep_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    form_data: SleepUpdate = Depends(SleepUpdate.as_form),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠記録更新"""
    sleep = db.query(Sleep).filter(
        Sleep.id == sleep_id,
        Sleep.baby_id == baby.id
    ).first()

    if not sleep:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    # 更新データを適用
    update_data = form_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(sleep, key, value)

    db.commit()
    db.refresh(sleep)

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "sleep/item.html",
            {"request": request, "sleep": sleep}
        )

    sleeps = db.query(Sleep).filter(
        Sleep.baby_id == baby.id
    ).order_by(Sleep.start_time.desc()).limit(50).all()

    ongoing_sleep = db.query(Sleep).filter(
        Sleep.baby_id == baby.id,
        Sleep.end_time == None
    ).first()

    return templates.TemplateResponse(
        "sleep/list.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "sleeps": sleeps,
            "ongoing_sleep": ongoing_sleep
        }
    )


@router.put("/{sleep_id}", response_model=SleepResponse)
async def update_sleep_json(
    sleep_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠記録更新（JSON専用）"""
    if not wants_json(request):
        raise HTTPException(status_code=406, detail="JSON only endpoint")

    sleep = db.query(Sleep).filter(
        Sleep.id == sleep_id,
        Sleep.baby_id == baby.id
    ).first()

    if not sleep:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    # リクエストボディをパース
    body = await request.json()
    update_data = SleepUpdate(**body)

    # 更新データを適用
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(sleep, key, value)

    db.commit()
    db.refresh(sleep)

    return SleepResponse.model_validate(sleep)


@router.delete("/{sleep_id}", response_model=None)
async def delete_sleep(
    sleep_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("sleep"))
):
    """睡眠記録削除（HTML/JSON Content Negotiation）"""
    sleep = db.query(Sleep).filter(
        Sleep.id == sleep_id,
        Sleep.baby_id == baby.id
    ).first()

    if not sleep:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    db.delete(sleep)
    db.commit()

    # JSONリクエストの場合
    if wants_json(request):
        return {"success": True, "message": "削除しました"}

    # HTMLリクエストの場合（htmx用）
    return ""
