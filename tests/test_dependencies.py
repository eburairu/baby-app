import pytest
from fastapi import Request
from sqlalchemy.orm import Session
from app.dependencies import get_current_baby, get_current_user
from app.models.user import User
from app.models.family import Family
from app.models.family_user import FamilyUser
from app.models.baby import Baby
from app.models.session import UserSession

@pytest.mark.asyncio
async def test_get_current_baby_dependency_logic(db: Session):
    # Setup
    family = Family(name="Dep Family", invite_code="DEPTEST")
    db.add(family)
    db.commit()

    user = User(username="dep_user", hashed_password="hashed_password")
    db.add(user)
    db.commit()

    db.add(FamilyUser(family_id=family.id, user_id=user.id, role="member"))
    
    baby = Baby(family_id=family.id, name="Dep Baby")
    db.add(baby)
    db.commit()

    session = UserSession(user_id=user.id, token="dep_token", expires_at=UserSession.default_expires_at())
    db.add(session)
    db.commit()

    # Mock Request
    class MockRequest:
        def __init__(self, cookies, method="GET"):
            self.cookies = cookies
            self.method = method
            self.headers = {}
        async def form(self):
            return {}

    request = MockRequest(cookies={"session_token": "dep_token"})
    
    # Test dependency functions directly
    # 1. get_current_user
    current_user = get_current_user(request=request, session_token="dep_token", db=db)
    assert current_user.id == user.id

    # 2. get_current_baby (This is where the NameError was)
    # Simulate FastAPI resolving the Query parameter
    res_baby = await get_current_baby(
        request=request,
        user=current_user,
        family=family,
        baby_id=None, # Passed as None, not Query(None)
        selected_baby_id=None,
        db=db
    )
    assert res_baby.id == baby.id
