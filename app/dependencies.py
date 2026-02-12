"""依存性注入モジュール"""
import secrets
from datetime import datetime
from typing import Optional
from fastapi import Cookie, Depends, Request, Response, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.session import UserSession


from app.models.family import Family
from app.models.family_user import FamilyUser
from app.models.baby import Baby


class AuthenticationRequired(Exception):
    """認証が必要な場合に発生する例外"""
    pass


class PermissionDenied(Exception):
    """権限が不足している場合に発生する例外"""
    pass


def get_current_user(
    request: Request,
    session_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> User:
    """現在のログインユーザーを取得（必須）

    未認証の場合は AuthenticationRequired を発生させる。
    """
    if not session_token:
        raise AuthenticationRequired()

    # DBからセッション検索
    user_session = db.query(UserSession).filter(
        UserSession.token == session_token
    ).first()

    if not user_session:
        raise AuthenticationRequired()

    # 有効期限チェック
    if user_session.is_expired:
        db.delete(user_session)
        db.commit()
        raise AuthenticationRequired()

    # ユーザー取得
    user = db.query(User).filter(User.id == user_session.user_id).first()
    if not user:
        db.delete(user_session)
        db.commit()
        raise AuthenticationRequired()

    return user


def get_current_family(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Family:
    """現在ユーザーが所属している最初の家族を取得（単一家族前提）
    
    複数家族に対応する場合は、セッションやクッキーで active_family_id を管理する。
    """
    if not user.families:
        # どの家族にも属していない場合
        raise PermissionDenied("家族に所属していません。作成または参加してください。")
    return user.families[0].family


async def get_current_baby(
    request: Request,
    family: Family = Depends(get_current_family),
    baby_id: Optional[int] = Query(None),  # URLクエリパラメータ
    selected_baby_id: Optional[str] = Cookie(None),  # クッキーから選択中の赤ちゃんID
    db: Session = Depends(get_db)
) -> Baby:
    """現在操作対象の赤ちゃんを取得

    優先順位:
    1. URLクエリパラメータの baby_id
    2. POSTフォームデータの baby_id
    3. クッキーの selected_baby_id
    4. 家族の最初の赤ちゃん（デフォルト）
    """
    if not family.babies:
        raise PermissionDenied("赤ちゃんが登録されていません。")

    # まずURLクエリパラメータから取得
    if not baby_id:
        # POSTリクエストの場合、フォームデータから取得を試みる
        if request.method == "POST":
            try:
                form = await request.form()
                baby_id_str = form.get("baby_id")
                if baby_id_str:
                    baby_id = int(baby_id_str)
            except Exception:
                pass

        # クエリパラメータもフォームデータもない場合、クッキーから取得
        if not baby_id and selected_baby_id:
            try:
                baby_id = int(selected_baby_id)
            except (ValueError, TypeError):
                pass

    if baby_id:
        baby = db.query(Baby).filter(Baby.id == baby_id, Baby.family_id == family.id).first()
        if not baby:
            raise PermissionDenied("指定された赤ちゃんが見つかりません。")
        return baby

    # 指定がない場合は最初の赤ちゃんを返す
    return family.babies[0]


def admin_required(
    user: User = Depends(get_current_user),
    family: Family = Depends(get_current_family),
    db: Session = Depends(get_db)
):
    """家族の管理者権限を要求する"""
    fu = db.query(FamilyUser).filter(
        FamilyUser.family_id == family.id,
        FamilyUser.user_id == user.id
    ).first()
    if not fu or fu.role != "admin":
        raise PermissionDenied("管理者権限が必要です。")
    return fu


def get_current_user_optional(
    session_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """現在のログインユーザーを取得（オプショナル）"""
    if not session_token:
        return None

    user_session = db.query(UserSession).filter(
        UserSession.token == session_token
    ).first()

    if not user_session or user_session.is_expired:
        return None

    return db.query(User).filter(User.id == user_session.user_id).first()


async def check_csrf(request: Request):
    """CSRF対策の共通依存関係"""
    csrf_token = getattr(request.state, "csrf_token", None)
    if not csrf_token:
        # Fallback if middleware is missing or cookie not set
        csrf_token = request.cookies.get("csrf_token")
        if not csrf_token:
             # Generate new token if missing
            csrf_token = secrets.token_urlsafe(32)
            request.state.csrf_token = csrf_token

    if request.method in ("POST", "PUT", "DELETE", "PATCH"):
        header_token = request.headers.get("X-CSRF-Token")
        form_token = None

        # Check form data if header is missing
        content_type = request.headers.get("content-type", "")
        if not header_token and (
            content_type.startswith("multipart/form-data") or
            content_type.startswith("application/x-www-form-urlencoded")
        ):
            try:
                # Using await request.form() inside dependency is safe as it uses cached data
                form = await request.form()
                form_token = form.get("csrf_token")
            except Exception:
                pass

        submitted_token = header_token or form_token

        if not submitted_token or not secrets.compare_digest(submitted_token, csrf_token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing or incorrect"
            )
