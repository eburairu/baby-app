"""ユーザーモデル"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """ユーザーテーブル"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # リレーション
    feedings = relationship("Feeding", back_populates="user", cascade="all, delete-orphan")
    sleeps = relationship("Sleep", back_populates="user", cascade="all, delete-orphan")
    diapers = relationship("Diaper", back_populates="user", cascade="all, delete-orphan")
    growths = relationship("Growth", back_populates="user", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="user", cascade="all, delete-orphan")
    contractions = relationship("Contraction", back_populates="user", cascade="all, delete-orphan")
