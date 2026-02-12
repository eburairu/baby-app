"""おむつ交換記録ルーター"""
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
from app.models.diaper import Diaper, DiaperType
from app.schemas.diaper import DiaperCreate, DiaperUpdate, DiaperResponse
from app.schemas.responses import ListResponse, BabyBasicInfo
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/diapers", tags=["diapers"])


@router.get("", response_model=None)
async def list_diapers(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    family: Family = Depends(get_current_family),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("diaper"))
):
    """おむつ交換記録一覧ページ（HTML/JSON Content Negotiation）"""
    diapers = db.query(Diaper).filter(
        Diaper.baby_id == baby.id
    ).order_by(Diaper.change_time.desc()).limit(50).all()

    # 閲覧可能な赤ちゃんリストを取得（グローバルナビゲーション用）
    baby_ids = [b.id for b in family.babies]
    perms_map = PermissionService.get_user_permissions_batch(
        db, user.id, baby_ids, family.id, "basic_info"
    )
    viewable_babies = [b for b in family.babies if perms_map.get(b.id, False)]

    # JSONリクエストの場合
    if wants_json(request):
        return ListResponse(
            items=[DiaperResponse.model_validate(d) for d in diapers],
            baby=BabyBasicInfo.model_validate(baby),
            viewable_babies=[BabyBasicInfo.model_validate(b) for b in viewable_babies]
        )

    # HTMLリクエストの場合
    response = templates.TemplateResponse(
        "diaper/list.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "diapers": diapers,
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


@router.post("/quick", response_model=None)
async def quick_diaper(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("diaper"))
):
    """ワンタップでおむつ交換記録（HTML/JSON Content Negotiation）"""
    # JSONリクエストの場合
    if wants_json(request):
        body = await request.json()
        diaper_type = body.get("diaper_type")
    else:
        # HTMLフォームの場合
        form = await request.form()
        diaper_type = form.get("diaper_type")

    new_diaper = Diaper(
        baby_id=baby.id,
        user_id=user.id,
        change_time=get_now_naive(),
        diaper_type=DiaperType(diaper_type)
    )

    db.add(new_diaper)
    db.commit()
    db.refresh(new_diaper)

    # JSONリクエストの場合
    if wants_json(request):
        return DiaperResponse.model_validate(new_diaper)

    # htmxリクエストの場合
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "diaper/item.html",
            {"request": request, "diaper": new_diaper}
        )

    # 通常のHTMLリクエストの場合
    diapers = db.query(Diaper).filter(
        Diaper.baby_id == baby.id
    ).order_by(Diaper.change_time.desc()).limit(50).all()

    return templates.TemplateResponse(
        "diaper/list.html",
        {"request": request, "user": user, "baby": baby, "diapers": diapers}
    )


@router.get("/new", response_class=HTMLResponse)
async def new_diaper_form(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    family: Family = Depends(get_current_family),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("diaper"))
):
    """新規おむつ交換記録フォーム"""
    # 閲覧可能な赤ちゃんリストを取得（グローバルナビゲーション用）
    baby_ids = [b.id for b in family.babies]
    perms_map = PermissionService.get_user_permissions_batch(
        db, user.id, baby_ids, family.id, "basic_info"
    )
    viewable_babies = [b for b in family.babies if perms_map.get(b.id, False)]

    return templates.TemplateResponse(
        "diaper/form.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "diaper": None,
            "diaper_types": DiaperType,
            "viewable_babies": viewable_babies,
            "current_baby": baby
        }
    )


@router.post("", response_model=None)
async def create_diaper(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("diaper"))
):
    """おむつ交換記録作成（HTML/JSON Content Negotiation）"""
    # JSONリクエストの場合
    if wants_json(request):
        body = await request.json()
        form_data = DiaperCreate(**body)
    else:
        # HTMLフォームの場合
        form = await request.form()
        form_data = DiaperCreate(
            change_time=datetime.fromisoformat(form.get("change_time")),
            diaper_type=DiaperType(form.get("diaper_type")),
            notes=form.get("notes") or None
        )

    new_diaper = Diaper(
        baby_id=baby.id,
        user_id=user.id,
        **form_data.model_dump()
    )

    db.add(new_diaper)
    db.commit()
    db.refresh(new_diaper)

    # JSONリクエストの場合
    if wants_json(request):
        return DiaperResponse.model_validate(new_diaper)

    # htmxリクエストの場合
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "diaper/item.html",
            {"request": request, "diaper": new_diaper}
        )

    # 通常のHTMLリクエストの場合
    diapers = db.query(Diaper).filter(
        Diaper.baby_id == baby.id
    ).order_by(Diaper.change_time.desc()).limit(50).all()

    return templates.TemplateResponse(
        "diaper/list.html",
        {"request": request, "user": user, "baby": baby, "diapers": diapers}
    )


@router.get("/{diaper_id}", response_model=DiaperResponse)
async def get_diaper(
    diaper_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("diaper"))
):
    """おむつ交換記録詳細取得（JSON専用）"""
    if not wants_json(request):
        raise HTTPException(status_code=406, detail="JSON only endpoint")

    diaper = db.query(Diaper).filter(
        Diaper.id == diaper_id,
        Diaper.baby_id == baby.id
    ).first()

    if not diaper:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    return DiaperResponse.model_validate(diaper)


@router.get("/{diaper_id}/edit", response_class=HTMLResponse)
async def edit_diaper_form(
    request: Request,
    diaper_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("diaper"))
):
    """おむつ交換記録編集フォーム"""
    diaper = db.query(Diaper).filter(
        Diaper.id == diaper_id,
        Diaper.baby_id == baby.id
    ).first()

    if not diaper:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    return templates.TemplateResponse(
        "diaper/form.html",
        {
            "request": request,
            "user": user,
            "baby": baby,
            "diaper": diaper,
            "diaper_types": DiaperType
        }
    )


@router.post("/{diaper_id}", response_class=HTMLResponse)
async def update_diaper(
    request: Request,
    diaper_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    form_data: DiaperUpdate = Depends(DiaperUpdate.as_form),
    _ = Depends(check_record_permission("diaper"))
):
    """おむつ交換記録更新"""
    diaper = db.query(Diaper).filter(
        Diaper.id == diaper_id,
        Diaper.baby_id == baby.id
    ).first()

    if not diaper:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    # 更新データを適用
    update_data = form_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(diaper, key, value)

    db.commit()
    db.refresh(diaper)

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "diaper/item.html",
            {"request": request, "diaper": diaper}
        )

    diapers = db.query(Diaper).filter(
        Diaper.baby_id == baby.id
    ).order_by(Diaper.change_time.desc()).limit(50).all()

    return templates.TemplateResponse(
        "diaper/list.html",
        {"request": request, "user": user, "baby": baby, "diapers": diapers}
    )


@router.put("/{diaper_id}", response_model=DiaperResponse)
async def update_diaper_json(
    diaper_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("diaper"))
):
    """おむつ交換記録更新（JSON専用）"""
    if not wants_json(request):
        raise HTTPException(status_code=406, detail="JSON only endpoint")

    diaper = db.query(Diaper).filter(
        Diaper.id == diaper_id,
        Diaper.baby_id == baby.id
    ).first()

    if not diaper:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    # リクエストボディをパース
    body = await request.json()
    update_data = DiaperUpdate(**body)

    # 更新データを適用
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(diaper, key, value)

    db.commit()
    db.refresh(diaper)

    return DiaperResponse.model_validate(diaper)


@router.delete("/{diaper_id}", response_model=None)
async def delete_diaper(
    diaper_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    baby: Baby = Depends(get_current_baby),
    _ = Depends(check_record_permission("diaper"))
):
    """おむつ交換記録削除（HTML/JSON Content Negotiation）"""
    diaper = db.query(Diaper).filter(
        Diaper.id == diaper_id,
        Diaper.baby_id == baby.id
    ).first()

    if not diaper:
        raise HTTPException(status_code=404, detail="記録が見つかりません")

    db.delete(diaper)
    db.commit()

    # JSONリクエストの場合
    if wants_json(request):
        return {"success": True, "message": "削除しました"}

    # HTMLリクエストの場合（htmx用）
    return ""
