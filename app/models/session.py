"""セッションモデル"""
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

# セッション有効期限: 7日間
SESSION_MAX_AGE_DAYS = 7


class UserSession(Base):
    """セッションテーブル（DBベース永続化）"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    # リレーション
    user = relationship("User", backref="sessions")

    @property
    def is_expired(self) -> bool:
        """セッションが期限切れかチェック"""
        return datetime.utcnow() > self.expires_at

    @staticmethod
    def default_expires_at() -> datetime:
        """デフォルトの有効期限を返す"""
        return datetime.utcnow() + timedelta(days=SESSION_MAX_AGE_DAYS)
