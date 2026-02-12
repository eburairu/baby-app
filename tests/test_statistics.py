import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.baby import Baby
from app.models.family import Family
from app.models.user import User
from app.models.sleep import Sleep
from app.services.statistics_service import StatisticsService
from app.utils.time import get_now_naive

@pytest.mark.asyncio
async def test_get_sleep_stats_with_ongoing_sleep(db: Session):
    """継続中の睡眠を含む睡眠統計が正しく計算されるかテスト"""
    # Setup
    family = Family(name="Test Family", invite_code=Family.generate_invite_code())
    user = User(username="testuser", hashed_password="password")
    db.add(family)
    db.add(user)
    db.commit()

    baby = Baby(name="Test Baby", family_id=family.id)
    db.add(baby)
    db.commit()

    now = get_now_naive()
    
    # 1. 完了した睡眠 (1時間)
    db.add(Sleep(
        baby_id=baby.id,
        user_id=user.id,
        start_time=now - timedelta(days=1, hours=2),
        end_time=now - timedelta(days=1, hours=1)
    ))
    
    # 2. 継続中の睡眠 (30分経過)
    db.add(Sleep(
        baby_id=baby.id,
        user_id=user.id,
        start_time=now - timedelta(minutes=30)
    ))
    db.commit()

    # Test
    stats = StatisticsService.get_sleep_stats(db, baby.id, days=2)
    
    # Assertions
    assert stats["count"] == 2
    
    # 合計時間: 60分 (完了) + 30分 (継続中) = 90分 = 1.5時間
    assert stats["total_hours"] == 1.5
    
    # 平均時間: 90分 / 2回 = 45分 = 0.75時間 -> 0.8時間（丸め）
    assert stats["avg_hours"] == 0.8
    assert stats["period_days"] == 2

@pytest.mark.asyncio
async def test_get_sleep_stats_no_records(db: Session):
    """睡眠記録がない場合に統計が0を返すかテスト"""
    family = Family(name="Test Family", invite_code=Family.generate_invite_code())
    db.add(family)
    db.commit()
    baby = Baby(name="No Sleep Baby", family_id=family.id)
    db.add(baby)
    db.commit()

    stats = StatisticsService.get_sleep_stats(db, baby.id, days=7)
    
    assert stats["count"] == 0
    assert stats["total_hours"] == 0
    assert stats["avg_hours"] == 0

@pytest.mark.asyncio
async def test_get_sleep_stats_only_completed(db: Session):
    """完了した睡眠記録のみの場合の統計テスト"""
    family = Family(name="Test Family", invite_code=Family.generate_invite_code())
    user = User(username="testuser", hashed_password="password")
    db.add(family)
    db.add(user)
    db.commit()

    baby = Baby(name="Completed Sleep Baby", family_id=family.id)
    db.add(baby)
    db.commit()

    now = get_now_naive()

    # 1. 60分
    db.add(Sleep(
        baby_id=baby.id,
        user_id=user.id,
        start_time=now - timedelta(hours=3),
        end_time=now - timedelta(hours=2)
    ))
    # 2. 90分
    db.add(Sleep(
        baby_id=baby.id,
        user_id=user.id,
        start_time=now - timedelta(hours=6),
        end_time=now - timedelta(hours=4, minutes=30)
    ))
    db.commit()

    stats = StatisticsService.get_sleep_stats(db, baby.id, days=1)

    assert stats["count"] == 2
    # 合計時間: 60 + 90 = 150分 = 2.5時間
    assert stats["total_hours"] == 2.5
    # 平均時間: 150 / 2 = 75分 = 1.25時間 -> 1.2時間（最近接偶数への丸め）
    assert stats["avg_hours"] == 1.2
