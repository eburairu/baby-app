"""テスト共通設定・Fixture

TEST_DATABASE_URL 環境変数でPostgreSQLを使用可能。
未設定時はSQLiteインメモリにフォールバック。

使用例:
  # SQLiteモード（デフォルト）
  pytest tests/ -v

  # PostgreSQLモード
  TEST_DATABASE_URL=postgresql://user:pass@localhost:5433/baby_app_test pytest tests/ -v
"""
import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.user import User
from app.models.family import Family
from app.models.family_user import FamilyUser
from app.models.baby import Baby
# すべてのモデルをインポート（テーブル作成のため）
from app.models import (  # noqa: F401
    UserSession, Feeding, Sleep, Diaper, Growth, Schedule, Contraction,
)

# テスト用データベースURL
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    # デフォルトでDocker ComposeのDBを指す（開発体験向上）
    TEST_DATABASE_URL = "postgresql://test_user:test_password@localhost:5433/baby_app_test"

# PostgreSQL接続
_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
_TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=_engine
)


@pytest.fixture(scope="function")
def db():
    """テスト用データベースセッション。

    各テスト関数ごとにテーブルを作成・破棄して分離を保証。
    """
    # テーブル作成
    Base.metadata.create_all(bind=_engine)

    session = _TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # テーブル削除（テスト間の分離 - PostgreSQL用）
        with _engine.connect() as conn:
            conn.execute(text(
                "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
            ))
            conn.commit()


@pytest.fixture
def test_user(db):
    """テスト用ユーザーを作成して返す。"""
    user = User(username="testuser", hashed_password="hashed_password")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_baby(db, test_user):
    """テスト用の赤ちゃんを作成して返す。

    Family → FamilyUser → Baby のリレーションを構築。
    """
    family = Family(name="テスト家族", invite_code="TEST1234")
    db.add(family)
    db.commit()
    db.refresh(family)

    family_user = FamilyUser(
        family_id=family.id, user_id=test_user.id, role="admin"
    )
    db.add(family_user)
    db.commit()

    baby = Baby(family_id=family.id, name="テスト赤ちゃん")
    db.add(baby)
    db.commit()
    db.refresh(baby)
    return baby
