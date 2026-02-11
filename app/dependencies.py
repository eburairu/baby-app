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


class AuthenticationRequired(Exception):
    """認証が必要な場合に発生する例外"""
    pass


async def get_current_user(
    request: Request,
    session_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> User:
    """現在のログインユーザーを取得（必須）

    未認証の場合は AuthenticationRequired を発生させる。
    main.py のエラーハンドラーでログインページへリダイレクトする。
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


async def get_current_user_optional(
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
