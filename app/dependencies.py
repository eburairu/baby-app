"""依存性注入モジュール"""
from typing import Optional
from fastapi import Cookie, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

# セッションストア（本番環境ではRedisなど外部ストア推奨）
sessions: dict[str, int] = {}


async def get_current_user(
    session_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> User:
    """現在のログインユーザーを取得"""
    if not session_token or session_token not in sessions:
        raise HTTPException(
            status_code=401,
            detail="認証が必要です"
        )

    user_id = sessions[session_token]
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        # セッションは存在するがユーザーが見つからない場合
        del sessions[session_token]
        raise HTTPException(
            status_code=401,
            detail="ユーザーが見つかりません"
        )

    return user


async def get_current_user_optional(
    session_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """現在のログインユーザーを取得（オプショナル）"""
    if not session_token or session_token not in sessions:
        return None

    user_id = sessions.get(session_token)
    if not user_id:
        return None

    return db.query(User).filter(User.id == user_id).first()
