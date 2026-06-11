"""Device model slugs, blog_post table

Revision ID: 009
Revises: 008
Create Date: 2026-06-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '009'
down_revision: Union[str, None] = '008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('device_model', sa.Column('slug', sa.String(100), nullable=True))
    op.add_column('device_model', sa.Column('seo_text', sa.Text(), nullable=True))
    op.create_unique_constraint('uq_device_model_slug', 'device_model', ['slug'])

    op.create_table(
        'blog_post',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('slug', sa.String(120), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('excerpt', sa.String(400), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('meta_description', sa.String(300), nullable=True),
        sa.Column('meta_keywords', sa.String(300), nullable=True),
        sa.Column('cover_icon', sa.String(50), server_default='fa-book-open'),
        sa.Column('reading_minutes', sa.Integer(), server_default='5'),
        sa.Column('is_published', sa.Boolean(), server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('slug'),
    )


def downgrade() -> None:
    op.drop_table('blog_post')
    op.drop_constraint('uq_device_model_slug', 'device_model', type_='unique')
    op.drop_column('device_model', 'seo_text')
    op.drop_column('device_model', 'slug')
