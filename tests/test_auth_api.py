import pytest
from app.models.user import User
from app.services.auth_service import AuthService
from app.config import settings

async def get_csrf_token(client):
    # GET /login was removed, use /api/health or similar to get cookie
    # But wait, CSRF middleware sets cookie on any response.
    # Let's use /api/health
    response = await client.get("/api/health")
    return response.cookies["csrf_token"]

@pytest.mark.asyncio
async def test_login_success(client, db):
    # Setup user
    password = "password123"
    hashed_password = AuthService.get_password_hash(password)
    user = User(username="testuser_login", hashed_password=hashed_password)
    db.add(user)
    db.commit()

    # Get CSRF token
    csrf_token = await get_csrf_token(client)
    headers = {"X-CSRF-Token": csrf_token}

    # Test login
    response = await client.post(
        "/api/login",
        json={"username": "testuser_login", "password": password},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Login successful"
    assert data["user"]["username"] == "testuser_login"
    assert "session_token" in response.cookies

@pytest.mark.asyncio
async def test_login_failure(client, db):
    csrf_token = await get_csrf_token(client)
    headers = {"X-CSRF-Token": csrf_token}

    response = await client.post(
        "/api/login",
        json={"username": "nonexistent", "password": "password"},
        headers=headers
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "ユーザー名またはパスワードが正しくありません"

@pytest.mark.asyncio
async def test_register_success(client, db):
    # Setup invite code
    settings.SYSTEM_INVITE_CODE = "SYS123"
    
    csrf_token = await get_csrf_token(client)
    headers = {"X-CSRF-Token": csrf_token}

    response = await client.post(
        "/api/register",
        json={
            "username": "newuser",
            "password": "password123",
            "invite_code": "SYS123"
        },
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Registration successful"
    assert data["user"]["username"] == "newuser"
    assert "session_token" in response.cookies

    # Verify user in DB
    user = db.query(User).filter(User.username == "newuser").first()
    assert user is not None

@pytest.mark.asyncio
async def test_register_honeypot(client):
    csrf_token = await get_csrf_token(client)
    headers = {"X-CSRF-Token": csrf_token}

    response = await client.post(
        "/api/register",
        json={
            "username": "botuser",
            "password": "password123",
            "invite_code": "SYS123",
            "email_confirm_hidden": "I am a bot"
        },
        headers=headers
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Bot detected"

@pytest.mark.asyncio
async def test_register_invalid_invite_code(client):
    csrf_token = await get_csrf_token(client)
    headers = {"X-CSRF-Token": csrf_token}

    response = await client.post(
        "/api/register",
        json={
            "username": "failuser",
            "password": "password123",
            "invite_code": "INVALID"
        },
        headers=headers
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "無効な招待コードです。管理者からコードを取得してください。"

@pytest.mark.asyncio
async def test_logout(client):
    # Login first (or set cookie manually)
    response = await client.get("/api/logout")
    # Actually checking cookie deletion might be tricky with AsyncClient without wrapper
    # But we can check response
    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"
    # Check that session_token is empty or expired in cookies if possible
    # (implementation dependent on how client handles cookies)
