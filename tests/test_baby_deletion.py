from app.main import app
from app.dependencies import get_current_user, get_current_family, admin_required
from app.models.baby import Baby
from app.models.family_user import FamilyUser
from app.models.user import User
import pytest

@pytest.mark.asyncio
async def test_delete_baby_admin(client, db, test_user, test_baby):
    """管理者は赤ちゃんを削除できる"""
    # 認証モック
    def mock_get_current_user():
        return test_user
    
    def mock_get_current_family():
        return test_baby.family
        
    def mock_admin_required():
        # adminロールであることを確認するロジックを通過させる
        return True

    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[get_current_family] = mock_get_current_family
    app.dependency_overrides[admin_required] = mock_admin_required

    response = await client.post(f"/babies/{test_baby.id}/delete", follow_redirects=False)
    
    assert response.status_code == 303
    assert response.headers["location"] == "/families/settings"
    
    # DBから消えているか確認
    deleted_baby = db.query(Baby).filter(Baby.id == test_baby.id).first()
    assert deleted_baby is None

@pytest.mark.asyncio
async def test_delete_baby_non_admin(client, db, test_baby):
    """非管理者は赤ちゃんを削除できない（権限エラーでリダイレクト）"""
    # 非管理者ユーザー作成
    other_user = User(username="other", hashed_password="pw")
    db.add(other_user)
    db.commit()
    db.refresh(other_user)
    
    # 家族に参加（メンバーロール）
    fu = FamilyUser(family_id=test_baby.family_id, user_id=other_user.id, role="member")
    db.add(fu)
    db.commit()

    # 認証モック
    def mock_get_current_user():
        return other_user
    
    def mock_get_current_family():
        return test_baby.family

    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[get_current_family] = mock_get_current_family
    # admin_required はオーバーライドしない -> 本来の実装が走る

    response = await client.post(f"/babies/{test_baby.id}/delete", follow_redirects=False)

    # PermissionDenied例外が発生し、例外ハンドラが 303 Redirect (/dashboard) を返すはず
    assert response.status_code == 303
    assert response.headers["location"] == "/dashboard"
    
    # 削除されていないこと
    baby = db.query(Baby).filter(Baby.id == test_baby.id).first()
    assert baby is not None
