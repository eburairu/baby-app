"""SQLAlchemy データベース設定"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# データベースエンジン作成
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 接続の健全性チェック
    echo=settings.ENVIRONMENT == "development"  # 開発環境でSQLログ出力
)

# セッションファクトリ
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ベースクラス
Base = declarative_base()


def get_db():
    """データベースセッション依存性"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
