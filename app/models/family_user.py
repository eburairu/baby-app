"""家族メンバーモデル"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.utils.time import get_now_naive

from app.database import Base


class FamilyUser(Base):
    """家族とユーザーの中間テーブル"""
    __tablename__ = "family_users"

    family_id = Column(Integer, ForeignKey("families.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role = Column(String, nullable=False, default="member")  # admin, member
    joined_at = Column(DateTime, default=get_now_naive, nullable=False)

    # リレーション
    family = relationship("Family", back_populates="members")
    user = relationship("User", back_populates="families")
