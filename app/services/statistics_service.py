"""統計計算サービス"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.feeding import Feeding
from app.models.sleep import Sleep
from app.models.diaper import Diaper
from app.models.growth import Growth


class StatisticsService:
    """統計計算ビジネスロジック"""

    @staticmethod
    def get_feeding_stats(db: Session, baby_id: int, days: int = 7) -> dict:
        """授乳統計を取得"""
        start_date = datetime.utcnow() - timedelta(days=days)

        # 期間内の授乳回数
        feeding_count = db.query(func.count(Feeding.id)).filter(
            Feeding.baby_id == baby_id,
            Feeding.feeding_time >= start_date
        ).scalar()

        # 期間内の平均授乳量（ミルクのみ）
        avg_amount = db.query(func.avg(Feeding.amount_ml)).filter(
            Feeding.baby_id == baby_id,
            Feeding.feeding_time >= start_date,
            Feeding.amount_ml.isnot(None)
        ).scalar()

        return {
            "count": feeding_count or 0,
            "avg_amount_ml": round(avg_amount, 1) if avg_amount else 0,
            "period_days": days
        }

    @staticmethod
    def get_sleep_stats(db: Session, baby_id: int, days: int = 7) -> dict:
        """睡眠統計を取得"""
        start_date = datetime.utcnow() - timedelta(days=days)
        now = datetime.utcnow()

        # 期間内のすべての睡眠記録
        sleeps = db.query(Sleep).filter(
            Sleep.baby_id == baby_id,
            Sleep.start_time >= start_date
        ).all()

        total_minutes = 0
        for sleep in sleeps:
            if sleep.end_time:
                total_minutes += sleep.duration_minutes
            else:
                # 継続中の場合は現在時刻までの時間を加算
                delta = now - sleep.start_time
                total_minutes += int(delta.total_seconds() / 60)

        avg_minutes = total_minutes / len(sleeps) if sleeps else 0
        avg_hours = avg_minutes / 60

        return {
            "count": len(sleeps),
            "total_hours": round(total_minutes / 60, 1),
            "avg_hours": round(avg_hours, 1),
            "period_days": days
        }

    @staticmethod
    def get_diaper_stats(db: Session, baby_id: int, days: int = 7) -> dict:
        """おむつ交換統計を取得"""
        start_date = datetime.utcnow() - timedelta(days=days)

        diaper_count = db.query(func.count(Diaper.id)).filter(
            Diaper.baby_id == baby_id,
            Diaper.change_time >= start_date
        ).scalar()

        return {
            "count": diaper_count or 0,
            "period_days": days
        }

    @staticmethod
    def get_latest_growth(db: Session, baby_id: int) -> Growth:
        """最新の成長記録を取得"""
        return db.query(Growth).filter(
            Growth.baby_id == baby_id
        ).order_by(Growth.measurement_date.desc()).first()

    @staticmethod
    def get_recent_records(db: Session, baby_id: int, limit: int = 10) -> dict:
        """最新記録を取得"""
        feedings = db.query(Feeding).filter(
            Feeding.baby_id == baby_id
        ).order_by(Feeding.feeding_time.desc()).limit(limit).all()

        sleeps = db.query(Sleep).filter(
            Sleep.baby_id == baby_id
        ).order_by(Sleep.start_time.desc()).limit(limit).all()

        diapers = db.query(Diaper).filter(
            Diaper.baby_id == baby_id
        ).order_by(Diaper.change_time.desc()).limit(limit).all()

        return {
            "feedings": feedings,
            "sleeps": sleeps,
            "diapers": diapers
        }
