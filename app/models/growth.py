"""成長記録モデル"""
from datetime import date
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Growth(Base):
    """成長記録テーブル"""
    __tablename__ = "growths"

    id = Column(Integer, primary_key=True, index=True)
    baby_id = Column(Integer, ForeignKey("babies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    measurement_date = Column(Date, nullable=False, index=True)
    weight_kg = Column(Float, nullable=True)  # 体重（kg）
    height_cm = Column(Float, nullable=True)  # 身長（cm）
    head_circumference_cm = Column(Float, nullable=True)  # 頭囲（cm）
    notes = Column(String, nullable=True)

    # リレーション
    baby = relationship("Baby", back_populates="growths")
    user = relationship("User")
