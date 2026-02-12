"""睡眠記録スキーマ"""
from datetime import datetime
from typing import Optional
from fastapi import Form, HTTPException
from pydantic import BaseModel, Field


class SleepCreate(BaseModel):
    """睡眠記録作成用スキーマ"""
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
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"日時の形式が正しくありません: {e}"
            )

        return cls(start_time=st, end_time=et, notes=notes)


class SleepUpdate(BaseModel):
    """睡眠記録更新用スキーマ"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        start_time: Optional[str] = Form(None),
        end_time: Optional[str] = Form(None),
        notes: Optional[str] = Form(None),
    ):
        try:
            st = datetime.fromisoformat(start_time) if start_time else None
            et = datetime.fromisoformat(end_time) if end_time else None
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"日時の形式が正しくありません: {e}"
            )
        return cls(start_time=st, end_time=et, notes=notes)


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
