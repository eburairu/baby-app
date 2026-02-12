import pytest
from datetime import datetime, timedelta
from app.models.sleep import Sleep
from app.dependencies import get_current_user, get_current_baby
from app.main import app

@pytest.mark.asyncio
async def test_start_sleep_while_ongoing(client, db, test_user, test_baby):
    """既に継続中の睡眠がある場合にエラーになることを確認"""

    # 1. 継続中の睡眠を作成
    ongoing_sleep = Sleep(
        baby_id=test_baby.id,
        user_id=test_user.id,
        start_time=datetime.utcnow() - timedelta(hours=1),
        end_time=None  # 継続中
    )
    db.add(ongoing_sleep)
    db.commit()
    db.refresh(ongoing_sleep)

    # 2. 認証モック
    def mock_get_current_user():
        return test_user

    def mock_get_current_baby():
        return test_baby

    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[get_current_baby] = mock_get_current_baby

    try:
        # 3. リクエスト送信
        response = await client.post("/sleeps/start")

        # 4. アサーション
        assert response.status_code == 400
        assert response.json()["detail"] == "既に睡眠が継続中です"

    finally:
        app.dependency_overrides.clear()
