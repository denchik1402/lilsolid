"""Rename ILUMA models, add gen-1 ILUMA line to device_model catalog.

Revision ID: 011
Revises: 010
"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
from sqlalchemy import text

revision: str = '011'
down_revision: Union[str, None] = '010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

RENAMES = [
    ('IQOS Iluma i One', 'IQOS ILUMA I ONE'),
    ('IQOS Iluma i Standart', 'IQOS ILUMA I'),
    ('IQOS Iluma i Standard', 'IQOS ILUMA I'),
    ('IQOS Iluma i Prime', 'IQOS ILUMA I PRIME'),
]

NEW_MODELS = [
    ('IQOS ILUMA ONE', 4),
    ('IQOS ILUMA PRIME', 5),
    ('IQOS ILUMA STANDART', 6),
]

SORT_ORDER = {
    'IQOS ILUMA I ONE': 1,
    'IQOS ILUMA I': 2,
    'IQOS ILUMA I PRIME': 3,
    'IQOS ILUMA ONE': 4,
    'IQOS ILUMA PRIME': 5,
    'IQOS ILUMA STANDART': 6,
    'LIL SOLID DUAL': 7,
    'LIL SOLID 3.0': 8,
    'LIL SOLID 4.0': 9,
}


def upgrade() -> None:
    conn = op.get_bind()
    now = datetime.utcnow()

    for old_name, new_name in RENAMES:
        conn.execute(
            text('UPDATE device_model SET name = :new WHERE name = :old'),
            {'old': old_name, 'new': new_name},
        )
        conn.execute(
            text('UPDATE product SET model = :new WHERE model = :old'),
            {'old': old_name, 'new': new_name},
        )

    for name, sort_order in NEW_MODELS:
        exists = conn.execute(
            text('SELECT id FROM device_model WHERE name = :name'),
            {'name': name},
        ).fetchone()
        if not exists:
            conn.execute(
                text(
                    'INSERT INTO device_model (name, sort_order, created_at) '
                    'VALUES (:name, :sort, :now)'
                ),
                {'name': name, 'sort': sort_order, 'now': now},
            )

    for name, sort_order in SORT_ORDER.items():
        conn.execute(
            text('UPDATE device_model SET sort_order = :sort WHERE name = :name'),
            {'sort': sort_order, 'name': name},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for name, _ in NEW_MODELS:
        conn.execute(text('DELETE FROM device_model WHERE name = :name'), {'name': name})
    reverse = [
        ('IQOS ILUMA I ONE', 'IQOS Iluma i One'),
        ('IQOS ILUMA I', 'IQOS Iluma i Standart'),
        ('IQOS ILUMA I PRIME', 'IQOS Iluma i Prime'),
    ]
    for new_name, old_name in reverse:
        conn.execute(
            text('UPDATE device_model SET name = :old WHERE name = :new'),
            {'old': old_name, 'new': new_name},
        )
        conn.execute(
            text('UPDATE product SET model = :old WHERE model = :new'),
            {'old': old_name, 'new': new_name},
        )
