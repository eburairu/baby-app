"""
統一されたAPIレスポンススキーマ

Next.jsフロントエンドとの一貫したインターフェースを提供する。
"""
from typing import Generic, TypeVar, Optional, Any, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict


T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """
    標準APIレスポンス

    すべてのAPIエンドポイントが使用する共通レスポンス構造
    """
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    timestamp: datetime = datetime.now()

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    """
    ページネーション対応レスポンス
    """
    items: List[T]
    total: int
    page: int = 1
    page_size: int = 50
    has_next: bool = False
    has_prev: bool = False

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """
    エラーレスポンス
    """
    success: bool = False
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = datetime.now()

    model_config = ConfigDict(from_attributes=True)


class BabyBasicInfo(BaseModel):
    """
    赤ちゃんの基本情報（レスポンスに含める用）
    """
    id: int
    name: str
    birthday: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DashboardData(BaseModel):
    """
    ダッシュボードデータ
    """
    baby: Optional[BabyBasicInfo] = None
    feeding_stats: Optional[dict] = None
    sleep_stats: Optional[dict] = None
    diaper_stats: Optional[dict] = None
    latest_growth: Optional[dict] = None
    recent_records: Optional[dict] = None
    prenatal_info: Optional[dict] = None
    perms: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class ListResponse(BaseModel, Generic[T]):
    """
    リスト表示用レスポンス（記録一覧など）
    """
    items: List[T]
    baby: Optional[BabyBasicInfo] = None
    viewable_babies: Optional[List[BabyBasicInfo]] = None
    perms: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)
