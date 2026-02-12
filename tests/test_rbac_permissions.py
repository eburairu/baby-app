import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.family import Family
from app.models.family_user import FamilyUser
from app.models.baby import Baby
from app.models.baby_permission import BabyPermission
from app.models.session import UserSession
from app.services.permission_service import PermissionService

@pytest.mark.asyncio
async def test_dashboard_access_with_permissions(client: AsyncClient, db: Session):
    # Setup: Family, Admin, Baby
    family = Family(name="Test Family", invite_code="DASHBOARD_TEST")
    db.add(family)
    db.commit()

    user = User(username="member_user", hashed_password="hashed_password")
    db.add(user)
    db.commit()

    db.add(FamilyUser(family_id=family.id, user_id=user.id, role="member"))
    
    baby = Baby(family_id=family.id, name="Test Baby")
    db.add(baby)
    db.commit()

    # Create session
    session = UserSession(user_id=user.id, token="test_token", expires_at=UserSession.default_expires_at())
    db.add(session)
    db.commit()

    client.cookies.set("session_token", "test_token")

    # 1. Default access (should be allowed)
    response = await client.get("/dashboard")
    assert response.status_code == 200
    assert "Test Baby" in response.text

    # 2. Restrict basic_info (should result in 403 or redirect due to PermissionDenied)
    # Note: get_current_baby raises PermissionDenied if basic_info is restricted
    PermissionService.update_permissions(db, user.id, baby.id, {"basic_info": False})
    
    response = await client.get("/dashboard")
    # In app/main.py, PermissionDenied is handled and redirects to /families/settings
    assert response.status_code == 200 # Redirect followed by client fixture
    assert "/families/settings" in str(response.url)

    # 3. Restrict feeding but allow basic_info
    PermissionService.update_permissions(db, user.id, baby.id, {"basic_info": True, "feeding": False})
    
    response = await client.get("/dashboard")
    assert response.status_code == 200
    assert "Test Baby" in response.text
    # Should NOT see feeding list or quick link if template handles perms (which I added)
    assert "最新の授乳記録" not in response.text

    # 4. Check direct access to /feedings
    response = await client.get("/feedings")
    # Redirect to settings because feeding is restricted
    assert "/families/settings" in str(response.url)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_admin_bypass_permissions(client: AsyncClient, db: Session):
    # Setup: Admin
    family = Family(name="Admin Family", invite_code="ADMIN_TEST")
    db.add(family)
    db.commit()

    admin = User(username="admin_user", hashed_password="hashed_password")
    db.add(admin)
    db.commit()

    db.add(FamilyUser(family_id=family.id, user_id=admin.id, role="admin"))
    
    baby = Baby(family_id=family.id, name="Admin Baby")
    db.add(baby)
    db.commit()

    # Restrict feeding for admin (should be ignored)
    PermissionService.update_permissions(db, admin.id, baby.id, {"feeding": False})

    # Create session
    session = UserSession(user_id=admin.id, token="admin_token", expires_at=UserSession.default_expires_at())
    db.add(session)
    db.commit()

    client.cookies.set("session_token", "admin_token")

    response = await client.get("/dashboard")
    assert response.status_code == 200
    # Admin should see feeding regardless of settings
    assert "最新の授乳記録" in response.text

    response = await client.get("/feedings")
    assert response.status_code == 200
    assert "授乳記録" in response.text
