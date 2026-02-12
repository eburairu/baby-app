"""スケジュールスキーマ"""
from datetime import datetime
from typing import Optional
from fastapi import Form
from pydantic import BaseModel, Field


class ScheduleCreate(BaseModel):
    """スケジュール作成用スキーマ"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_time: datetime

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        description: Optional[str] = Form(None),
        scheduled_time: str = Form(...),
    ):
        try:
            st = datetime.fromisoformat(scheduled_time)
        except ValueError:
            st = scheduled_time
        return cls(
            title=title,
            description=description,
            scheduled_time=st
        )


class ScheduleUpdate(BaseModel):
    """スケジュール更新用スキーマ"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    is_completed: Optional[bool] = None

    @classmethod
    def as_form(
        cls,
        title: Optional[str] = Form(None),
        description: Optional[str] = Form(None),
        scheduled_time: Optional[str] = Form(None),
        is_completed: Optional[bool] = Form(None),
    ):
        st = None
        if scheduled_time:
            try:
                st = datetime.fromisoformat(scheduled_time)
            except ValueError:
                st = scheduled_time
        
        return cls(
            title=title,
            description=description,
            scheduled_time=st,
            is_completed=is_completed
        )


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
