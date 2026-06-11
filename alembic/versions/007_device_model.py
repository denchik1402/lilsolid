"""Add device_model table

Revision ID: 007
Revises: 006
Create Date: 2025-05-28

"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa

revision: str = '007'
down_revision: Union[str, None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEFAULT_MODELS = [
    ('IQOS Iluma i One', 1),
    ('IQOS Iluma i Standart', 2),
    ('IQOS Iluma i Prime', 3),
    ('LIL SOLID DUAL', 4),
    ('LIL SOLID 3.0', 5),
    ('LIL SOLID 4.0', 6),
]


def upgrade() -> None:
    op.create_table(
        'device_model',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('sort_order', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('name'),
    )
    now = datetime.utcnow()
    device_model = sa.table(
        'device_model',
        sa.column('name', sa.String),
        sa.column('sort_order', sa.Integer),
        sa.column('created_at', sa.DateTime),
    )
    op.bulk_insert(
        device_model,
        [{'name': n, 'sort_order': s, 'created_at': now} for n, s in DEFAULT_MODELS],
    )


def downgrade() -> None:
    op.drop_table('device_model')
