"""initial_schema_with_auth_and_sync

Revision ID: 9e330d3e9d9e
Revises: 
Create Date: 2026-11-13 19:34:36.107434

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '9e330d3e9d9e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create sync_metadata table if not exists
    op.create_table(
        'sync_metadata',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('last_sync_time', sa.DateTime(), nullable=False),
        sa.Column('synced_by', sa.String(length=100), nullable=True),
        sa.Column('total_fetched', sa.Integer(), nullable=True),
        sa.Column('total_added', sa.Integer(), nullable=True),
        sa.Column('message', sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_demo', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # 3. Batch alter analysis_records for SQLite/PostgreSQL portability
    with op.batch_alter_table('analysis_records', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_analysis_records_user_id'), ['user_id'], unique=False)
        batch_op.create_foreign_key('fk_analysis_records_user_id', 'users', ['user_id'], ['id'], ondelete='CASCADE')

    # 4. Batch alter job_listings
    with op.batch_alter_table('job_listings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_demo', sa.Boolean(), default=False, nullable=True))
        batch_op.add_column(sa.Column('last_synced_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('expires_at', sa.DateTime(), nullable=True))
        batch_op.create_index(batch_op.f('ix_job_listings_expires_at'), ['expires_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_job_listings_is_demo'), ['is_demo'], unique=False)
        batch_op.create_index(batch_op.f('ix_job_listings_last_synced_at'), ['last_synced_at'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('job_listings', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_job_listings_last_synced_at'))
        batch_op.drop_index(batch_op.f('ix_job_listings_is_demo'))
        batch_op.drop_index(batch_op.f('ix_job_listings_expires_at'))
        batch_op.drop_column('expires_at')
        batch_op.drop_column('last_synced_at')
        batch_op.drop_column('is_demo')

    with op.batch_alter_table('analysis_records', schema=None) as batch_op:
        batch_op.drop_constraint('fk_analysis_records_user_id', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_analysis_records_user_id'))
        batch_op.drop_column('user_id')

    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('sync_metadata')
