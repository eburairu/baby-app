"""認証サービス"""
from passlib.context import CryptContext

# パスワードハッシュ化コンテキスト
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """認証関連のビジネスロジック"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """パスワード検証"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """パスワードハッシュ化"""
        return pwd_context.hash(password)
