"""Initial migration

Revision ID: 001
Revises:
Create Date: 2026-02-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Feedings table
    op.create_table(
        'feedings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('feeding_time', sa.DateTime(), nullable=False),
        sa.Column('feeding_type', sa.Enum('BREAST', 'BOTTLE', 'MIXED', name='feedingtype'), nullable=False),
        sa.Column('amount_ml', sa.Float(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_feedings_id'), 'feedings', ['id'], unique=False)
    op.create_index(op.f('ix_feedings_feeding_time'), 'feedings', ['feeding_time'], unique=False)

    # Sleeps table
    op.create_table(
        'sleeps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sleeps_id'), 'sleeps', ['id'], unique=False)
    op.create_index(op.f('ix_sleeps_start_time'), 'sleeps', ['start_time'], unique=False)

    # Diapers table
    op.create_table(
        'diapers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('change_time', sa.DateTime(), nullable=False),
        sa.Column('diaper_type', sa.Enum('WET', 'DIRTY', 'BOTH', name='diapertype'), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_diapers_id'), 'diapers', ['id'], unique=False)
    op.create_index(op.f('ix_diapers_change_time'), 'diapers', ['change_time'], unique=False)

    # Growths table
    op.create_table(
        'growths',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('measurement_date', sa.Date(), nullable=False),
        sa.Column('weight_kg', sa.Float(), nullable=True),
        sa.Column('height_cm', sa.Float(), nullable=True),
        sa.Column('head_circumference_cm', sa.Float(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_growths_id'), 'growths', ['id'], unique=False)
    op.create_index(op.f('ix_growths_measurement_date'), 'growths', ['measurement_date'], unique=False)

    # Contractions table
    op.create_table(
        'contractions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('interval_seconds', sa.Integer(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contractions_id'), 'contractions', ['id'], unique=False)
    op.create_index(op.f('ix_contractions_start_time'), 'contractions', ['start_time'], unique=False)

    # Schedules table
    op.create_table(
        'schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('scheduled_time', sa.DateTime(), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_schedules_id'), 'schedules', ['id'], unique=False)
    op.create_index(op.f('ix_schedules_scheduled_time'), 'schedules', ['scheduled_time'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_schedules_scheduled_time'), table_name='schedules')
    op.drop_index(op.f('ix_schedules_id'), table_name='schedules')
    op.drop_table('schedules')
    op.drop_index(op.f('ix_contractions_start_time'), table_name='contractions')
    op.drop_index(op.f('ix_contractions_id'), table_name='contractions')
    op.drop_table('contractions')
    op.drop_index(op.f('ix_growths_measurement_date'), table_name='growths')
    op.drop_index(op.f('ix_growths_id'), table_name='growths')
    op.drop_table('growths')
    op.drop_index(op.f('ix_diapers_change_time'), table_name='diapers')
    op.drop_index(op.f('ix_diapers_id'), table_name='diapers')
    op.drop_table('diapers')
    op.drop_index(op.f('ix_sleeps_start_time'), table_name='sleeps')
    op.drop_index(op.f('ix_sleeps_id'), table_name='sleeps')
    op.drop_table('sleeps')
    op.drop_index(op.f('ix_feedings_feeding_time'), table_name='feedings')
    op.drop_index(op.f('ix_feedings_id'), table_name='feedings')
    op.drop_table('feedings')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
