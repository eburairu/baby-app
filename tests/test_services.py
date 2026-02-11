import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User
from app.models.sleep import Sleep
from app.models.contraction import Contraction
from app.models.feeding import Feeding
from app.models.diaper import Diaper
from app.models.growth import Growth
from app.models.schedule import Schedule
from app.services.statistics_service import StatisticsService
from app.services.contraction_service import ContractionService

# テスト用データベースの設定 (SQLite インメモリ)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db):
    user = User(username="testuser", hashed_password="hashed_password")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def test_get_sleep_stats_including_ongoing(db, test_user):
    """
    継続中の睡眠記録が統計に含まれるかテスト
    """
    # 1. 完了した睡眠 (2時間)
    sleep1 = Sleep(
        user_id=test_user.id,
        start_time=datetime.utcnow() - timedelta(hours=5),
        end_time=datetime.utcnow() - timedelta(hours=3)
    )
    # 2. 継続中の睡眠 (現在まで3時間経過していると仮定)
    sleep2 = Sleep(
        user_id=test_user.id,
        start_time=datetime.utcnow() - timedelta(hours=3),
        end_time=None
    )
    db.add_all([sleep1, sleep2])
    db.commit()

    stats = StatisticsService.get_sleep_stats(db, test_user.id)
    
    # 現状のバグ: 継続中の睡眠は count に含まれず、total_hours にも加算されないはず
    # 理想的な挙動: count=2, total_hours=5.0
    print(f"Current Sleep Stats: {stats}")
    assert stats["count"] == 2, "継続中の睡眠もカウントに含めるべき"

def test_get_contraction_stats_including_ongoing(db, test_user):
    """
    進行中の陣痛が統計に含まれるかテスト
    """
    # 1. 完了した陣痛
    c1 = Contraction(
        user_id=test_user.id,
        start_time=datetime.utcnow() - timedelta(minutes=30),
        end_time=datetime.utcnow() - timedelta(minutes=29),
        duration_seconds=60,
        interval_seconds=600
    )
    # 2. 進行中の陣痛
    c2 = Contraction(
        user_id=test_user.id,
        start_time=datetime.utcnow() - timedelta(minutes=5),
        end_time=None
    )
    db.add_all([c1, c2])
    db.commit()

    stats = ContractionService.get_statistics(db, test_user.id)

    # 現状のバグ: 進行中の陣痛は count に含まれないはず
    # 理想的な挙動: count=2
    print(f"Current Contraction Stats: {stats}")
    assert stats["count"] == 2, "進行中の陣痛もカウントに含めるべき"
