"""テストデータ作成スクリプト"""
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models.user import User
from app.models.family import Family
from app.models.family_user import FamilyUser
from app.models.baby import Baby
from app.models.feeding import Feeding, FeedingType
from app.services.auth_service import AuthService
from app.utils.time import get_now_naive

def create_test_data():
    db = SessionLocal()
    try:
        # 1. ユーザー作成
        user = User(
            username="testuser",
            hashed_password=AuthService.get_password_hash("password123")
        )
        db.add(user)
        db.flush()

        # 2. 家族作成
        family = Family(
            name="佐藤家",
            invite_code="TEST-CODE"
        )
        db.add(family)
        db.flush()

        # 3. 家族メンバー登録
        fu = FamilyUser(
            family_id=family.id,
            user_id=user.id,
            role="admin"
        )
        db.add(fu)

        # 4. 赤ちゃん登録
        baby = Baby(
            family_id=family.id,
            name="はなちゃん",
            birthday=date(2025, 1, 1)
        )
        db.add(baby)
        db.flush()

        # 5. 授乳記録作成
        feeding = Feeding(
            baby_id=baby.id,
            user_id=user.id,
            feeding_time=get_now_naive(),
            feeding_type=FeedingType.BREAST,
            duration_minutes=15
        )
        db.add(feeding)

        db.commit()
        print("Test data created successfully!")
        print(f"Username: testuser / Password: password123")
        print(f"Family: {family.name} (Invite Code: {family.invite_code})")
        print(f"Baby: {baby.name}")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()
