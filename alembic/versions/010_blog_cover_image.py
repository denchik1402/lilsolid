"""Blog post cover image

Revision ID: 010
Revises: 009
Create Date: 2026-06-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from migration_helpers import column_exists, table_exists

revision: str = '010'
down_revision: Union[str, None] = '009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    if table_exists(conn, 'blog_post') and not column_exists(conn, 'blog_post', 'cover_image'):
        op.add_column('blog_post', sa.Column('cover_image', sa.String(300), nullable=True))


def downgrade() -> None:
    op.drop_column('blog_post', 'cover_image')
