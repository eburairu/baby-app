"""権限サービス"""
from sqlalchemy.orm import Session
from app.models.baby_permission import BabyPermission
from app.models.family_user import FamilyUser


class PermissionService:
    """権限チェックと管理を行うサービス"""

    @staticmethod
    def can_view_baby_record(db: Session, user_id: int, family_id: int, baby_id: int, record_type: str) -> bool:
        """指定した赤ちゃん・記録タイプの閲覧権限があるか確認"""
        
        # 1. 管理者はすべて許可
        fu = db.query(FamilyUser).filter(
            FamilyUser.family_id == family_id,
            FamilyUser.user_id == user_id
        ).first()
        if fu and fu.role == "admin":
            return True

        # 2. 個別設定を確認
        permission = db.query(BabyPermission).filter(
            BabyPermission.user_id == user_id,
            BabyPermission.baby_id == baby_id,
            BabyPermission.record_type == record_type
        ).first()

        if permission:
            return permission.can_view

        # 3. 設定がない場合はデフォルト許可（ホワイトリスト方式）
        return True

    @staticmethod
    def get_user_permissions(db: Session, user_id: int, baby_id: int, family_id: int = None) -> dict:
        """ユーザーの特定の赤ちゃんに対するすべての記録タイプの権限を取得"""
        
        # 管理者チェック（family_idが提供されている場合）
        if family_id:
            fu = db.query(FamilyUser).filter(
                FamilyUser.family_id == family_id,
                FamilyUser.user_id == user_id
            ).first()
            if fu and fu.role == "admin":
                return {k: True for k in ['feeding', 'sleep', 'diaper', 'growth', 'schedule', 'contraction', 'basic_info']}

        permissions = db.query(BabyPermission).filter(
            BabyPermission.user_id == user_id,
            BabyPermission.baby_id == baby_id
        ).all()
        
        # デフォルトはすべてTrue
        result = {
            'feeding': True,
            'sleep': True,
            'diaper': True,
            'growth': True,
            'schedule': True,
            'contraction': True,
            'basic_info': True
        }
        
        for p in permissions:
            result[p.record_type] = p.can_view
            
        return result

    @staticmethod
    def update_permissions(db: Session, user_id: int, baby_id: int, permissions_dict: dict):
        """権限設定を更新"""
        for record_type, can_view in permissions_dict.items():
            permission = db.query(BabyPermission).filter(
                BabyPermission.user_id == user_id,
                BabyPermission.baby_id == baby_id,
                BabyPermission.record_type == record_type
            ).first()

            if permission:
                permission.can_view = can_view
            else:
                new_permission = BabyPermission(
                    user_id=user_id,
                    baby_id=baby_id,
                    record_type=record_type,
                    can_view=can_view
                )
                db.add(new_permission)
        
        db.commit()
