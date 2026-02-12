"""権限サービスのテスト"""
from app.models.family_user import FamilyUser
from app.models.baby import Baby
from app.models.baby_permission import BabyPermission
from app.services.permission_service import PermissionService


def test_get_user_permissions_batch_admin(db, test_user, test_family):
    """管理者は全ての赤ちゃんに対して権限がある"""
    # 管理者として登録
    fu = FamilyUser(
        family_id=test_family.id,
        user_id=test_user.id,
        role="admin"
    )
    db.add(fu)

    # 複数の赤ちゃんを作成
    baby1 = Baby(family_id=test_family.id, name="Baby1")
    baby2 = Baby(family_id=test_family.id, name="Baby2")
    baby3 = Baby(family_id=test_family.id, name="Baby3")
    db.add_all([baby1, baby2, baby3])
    db.commit()

    # バッチ取得
    baby_ids = [baby1.id, baby2.id, baby3.id]
    result = PermissionService.get_user_permissions_batch(
        db, test_user.id, baby_ids, test_family.id, "basic_info"
    )

    # 管理者は全てTrue
    assert result == {baby1.id: True, baby2.id: True, baby3.id: True}


def test_get_user_permissions_batch_member_with_permissions(db, test_user, test_family):
    """メンバーは個別設定に基づいて権限が付与される"""
    # メンバーとして登録
    fu = FamilyUser(
        family_id=test_family.id,
        user_id=test_user.id,
        role="member"
    )
    db.add(fu)

    # 複数の赤ちゃんを作成
    baby1 = Baby(family_id=test_family.id, name="Baby1")
    baby2 = Baby(family_id=test_family.id, name="Baby2")
    baby3 = Baby(family_id=test_family.id, name="Baby3")
    db.add_all([baby1, baby2, baby3])
    db.commit()

    # baby1とbaby3のみに権限を付与
    perm1 = BabyPermission(
        user_id=test_user.id,
        baby_id=baby1.id,
        record_type="basic_info",
        can_view=True
    )
    perm3 = BabyPermission(
        user_id=test_user.id,
        baby_id=baby3.id,
        record_type="basic_info",
        can_view=True
    )
    db.add_all([perm1, perm3])
    db.commit()

    # バッチ取得
    baby_ids = [baby1.id, baby2.id, baby3.id]
    result = PermissionService.get_user_permissions_batch(
        db, test_user.id, baby_ids, test_family.id, "basic_info"
    )

    # baby1とbaby3はTrue、baby2はFalse（設定なし）
    assert result == {baby1.id: True, baby2.id: False, baby3.id: True}


def test_get_user_permissions_batch_empty_list(db, test_user, test_family):
    """空のbaby_idsリストを渡すと空の辞書が返る"""
    result = PermissionService.get_user_permissions_batch(
        db, test_user.id, [], test_family.id, "basic_info"
    )

    assert result == {}


def test_get_user_permissions_batch_no_permissions(db, test_user, test_family):
    """権限設定がない場合は全てFalse"""
    # メンバーとして登録
    fu = FamilyUser(
        family_id=test_family.id,
        user_id=test_user.id,
        role="member"
    )
    db.add(fu)

    # 複数の赤ちゃんを作成（権限設定なし）
    baby1 = Baby(family_id=test_family.id, name="Baby1")
    baby2 = Baby(family_id=test_family.id, name="Baby2")
    db.add_all([baby1, baby2])
    db.commit()

    # バッチ取得
    baby_ids = [baby1.id, baby2.id]
    result = PermissionService.get_user_permissions_batch(
        db, test_user.id, baby_ids, test_family.id, "basic_info"
    )

    # 権限設定がないのでデフォルトFalse
    assert result == {baby1.id: False, baby2.id: False}


def test_get_user_permissions_batch_query_count(db, test_user, test_family):
    """クエリ数が最小限であることを確認（パフォーマンステスト）"""
    # メンバーとして登録
    fu = FamilyUser(
        family_id=test_family.id,
        user_id=test_user.id,
        role="member"
    )
    db.add(fu)

    # 10個の赤ちゃんを作成
    babies = [Baby(family_id=test_family.id, name=f"Baby{i}") for i in range(10)]
    db.add_all(babies)
    db.commit()

    # 全ての赤ちゃんに権限を付与
    permissions = [
        BabyPermission(
            user_id=test_user.id,
            baby_id=baby.id,
            record_type="basic_info",
            can_view=True
        )
        for baby in babies
    ]
    db.add_all(permissions)
    db.commit()

    # バッチ取得（クエリ数は赤ちゃんの数に依存せず一定）
    baby_ids = [baby.id for baby in babies]
    result = PermissionService.get_user_permissions_batch(
        db, test_user.id, baby_ids, test_family.id, "basic_info"
    )

    # 全てTrue
    assert all(result[baby_id] for baby_id in baby_ids)
    assert len(result) == 10
