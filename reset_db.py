"""データベースリセットスクリプト"""
import sys
import os

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
# 全てのモデルをインポートして Base.metadata に登録
from app.models.user import User
from app.models.family import Family
from app.models.family_user import FamilyUser
from app.models.baby import Baby
from app.models.feeding import Feeding
from app.models.sleep import Sleep
from app.models.diaper import Diaper
from app.models.growth import Growth
from app.models.schedule import Schedule
from app.models.contraction import Contraction
from app.models.session import UserSession

def reset_database():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Database reset and initialization complete.")

if __name__ == "__main__":
    reset_database()
