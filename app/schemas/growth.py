"""成長記録スキーマ"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class GrowthCreate(BaseModel):
    """成長記録作成用スキーマ"""
    measurement_date: date = Field(default_factory=date.today)
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    head_circumference_cm: Optional[float] = None
    notes: Optional[str] = None


class GrowthUpdate(BaseModel):
    """成長記録更新用スキーマ"""
    measurement_date: Optional[date] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    head_circumference_cm: Optional[float] = None
    notes: Optional[str] = None


class GrowthResponse(BaseModel):
    """成長記録レスポンススキーマ"""
    id: int
    user_id: int
    measurement_date: date
    weight_kg: Optional[float]
    height_cm: Optional[float]
    head_circumference_cm: Optional[float]
    notes: Optional[str]

    class Config:
        from_attributes = True
