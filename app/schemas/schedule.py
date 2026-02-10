"""スケジュールスキーマ"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ScheduleCreate(BaseModel):
    """スケジュール作成用スキーマ"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_time: datetime


class ScheduleUpdate(BaseModel):
    """スケジュール更新用スキーマ"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    is_completed: Optional[bool] = None


class ScheduleResponse(BaseModel):
    """スケジュールレスポンススキーマ"""
    id: int
    user_id: int
    title: str
    description: Optional[str]
    scheduled_time: datetime
    is_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True
