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
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = set(inspector.get_table_names())

    # 1. users table
    if 'users' not in existing_tables:
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('email', sa.String(length=255), nullable=False),
            sa.Column('hashed_password', sa.String(length=255), nullable=False),
            sa.Column('full_name', sa.String(length=255), server_default='', nullable=True),
            sa.Column('is_active', sa.Boolean(), server_default=sa.true(), nullable=True),
            sa.Column('is_demo', sa.Boolean(), server_default=sa.false(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
        op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # 2. sync_metadata table
    if 'sync_metadata' not in existing_tables:
        op.create_table(
            'sync_metadata',
            sa.Column('id', sa.String(length=50), nullable=False),
            sa.Column('last_sync_time', sa.DateTime(), nullable=False),
            sa.Column('synced_by', sa.String(length=100), server_default='system', nullable=True),
            sa.Column('total_fetched', sa.Integer(), server_default='0', nullable=True),
            sa.Column('total_added', sa.Integer(), server_default='0', nullable=True),
            sa.Column('message', sa.String(length=500), server_default='', nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # 3. company_profiles table
    if 'company_profiles' not in existing_tables:
        op.create_table(
            'company_profiles',
            sa.Column('id', sa.String(length=100), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('logo', sa.String(length=500), server_default='', nullable=True),
            sa.Column('industry', sa.String(length=100), server_default='Technology', nullable=True),
            sa.Column('headquarters', sa.String(length=255), server_default='', nullable=True),
            sa.Column('locations', sa.Text(), server_default='[]', nullable=True),
            sa.Column('website', sa.String(length=500), server_default='', nullable=True),
            sa.Column('career_page', sa.String(length=500), server_default='', nullable=True),
            sa.Column('description', sa.Text(), server_default='', nullable=True),
            sa.Column('size', sa.String(length=100), server_default='10,000+ employees', nullable=True),
            sa.Column('founded_year', sa.Integer(), nullable=True),
            sa.Column('openings_count', sa.Integer(), server_default='0', nullable=True),
            sa.Column('is_featured', sa.Boolean(), server_default=sa.false(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_company_profiles_id'), 'company_profiles', ['id'], unique=False)
        op.create_index(op.f('ix_company_profiles_industry'), 'company_profiles', ['industry'], unique=False)
        op.create_index(op.f('ix_company_profiles_name'), 'company_profiles', ['name'], unique=False)

    # 4. job_listings table
    if 'job_listings' not in existing_tables:
        op.create_table(
            'job_listings',
            sa.Column('id', sa.String(length=100), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('company', sa.String(length=255), nullable=False),
            sa.Column('company_logo', sa.String(length=500), server_default='', nullable=True),
            sa.Column('company_id', sa.String(length=100), server_default='', nullable=True),
            sa.Column('location', sa.String(length=255), server_default='Remote', nullable=True),
            sa.Column('city', sa.String(length=100), server_default='', nullable=True),
            sa.Column('country', sa.String(length=100), server_default='Global', nullable=True),
            sa.Column('work_mode', sa.String(length=50), server_default='Remote', nullable=True),
            sa.Column('role_category', sa.String(length=100), server_default='Software Engineering', nullable=True),
            sa.Column('experience_level', sa.String(length=50), server_default='Mid-level', nullable=True),
            sa.Column('employment_type', sa.String(length=50), server_default='Full-time', nullable=True),
            sa.Column('salary_min', sa.Float(), nullable=True),
            sa.Column('salary_max', sa.Float(), nullable=True),
            sa.Column('salary_currency', sa.String(length=20), server_default='USD', nullable=True),
            sa.Column('salary_text', sa.String(length=100), server_default='', nullable=True),
            sa.Column('skills', sa.Text(), server_default='[]', nullable=True),
            sa.Column('description', sa.Text(), server_default='', nullable=True),
            sa.Column('url', sa.String(length=1000), server_default='', nullable=True),
            sa.Column('source', sa.String(length=100), server_default='Verified Career Portal', nullable=True),
            sa.Column('is_demo', sa.Boolean(), server_default=sa.false(), nullable=True),
            sa.Column('posted_date', sa.DateTime(), nullable=True),
            sa.Column('last_synced_at', sa.DateTime(), nullable=True),
            sa.Column('expires_at', sa.DateTime(), nullable=True),
            sa.Column('is_active', sa.Boolean(), server_default=sa.true(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_job_listings_id'), 'job_listings', ['id'], unique=False)
        op.create_index(op.f('ix_job_listings_title'), 'job_listings', ['title'], unique=False)
        op.create_index(op.f('ix_job_listings_company'), 'job_listings', ['company'], unique=False)
        op.create_index(op.f('ix_job_listings_company_id'), 'job_listings', ['company_id'], unique=False)
        op.create_index(op.f('ix_job_listings_work_mode'), 'job_listings', ['work_mode'], unique=False)
        op.create_index(op.f('ix_job_listings_role_category'), 'job_listings', ['role_category'], unique=False)
        op.create_index(op.f('ix_job_listings_experience_level'), 'job_listings', ['experience_level'], unique=False)
        op.create_index(op.f('ix_job_listings_employment_type'), 'job_listings', ['employment_type'], unique=False)
        op.create_index(op.f('ix_job_listings_posted_date'), 'job_listings', ['posted_date'], unique=False)
        op.create_index(op.f('ix_job_listings_is_active'), 'job_listings', ['is_active'], unique=False)
        op.create_index(op.f('ix_job_listings_is_demo'), 'job_listings', ['is_demo'], unique=False)
        op.create_index(op.f('ix_job_listings_last_synced_at'), 'job_listings', ['last_synced_at'], unique=False)
        op.create_index(op.f('ix_job_listings_expires_at'), 'job_listings', ['expires_at'], unique=False)
    else:
        # Table exists: check columns
        job_cols = {c['name'] for c in inspector.get_columns('job_listings')}
        with op.batch_alter_table('job_listings', schema=None) as batch_op:
            if 'is_demo' not in job_cols:
                batch_op.add_column(sa.Column('is_demo', sa.Boolean(), server_default=sa.false(), nullable=True))
                batch_op.create_index(batch_op.f('ix_job_listings_is_demo'), ['is_demo'], unique=False)
            if 'last_synced_at' not in job_cols:
                batch_op.add_column(sa.Column('last_synced_at', sa.DateTime(), nullable=True))
                batch_op.create_index(batch_op.f('ix_job_listings_last_synced_at'), ['last_synced_at'], unique=False)
            if 'expires_at' not in job_cols:
                batch_op.add_column(sa.Column('expires_at', sa.DateTime(), nullable=True))
                batch_op.create_index(batch_op.f('ix_job_listings_expires_at'), ['expires_at'], unique=False)

    # 5. analysis_records table
    if 'analysis_records' not in existing_tables:
        op.create_table(
            'analysis_records',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('candidate_name', sa.String(length=255), server_default='Unknown Candidate', nullable=True),
            sa.Column('candidate_email', sa.String(length=255), server_default='', nullable=True),
            sa.Column('candidate_phone', sa.String(length=100), server_default='', nullable=True),
            sa.Column('file_name', sa.String(length=255), server_default='resume.pdf', nullable=True),
            sa.Column('job_title', sa.String(length=255), server_default='Target Role', nullable=True),
            sa.Column('job_company', sa.String(length=255), server_default='Target Company', nullable=True),
            sa.Column('overall_score', sa.Float(), server_default='0.0', nullable=True),
            sa.Column('match_rating', sa.String(length=100), server_default='Needs Optimization', nullable=True),
            sa.Column('skills_score', sa.Float(), server_default='0.0', nullable=True),
            sa.Column('similarity_score', sa.Float(), server_default='0.0', nullable=True),
            sa.Column('section_score', sa.Float(), server_default='0.0', nullable=True),
            sa.Column('metrics_score', sa.Float(), server_default='0.0', nullable=True),
            sa.Column('extracted_skills', sa.Text(), server_default='[]', nullable=True),
            sa.Column('matching_skills', sa.Text(), server_default='[]', nullable=True),
            sa.Column('missing_skills', sa.Text(), server_default='[]', nullable=True),
            sa.Column('additional_skills', sa.Text(), server_default='[]', nullable=True),
            sa.Column('parsed_sections', sa.Text(), server_default='{}', nullable=True),
            sa.Column('recommendations', sa.Text(), server_default='[]', nullable=True),
            sa.Column('score_breakdown', sa.Text(), server_default='{}', nullable=True),
            sa.Column('raw_resume_text', sa.Text(), server_default='', nullable=True),
            sa.Column('raw_job_description', sa.Text(), server_default='', nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_analysis_records_created_at'), 'analysis_records', ['created_at'], unique=False)
        op.create_index(op.f('ix_analysis_records_id'), 'analysis_records', ['id'], unique=False)
        op.create_index(op.f('ix_analysis_records_user_id'), 'analysis_records', ['user_id'], unique=False)
    else:
        # Table exists: check if user_id column is missing
        ar_cols = {c['name'] for c in inspector.get_columns('analysis_records')}
        if 'user_id' not in ar_cols:
            with op.batch_alter_table('analysis_records', schema=None) as batch_op:
                batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
                batch_op.create_index(batch_op.f('ix_analysis_records_user_id'), ['user_id'], unique=False)
                batch_op.create_foreign_key('fk_analysis_records_user_id', 'users', ['user_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    # Safe downgrade: never drop tables with user records in production
    pass
