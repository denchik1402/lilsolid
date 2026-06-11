"""Add image_alt to product

Revision ID: 006
Revises: 005
Create Date: 2025-03-02

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('product', sa.Column('image_alt', sa.String(200), nullable=True))


def downgrade() -> None:
    op.drop_column('product', 'image_alt')
