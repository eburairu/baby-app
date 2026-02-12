from datetime import datetime
from zoneinfo import ZoneInfo
from app.config import settings

def get_now():
    """現在のタイムゾーンにおける現在時刻を返す"""
    return datetime.now(ZoneInfo(settings.TIMEZONE))

def get_now_naive():
    """タイムゾーン情報を含まない現在時刻を返す（DB保存用）"""
    return datetime.now(ZoneInfo(settings.TIMEZONE)).replace(tzinfo=None)
