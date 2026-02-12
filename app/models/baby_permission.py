"""赤ちゃん情報閲覧権限モデル"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class BabyPermission(Base):
    """ユーザーごとの赤ちゃん・記録タイプ別の権限設定"""
    __tablename__ = "baby_permissions"

    id = Column(Integer, primary_key=True, index=True)
    baby_id = Column(Integer, ForeignKey("babies.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # 記録タイプ: 'feeding', 'sleep', 'diaper', 'growth', 'schedule', 'contraction', 'basic_info'
    record_type = Column(String, nullable=False)
    
    can_view = Column(Boolean, default=True, nullable=False)
    # can_edit = Column(Boolean, default=True, nullable=False) # 将来的な拡張用

    # 同一ユーザー・同一赤ちゃん・同一タイプに複数の設定は持たせない
    __table_args__ = (
        UniqueConstraint('baby_id', 'user_id', 'record_type', name='uix_baby_user_record_type'),
    )

    # リレーション
    baby = relationship("Baby")
    user = relationship("User")
