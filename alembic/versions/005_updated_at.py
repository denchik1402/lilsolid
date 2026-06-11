"""Add updated_at to product and category for sitemap lastmod

Revision ID: 005
Revises: 004
Create Date: 2025-03-02

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('product', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.add_column('category', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.execute(sa.text("UPDATE product SET updated_at = created_at WHERE updated_at IS NULL"))
    op.execute(sa.text("UPDATE category SET updated_at = created_at WHERE updated_at IS NULL"))


def downgrade() -> None:
    op.drop_column('category', 'updated_at')
    op.drop_column('product', 'updated_at')
