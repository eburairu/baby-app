import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.family import Family
from app.models.family_user import FamilyUser
from app.models.baby import Baby
from app.models.session import UserSession
from app.services.permission_service import PermissionService

@pytest.mark.asyncio
async def test_update_basic_info_permission_bug(client: AsyncClient, db: Session):
    # Setup: Family, Admin, Member, Baby
    family = Family(name="Test Family", invite_code="BUG_TEST")
    db.add(family)
    db.commit()

    admin = User(username="admin_user", hashed_password="hashed_password")
    member = User(username="member_user", hashed_password="hashed_password")
    db.add(admin)
    db.add(member)
    db.commit()

    db.add(FamilyUser(family_id=family.id, user_id=admin.id, role="admin"))
    db.add(FamilyUser(family_id=family.id, user_id=member.id, role="member"))
    
    baby = Baby(family_id=family.id, name="Test Baby")
    db.add(baby)
    db.commit()

    # Create admin session
    session = UserSession(user_id=admin.id, token="admin_token", expires_at=UserSession.default_expires_at())
    db.add(session)
    db.commit()

    client.cookies.set("session_token", "admin_token")

    # CSRFトークンを取得
    res = await client.get("/families/settings")
    csrf_token = res.cookies.get("csrf_token")
    client.cookies.set("csrf_token", csrf_token)

    # 初期状態では権限なしを確認
    perms = PermissionService.get_user_permissions(db, member.id, baby.id)
    assert perms["basic_info"] is False

    # 権限更新リクエストを送信 (basic_info を True に)
    # フォームデータのキーは perm_{baby_id}_{record_type}
    response = await client.post(
        f"/families/members/{member.id}/permissions",
        data={
            f"perm_{baby.id}_basic_info": "on",
            f"perm_{baby.id}_feeding": "on",
            "csrf_token": csrf_token
        },
        follow_redirects=True
    )
    assert response.status_code == 200

    # 結果を確認
    db.expire_all()
    new_perms = PermissionService.get_user_permissions(db, member.id, baby.id)
    
    # feeding は "_" が1つなので更新されるはず
    assert new_perms["feeding"] is True
    
    # basic_info は "_" が2つあるため、バグにより更新されない（Falseのまま）はず
    # これが True になればバグが修正されたことになる
    assert new_perms["basic_info"] is True, "basic_info permission should be True after update"
