"""サービスレイヤーのテスト

DB fixture (db, test_user, test_baby) は conftest.py で定義。
TEST_DATABASE_URL 環境変数でPostgreSQLも使用可能。
"""
from datetime import datetime, timedelta

from app.models.sleep import Sleep
from app.models.feeding import Feeding, FeedingType
from app.models.diaper import Diaper, DiaperType
from app.models.contraction import Contraction
from app.services.statistics_service import StatisticsService
from app.services.contraction_service import ContractionService
from app.utils.time import get_now_naive


def test_get_sleep_stats_including_ongoing(db, test_user, test_baby):
    """
    継続中の睡眠記録が統計に含まれるかテスト
    """
    # 1. 完了した睡眠 (2時間)
    sleep1 = Sleep(
        baby_id=test_baby.id,
        user_id=test_user.id,
        start_time=get_now_naive() - timedelta(hours=5),
        end_time=get_now_naive() - timedelta(hours=3)
    )
    # 2. 継続中の睡眠 (現在まで3時間経過していると仮定)
    sleep2 = Sleep(
        baby_id=test_baby.id,
        user_id=test_user.id,
        start_time=get_now_naive() - timedelta(hours=3),
        end_time=None
    )
    db.add_all([sleep1, sleep2])
    db.commit()

    stats = StatisticsService.get_sleep_stats(db, test_baby.id)

    # 理想的な挙動: count=2, total_hours=5.0
    print(f"Current Sleep Stats: {stats}")
    assert stats["count"] == 2, "継続中の睡眠もカウントに含めるべき"


def test_get_contraction_stats_including_ongoing(db, test_user, test_baby):
    """
    進行中の陣痛が統計に含まれるかテスト
    """
    # 1. 完了した陣痛
    c1 = Contraction(
        baby_id=test_baby.id,
        user_id=test_user.id,
        start_time=get_now_naive() - timedelta(minutes=30),
        end_time=get_now_naive() - timedelta(minutes=29),
        duration_seconds=60,
        interval_seconds=600
    )
    # 2. 進行中の陣痛
    c2 = Contraction(
        baby_id=test_baby.id,
        user_id=test_user.id,
        start_time=get_now_naive() - timedelta(minutes=5),
        end_time=None
    )
    db.add_all([c1, c2])
    db.commit()

    stats = ContractionService.get_statistics(db, test_baby.id)

    # 理想的な挙動: count=2
    print(f"Current Contraction Stats: {stats}")
    assert stats["count"] == 2, "進行中の陣痛もカウントに含めるべき"


def test_get_sleep_stats_empty(db, test_baby):
    """
    記録がない場合の睡眠統計
    """
    stats = StatisticsService.get_sleep_stats(db, test_baby.id)
    assert stats["count"] == 0
    assert stats["total_hours"] == 0
    assert stats["avg_hours"] == 0


def test_get_sleep_stats_boundary(db, test_user, test_baby):
    """
    期間外の記録が除外されるかテスト
    """
    # 8日前の記録 (期間外)
    sleep_old = Sleep(
        baby_id=test_baby.id,
        user_id=test_user.id,
        start_time=get_now_naive() - timedelta(days=8),
        end_time=get_now_naive() - timedelta(days=7, hours=22)
    )
    # 6日前の記録 (期間内)
    sleep_new = Sleep(
        baby_id=test_baby.id,
        user_id=test_user.id,
        start_time=get_now_naive() - timedelta(days=6),
        end_time=get_now_naive() - timedelta(days=6, hours=-2) # 2時間
    )
    db.add_all([sleep_old, sleep_new])
    db.commit()

    stats = StatisticsService.get_sleep_stats(db, test_baby.id, days=7)
    assert stats["count"] == 1
    assert stats["total_hours"] == 2.0


def test_get_contraction_stats_empty(db, test_baby):
    """
    記録がない場合の陣痛統計
    """
    stats = ContractionService.get_statistics(db, test_baby.id)
    assert stats["count"] == 0
    assert stats["avg_duration_seconds"] == 0


def test_get_feeding_stats_optimized(db, test_user, test_baby):
    """
    授乳統計のSQL最適化版が正しく動作するかテスト
    """
    # 複数の授乳記録を作成
    feeding1 = Feeding(
        baby_id=test_baby.id,
        user_id=test_user.id,
        feeding_time=get_now_naive() - timedelta(hours=2),
        feeding_type=FeedingType.BREAST,
        amount_ml=100
    )
    feeding2 = Feeding(
        baby_id=test_baby.id,
        user_id=test_user.id,
        feeding_time=get_now_naive() - timedelta(hours=4),
        feeding_type=FeedingType.BOTTLE,
        amount_ml=150
    )
    feeding3 = Feeding(
        baby_id=test_baby.id,
        user_id=test_user.id,
        feeding_time=get_now_naive() - timedelta(hours=6),
        feeding_type=FeedingType.BOTTLE,
        amount_ml=200
    )
    db.add_all([feeding1, feeding2, feeding3])
    db.commit()

    stats = StatisticsService.get_feeding_stats(db, test_baby.id)

    assert stats["count"] == 3
    assert stats["avg_amount_ml"] == 150.0  # (100 + 150 + 200) / 3


def test_get_recent_records_selective(db, test_user, test_baby):
    """
    最新記録の選択的取得が正しく動作するかテスト
    """
    # データを作成
    feeding = Feeding(
        baby_id=test_baby.id,
        user_id=test_user.id,
        feeding_time=get_now_naive(),
        feeding_type=FeedingType.BREAST
    )
    sleep = Sleep(
        baby_id=test_baby.id,
        user_id=test_user.id,
        start_time=get_now_naive() - timedelta(hours=2),
        end_time=get_now_naive() - timedelta(hours=1)
    )
    diaper = Diaper(
        baby_id=test_baby.id,
        user_id=test_user.id,
        change_time=get_now_naive() - timedelta(hours=3),
        diaper_type=DiaperType.WET
    )
    db.add_all([feeding, sleep, diaper])
    db.commit()

    # 全て取得
    result_all = StatisticsService.get_recent_records_selective(
        db, test_baby.id,
        include_feeding=True,
        include_sleep=True,
        include_diaper=True
    )
    assert len(result_all["feedings"]) == 1
    assert len(result_all["sleeps"]) == 1
    assert len(result_all["diapers"]) == 1

    # 授乳のみ取得
    result_feeding_only = StatisticsService.get_recent_records_selective(
        db, test_baby.id,
        include_feeding=True,
        include_sleep=False,
        include_diaper=False
    )
    assert len(result_feeding_only["feedings"]) == 1
    assert len(result_feeding_only["sleeps"]) == 0
    assert len(result_feeding_only["diapers"]) == 0

    # 何も取得しない
    result_none = StatisticsService.get_recent_records_selective(
        db, test_baby.id,
        include_feeding=False,
        include_sleep=False,
        include_diaper=False
    )
    assert len(result_none["feedings"]) == 0
    assert len(result_none["sleeps"]) == 0
    assert len(result_none["diapers"]) == 0
