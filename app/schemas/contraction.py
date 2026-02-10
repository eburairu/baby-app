"""陣痛記録スキーマ"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ContractionCreate(BaseModel):
    """陣痛記録作成用スキーマ"""
    start_time: datetime
    notes: Optional[str] = None


class ContractionEnd(BaseModel):
    """陣痛終了用スキーマ"""
    end_time: datetime


class ContractionResponse(BaseModel):
    """陣痛記録レスポンススキーマ"""
    id: int
    user_id: int
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[int]
    interval_seconds: Optional[int]
    notes: Optional[str]
    is_ongoing: bool
    duration_display: str
    interval_display: str

    class Config:
        from_attributes = True
