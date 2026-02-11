"""赤ちゃんモデル"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Baby(Base):
    """赤ちゃんテーブル"""
    __tablename__ = "babies"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    name = Column(String, nullable=False)
    birthday = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # リレーション
    family = relationship("Family", back_populates="babies")
    
    # 記録類のリレーション
    feedings = relationship("Feeding", back_populates="baby", cascade="all, delete-orphan")
    sleeps = relationship("Sleep", back_populates="baby", cascade="all, delete-orphan")
    diapers = relationship("Diaper", back_populates="baby", cascade="all, delete-orphan")
    growths = relationship("Growth", back_populates="baby", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="baby", cascade="all, delete-orphan")
    contractions = relationship("Contraction", back_populates="baby", cascade="all, delete-orphan")
