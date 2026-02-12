"""統計計算サービス"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.utils.time import get_now_naive

from app.models.feeding import Feeding
from app.models.sleep import Sleep
from app.models.diaper import Diaper
from app.models.growth import Growth


class StatisticsService:
    """統計計算ビジネスロジック"""

    @staticmethod
    def get_feeding_stats(db: Session, baby_id: int, days: int = 7) -> dict:
        """授乳統計を取得（SQL最適化版）"""
        start_date = get_now_naive() - timedelta(days=days)

        # 1回のクエリで授乳回数と平均授乳量を取得
        result = db.query(
            func.count(Feeding.id).label('count'),
            func.avg(Feeding.amount_ml).label('avg_amount')
        ).filter(
            Feeding.baby_id == baby_id,
            Feeding.feeding_time >= start_date
        ).first()

        return {
            "count": result.count or 0,
            "avg_amount_ml": round(result.avg_amount, 1) if result.avg_amount else 0,
            "period_days": days
        }

    @staticmethod
    def get_sleep_stats(db: Session, baby_id: int, days: int = 7) -> dict:
        """睡眠統計を取得（SQL最適化版）"""
        start_date = get_now_naive() - timedelta(days=days)
        now = get_now_naive()

        # 1. 完了した睡眠記録の統計（SQLで集計）
        # duration_minutes はプロパティなのでSQL計算式で代替
        completed_stats = db.query(
            func.count(Sleep.id).label('count'),
            func.sum(
                func.extract('epoch', Sleep.end_time - Sleep.start_time) / 60
            ).label('total_minutes')
        ).filter(
            Sleep.baby_id == baby_id,
            Sleep.start_time >= start_date,
            Sleep.end_time.isnot(None)
        ).first()

        # 2. 進行中の睡眠記録（少数のみメモリにロード）
        ongoing_sleeps = db.query(Sleep).filter(
            Sleep.baby_id == baby_id,
            Sleep.start_time >= start_date,
            Sleep.end_time.is_(None)
        ).all()

        # 3. 集計
        total_minutes = completed_stats.total_minutes or 0
        count = completed_stats.count or 0

        for sleep in ongoing_sleeps:
            delta = now - sleep.start_time
            total_minutes += int(delta.total_seconds() / 60)
            count += 1

        avg_hours = (total_minutes / count / 60) if count > 0 else 0

        return {
            "count": count,
            "total_hours": round(total_minutes / 60, 1),
            "avg_hours": round(avg_hours, 1),
            "period_days": days
        }

    @staticmethod
    def get_diaper_stats(db: Session, baby_id: int, days: int = 7) -> dict:
        """おむつ交換統計を取得"""
        start_date = get_now_naive() - timedelta(days=days)

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

    @staticmethod
    def get_recent_records_selective(
        db: Session,
        baby_id: int,
        include_feeding: bool = True,
        include_sleep: bool = True,
        include_diaper: bool = True,
        limit: int = 10
    ) -> dict:
        """権限に基づいて最新記録を選択的に取得（パフォーマンス最適化版）

        Args:
            db: データベースセッション
            baby_id: 赤ちゃんID
            include_feeding: 授乳記録を含めるか
            include_sleep: 睡眠記録を含めるか
            include_diaper: おむつ記録を含めるか
            limit: 各記録の取得上限

        Returns:
            最新記録の辞書
        """
        result = {}

        if include_feeding:
            result["feedings"] = db.query(Feeding).filter(
                Feeding.baby_id == baby_id
            ).order_by(Feeding.feeding_time.desc()).limit(limit).all()
        else:
            result["feedings"] = []

        if include_sleep:
            result["sleeps"] = db.query(Sleep).filter(
                Sleep.baby_id == baby_id
            ).order_by(Sleep.start_time.desc()).limit(limit).all()
        else:
            result["sleeps"] = []

        if include_diaper:
            result["diapers"] = db.query(Diaper).filter(
                Diaper.baby_id == baby_id
            ).order_by(Diaper.change_time.desc()).limit(limit).all()
        else:
            result["diapers"] = []

        return result
