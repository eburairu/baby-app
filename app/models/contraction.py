"""陣痛記録モデル"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Contraction(Base):
    """陣痛記録テーブル"""
    __tablename__ = "contractions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=True)  # 継続中の場合はNull
    duration_seconds = Column(Integer, nullable=True)  # 持続時間（秒）
    interval_seconds = Column(Integer, nullable=True)  # 前回からの間隔（秒）
    notes = Column(String, nullable=True)

    # リレーション
    user = relationship("User", back_populates="contractions")

    @property
    def is_ongoing(self) -> bool:
        """継続中かどうか"""
        return self.end_time is None

    @property
    def duration_display(self) -> str:
        """持続時間を分:秒で表示"""
        if not self.duration_seconds:
            return "-"
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes}:{seconds:02d}"

    @property
    def interval_display(self) -> str:
        """間隔を分:秒で表示"""
        if not self.interval_seconds:
            return "-"
        minutes = self.interval_seconds // 60
        seconds = self.interval_seconds % 60
        return f"{minutes}:{seconds:02d}"
