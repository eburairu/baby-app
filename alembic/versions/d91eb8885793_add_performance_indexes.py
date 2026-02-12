"""add performance indexes

Revision ID: d91eb8885793
Revises: 162383dfc515
Create Date: 2026-02-12 17:15:25.187870

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd91eb8885793'
down_revision: Union[str, None] = '162383dfc515'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 権限チェック用の複合インデックス
    # user_id, baby_id, record_type の組み合わせでの検索を高速化
    op.create_index(
        'idx_baby_permissions_user_baby_type',
        'baby_permissions',
        ['user_id', 'baby_id', 'record_type'],
        unique=False
    )

    # 家族ユーザー用の複合インデックス
    # family_id, user_id の組み合わせでの検索を高速化（管理者チェック用）
    op.create_index(
        'idx_family_users_family_user',
        'family_users',
        ['family_id', 'user_id'],
        unique=False
    )

    # 睡眠記録用のインデックス（baby_id + start_time 降順）
    # 最新の睡眠記録取得を高速化
    op.create_index(
        'idx_sleep_baby_start_time',
        'sleeps',
        ['baby_id', sa.text('start_time DESC')],
        unique=False,
        postgresql_using='btree'
    )

    # 授乳記録用のインデックス（baby_id + feeding_time 降順）
    # 最新の授乳記録取得を高速化
    op.create_index(
        'idx_feeding_baby_time',
        'feedings',
        ['baby_id', sa.text('feeding_time DESC')],
        unique=False,
        postgresql_using='btree'
    )

    # おむつ記録用のインデックス（baby_id + change_time 降順）
    # 最新のおむつ記録取得を高速化
    op.create_index(
        'idx_diaper_baby_time',
        'diapers',
        ['baby_id', sa.text('change_time DESC')],
        unique=False,
        postgresql_using='btree'
    )


def downgrade() -> None:
    # インデックスを削除（逆順で削除）
    op.drop_index('idx_diaper_baby_time', table_name='diapers')
    op.drop_index('idx_feeding_baby_time', table_name='feedings')
    op.drop_index('idx_sleep_baby_start_time', table_name='sleeps')
    op.drop_index('idx_family_users_family_user', table_name='family_users')
    op.drop_index('idx_baby_permissions_user_baby_type', table_name='baby_permissions')
