"""Add meta_description, meta_keywords to product

Revision ID: 002
Revises: 001
Create Date: 2025-03-02

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('product', sa.Column('meta_description', sa.String(300), nullable=True))
    op.add_column('product', sa.Column('meta_keywords', sa.String(300), nullable=True))


def downgrade() -> None:
    op.drop_column('product', 'meta_keywords')
    op.drop_column('product', 'meta_description')
