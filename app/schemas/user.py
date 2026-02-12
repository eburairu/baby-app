"""ユーザースキーマ"""
from datetime import datetime
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """ユーザー登録用スキーマ"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=72)


class UserLogin(BaseModel):
    """ログイン用スキーマ"""
    username: str
    password: str



class UserRegisterRequest(BaseModel):
    """ユーザー登録リクエストスキーマ"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=72)
    invite_code: str
    email_confirm_hidden: str | None = None  # Honeypot


class UserResponse(BaseModel):
    """ユーザーレスポンススキーマ"""
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True
