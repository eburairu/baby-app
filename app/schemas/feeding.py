"""授乳記録スキーマ"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.feeding import FeedingType


class FeedingCreate(BaseModel):
    """授乳記録作成用スキーマ"""
    feeding_time: datetime = Field(default_factory=datetime.utcnow)
    feeding_type: FeedingType
    amount_ml: Optional[float] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None


class FeedingUpdate(BaseModel):
    """授乳記録更新用スキーマ"""
    feeding_time: Optional[datetime] = None
    feeding_type: Optional[FeedingType] = None
    amount_ml: Optional[float] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None


class FeedingResponse(BaseModel):
    """授乳記録レスポンススキーマ"""
    id: int
    user_id: int
    feeding_time: datetime
    feeding_type: FeedingType
    amount_ml: Optional[float]
    duration_minutes: Optional[int]
    notes: Optional[str]

    class Config:
        from_attributes = True
