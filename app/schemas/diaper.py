"""おむつ交換記録スキーマ"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.diaper import DiaperType


class DiaperCreate(BaseModel):
    """おむつ交換記録作成用スキーマ"""
    change_time: datetime = Field(default_factory=datetime.utcnow)
    diaper_type: DiaperType
    notes: Optional[str] = None


class DiaperUpdate(BaseModel):
    """おむつ交換記録更新用スキーマ"""
    change_time: Optional[datetime] = None
    diaper_type: Optional[DiaperType] = None
    notes: Optional[str] = None


class DiaperResponse(BaseModel):
    """おむつ交換記録レスポンススキーマ"""
    id: int
    user_id: int
    change_time: datetime
    diaper_type: DiaperType
    notes: Optional[str]

    class Config:
        from_attributes = True
