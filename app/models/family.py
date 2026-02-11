"""家族モデル"""
from datetime import datetime
import secrets
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Family(Base):
    """家族テーブル"""
    __tablename__ = "families"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    invite_code = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # リレーション
    members = relationship("FamilyUser", back_populates="family", cascade="all, delete-orphan")
    babies = relationship("Baby", back_populates="family", cascade="all, delete-orphan")

    @staticmethod
    def generate_invite_code():
        """招待コードを生成（8文字のランダム文字列）"""
        return secrets.token_hex(4).upper()
