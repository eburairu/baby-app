"""授乳記録モデル"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.utils.time import get_now_naive

from app.database import Base


class FeedingType(str, enum.Enum):
    """授乳タイプ"""
    BREAST = "breast"  # 母乳
    BOTTLE = "bottle"  # ミルク
    MIXED = "mixed"    # 混合


class Feeding(Base):
    """授乳記録テーブル"""
    __tablename__ = "feedings"

    id = Column(Integer, primary_key=True, index=True)
    baby_id = Column(Integer, ForeignKey("babies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 記録者
    feeding_time = Column(DateTime, default=get_now_naive, nullable=False, index=True)
    feeding_type = Column(SQLEnum(FeedingType), nullable=False)
    amount_ml = Column(Float, nullable=True)  # ミルクの量（母乳の場合はNull）
    duration_minutes = Column(Integer, nullable=True)  # 授乳時間（分）
    notes = Column(String, nullable=True)

    # リレーション
    baby = relationship("Baby", back_populates="feedings")
    user = relationship("User")
