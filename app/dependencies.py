"""依存性注入モジュール"""
import secrets
from datetime import datetime
from typing import Optional
from fastapi import Cookie, Depends, Request
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


def get_current_baby(
    family: Family = Depends(get_current_family),
    baby_id: Optional[int] = None,  # URLクエリやパラメータから
    db: Session = Depends(get_db)
) -> Baby:
    """現在操作対象の赤ちゃんを取得"""
    if not family.babies:
        raise PermissionDenied("赤ちゃんが登録されていません。")
    
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
