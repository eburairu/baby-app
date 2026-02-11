"""認証サービス"""
import bcrypt


class AuthService:
    """認証関連のビジネスロジック"""

    @staticmethod
    def _ensure_bytes(password: str) -> bytes:
        """パスワードをバイト列に変換し、72バイトに制限する。

        bcryptは最大72バイトまでしか受け付けないため、
        それを超える場合は切り詰める。
        """
        password_bytes = password.encode("utf-8")
        return password_bytes[:72]

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """パスワード検証"""
        password_bytes = AuthService._ensure_bytes(plain_password)
        return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))

    @staticmethod
    def get_password_hash(password: str) -> str:
        """パスワードハッシュ化"""
        password_bytes = AuthService._ensure_bytes(password)
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password_bytes, salt).decode("utf-8")
