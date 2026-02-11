"""家族管理サービス"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.family import Family
from app.models.family_user import FamilyUser
from app.models.user import User


class FamilyService:
    """家族関連のビジネスロジック"""

    @staticmethod
    def create_family(db: Session, user: User, name: str) -> Family:
        """新しい家族を作成し、作成者を管理者として登録"""
        family = Family(
            name=name,
            invite_code=Family.generate_invite_code()
        )
        db.add(family)
        db.flush()  # IDを確定させる

        # 作成者を管理者として追加
        family_user = FamilyUser(
            family_id=family.id,
            user_id=user.id,
            role="admin"
        )
        db.add(family_user)
        db.commit()
        db.refresh(family)
        return family

    @staticmethod
    def join_family(db: Session, user: User, invite_code: str) -> Optional[Family]:
        """招待コードを使用して家族に参加"""
        family = db.query(Family).filter(Family.invite_code == invite_code).first()
        if not family:
            return None

        # すでに参加していないかチェック
        existing = db.query(FamilyUser).filter(
            FamilyUser.family_id == family.id,
            FamilyUser.user_id == user.id
        ).first()
        
        if existing:
            return family

        # メンバーとして追加
        family_user = FamilyUser(
            family_id=family.id,
            user_id=user.id,
            role="member"
        )
        db.add(family_user)
        db.commit()
        return family

    @staticmethod
    def get_user_families(db: Session, user: User) -> List[Family]:
        """ユーザーが所属している家族一覧を取得"""
        return [fu.family for fu in user.families]

    @staticmethod
    def is_admin(db: Session, user_id: int, family_id: int) -> bool:
        """ユーザーがその家族の管理者かどうかを確認"""
        fu = db.query(FamilyUser).filter(
            FamilyUser.family_id == family_id,
            FamilyUser.user_id == user_id
        ).first()
        return fu is not None and fu.role == "admin"
