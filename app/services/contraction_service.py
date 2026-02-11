"""陣痛タイマーサービス"""
from datetime import datetime, timedelta
from typing import Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.contraction import Contraction


class ContractionService:
    """陣痛タイマー関連のビジネスロジック"""

    @staticmethod
    def calculate_interval(db: Session, user_id: int) -> Optional[int]:
        """
        前回の陣痛終了時刻から今回の開始時刻までの間隔を計算（秒）
        """
        # 最新の完了した陣痛記録を取得
        last_contraction = db.query(Contraction).filter(
            Contraction.user_id == user_id,
            Contraction.end_time.isnot(None)
        ).order_by(Contraction.start_time.desc()).first()

        if not last_contraction or not last_contraction.end_time:
            return None

        # 前回の終了時刻から現在までの秒数
        now = datetime.utcnow()
        interval = (now - last_contraction.end_time).total_seconds()

        return int(interval)

    @staticmethod
    def calculate_duration(start_time: datetime, end_time: datetime) -> int:
        """持続時間を計算（秒）"""
        duration = (end_time - start_time).total_seconds()
        return int(duration)

    @staticmethod
    def get_statistics(db: Session, user_id: int, hours: int = 1) -> Dict:
        """
        直近N時間の陣痛統計を計算
        """
        start_time = datetime.utcnow() - timedelta(hours=hours)

        # 期間内のすべての陣痛記録（進行中も含む）
        contractions = db.query(Contraction).filter(
            Contraction.user_id == user_id,
            Contraction.start_time >= start_time
        ).all()

        if not contractions:
            return {
                "count": 0,
                "avg_duration_seconds": 0,
                "avg_interval_seconds": 0,
                "last_interval_seconds": None,
                "period_hours": hours
            }

        # 完了した記録
        completed_contractions = [c for c in contractions if c.end_time is not None]

        # 平均持続時間（完了したもののみ）
        avg_duration = sum(
            c.duration_seconds for c in completed_contractions if c.duration_seconds
        ) / len(completed_contractions) if completed_contractions else 0

        # 平均間隔（間隔データがある記録のみ）
        intervals = [c.interval_seconds for c in contractions if c.interval_seconds]
        avg_interval = sum(intervals) / len(intervals) if intervals else 0

        # 最新の間隔（これは進行中のものでも、直近の「開始時」にセットされているはず）
        last_interval = contractions[-1].interval_seconds if contractions else None

        return {
            "count": len(contractions),
            "avg_duration_seconds": int(avg_duration),
            "avg_interval_seconds": int(avg_interval),
            "last_interval_seconds": last_interval,
            "period_hours": hours
        }

    @staticmethod
    def format_seconds(seconds: Optional[int]) -> str:
        """秒を分:秒形式に変換"""
        if seconds is None:
            return "-"
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
