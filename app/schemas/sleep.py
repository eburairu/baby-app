"""睡眠記録スキーマ"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SleepCreate(BaseModel):
    """睡眠記録作成用スキーマ"""
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    notes: Optional[str] = None


class SleepUpdate(BaseModel):
    """睡眠記録更新用スキーマ"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: Optional[str] = None


class SleepResponse(BaseModel):
    """睡眠記録レスポンススキーマ"""
    id: int
    user_id: int
    start_time: datetime
    end_time: Optional[datetime]
    notes: Optional[str]
    duration_minutes: int
    is_ongoing: bool

    class Config:
        from_attributes = True
