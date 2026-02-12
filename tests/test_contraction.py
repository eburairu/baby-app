import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.baby import Baby
from app.models.family import Family
from app.models.user import User
from app.models.contraction import Contraction
from app.services.contraction_service import ContractionService
from app.utils.time import get_now_naive

@pytest.mark.asyncio
async def test_get_contraction_stats_with_ongoing(db: Session):
    """進行中の陣痛を含む統計計算をテスト"""
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

    # 1. 完了した陣痛 (持続時間60秒, 間隔300秒)
    db.add(Contraction(
        baby_id=baby.id,
        user_id=user.id,
        start_time=now - timedelta(minutes=10),
        end_time=now - timedelta(minutes=9),
        duration_seconds=60,
        interval_seconds=300 
    ))

    # 2. 進行中の陣痛 (30秒経過)
    db.add(Contraction(
        baby_id=baby.id,
        user_id=user.id,
        start_time=now - timedelta(seconds=30),
        interval_seconds=510 # (10-1) * 60 - 30 = 510
    ))
    db.commit()

    # Test
    stats = ContractionService.get_statistics(db, baby.id, hours=1)

    # Assertions
    assert stats["count"] == 2
    
    # 平均持続時間: (60秒 + 30秒) / 2 = 45秒
    assert stats["avg_duration_seconds"] == 45
    
    # 平均間隔: (300 + 510) / 2 = 405
    assert stats["avg_interval_seconds"] == 405
    
    assert stats["last_interval_seconds"] == 510
