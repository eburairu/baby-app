"""授乳記録スキーマ"""
from datetime import datetime
from typing import Optional
from fastapi import Form
from pydantic import BaseModel, Field, field_validator

from app.models.feeding import FeedingType


class FeedingCreate(BaseModel):
    """授乳記録作成用スキーマ"""
    feeding_time: datetime
    feeding_type: FeedingType
    amount_ml: Optional[float] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        feeding_time: str = Form(...),
        feeding_type: FeedingType = Form(...),
        amount_ml: Optional[float] = Form(None),
        duration_minutes: Optional[int] = Form(None),
        notes: Optional[str] = Form(None),
    ):
        # 空文字列の処理
        try:
            dt = datetime.fromisoformat(feeding_time)
        except ValueError:
            # Pydantic 側でエラーを出すために不正な値を渡すか、ここで raise する
            dt = feeding_time

        return cls(
            feeding_time=dt,
            feeding_type=feeding_type,
            amount_ml=amount_ml,
            duration_minutes=duration_minutes,
            notes=notes
        )

    @field_validator("amount_ml")
    @classmethod
    def validate_amount(cls, v: Optional[float], info):
        if v is not None and v < 0:
            raise ValueError("量は正の数である必要があります")
        return v


class FeedingUpdate(BaseModel):
    """授乳記録更新用スキーマ"""
    feeding_time: Optional[datetime] = None
    feeding_type: Optional[FeedingType] = None
    amount_ml: Optional[float] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        feeding_time: str = Form(None),
        feeding_type: FeedingType = Form(None),
        amount_ml: Optional[float] = Form(None),
        duration_minutes: Optional[int] = Form(None),
        notes: Optional[str] = Form(None),
    ):
        dt = None
        if feeding_time:
            try:
                dt = datetime.fromisoformat(feeding_time)
            except ValueError:
                dt = feeding_time

        return cls(
            feeding_time=dt,
            feeding_type=feeding_type,
            amount_ml=amount_ml,
            duration_minutes=duration_minutes,
            notes=notes
        )


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
