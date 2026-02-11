"""成長記録スキーマ"""
from datetime import date
from typing import Optional
from fastapi import Form
from pydantic import BaseModel, Field


class GrowthCreate(BaseModel):
    """成長記録作成用スキーマ"""
    measurement_date: date
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    head_circumference_cm: Optional[float] = None
    notes: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        measurement_date: str = Form(...),
        weight_kg: Optional[float] = Form(None),
        height_cm: Optional[float] = Form(None),
        head_circumference_cm: Optional[float] = Form(None),
        notes: Optional[str] = Form(None),
    ):
        try:
            d = date.fromisoformat(measurement_date)
        except ValueError:
            d = measurement_date
        return cls(
            measurement_date=d,
            weight_kg=weight_kg,
            height_cm=height_cm,
            head_circumference_cm=head_circumference_cm,
            notes=notes
        )


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
