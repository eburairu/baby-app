"""睡眠記録モデル"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Sleep(Base):
    """睡眠記録テーブル"""
    __tablename__ = "sleeps"

    id = Column(Integer, primary_key=True, index=True)
    baby_id = Column(Integer, ForeignKey("babies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    end_time = Column(DateTime, nullable=True)  # 継続中の場合はNull
    notes = Column(String, nullable=True)

    # リレーション
    baby = relationship("Baby", back_populates="sleeps")
    user = relationship("User")

    @property
    def duration_minutes(self) -> int:
        """睡眠時間（分）を計算"""
        if not self.end_time:
            return 0
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)

    @property
    def is_ongoing(self) -> bool:
        """継続中かどうか"""
        return self.end_time is None
