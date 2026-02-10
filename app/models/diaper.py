"""おむつ交換記録モデル"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class DiaperType(str, enum.Enum):
    """おむつタイプ"""
    WET = "wet"      # おしっこ
    DIRTY = "dirty"  # うんち
    BOTH = "both"    # 両方


class Diaper(Base):
    """おむつ交換記録テーブル"""
    __tablename__ = "diapers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    change_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    diaper_type = Column(SQLEnum(DiaperType), nullable=False)
    notes = Column(String, nullable=True)

    # リレーション
    user = relationship("User", back_populates="diapers")
