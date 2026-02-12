"""陣痛記録スキーマ"""
from datetime import datetime
from typing import Optional
from fastapi import Form
from pydantic import BaseModel


class ContractionCreate(BaseModel):
    """陣痛記録作成用スキーマ"""
    start_time: datetime
    notes: Optional[str] = None


class ContractionEnd(BaseModel):
    """陣痛終了用スキーマ"""
    end_time: datetime


class ContractionUpdate(BaseModel):
    """陣痛記録更新用スキーマ"""
    start_time: datetime
    end_time: Optional[datetime] = None
    notes: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        start_time: str = Form(...),
        end_time: Optional[str] = Form(None),
        notes: Optional[str] = Form(None),
    ):
        try:
            st = datetime.fromisoformat(start_time)
            et = datetime.fromisoformat(end_time) if end_time else None
        except ValueError:
            st, et = start_time, end_time
        return cls(start_time=st, end_time=et, notes=notes)


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
