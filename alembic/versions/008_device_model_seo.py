"""Add SEO fields to device_model, fix LIL names, add LIL SOLID 4.0

Revision ID: 008
Revises: 007
Create Date: 2025-05-28

"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision: str = '008'
down_revision: Union[str, None] = '007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

RENAME_MODELS = [
    ('lil SOLID DUAL', 'LIL SOLID DUAL'),
    ('lil SOLID 3.0', 'LIL SOLID 3.0'),
]


def upgrade() -> None:
    op.add_column('device_model', sa.Column('image_alt', sa.String(200), nullable=True))
    op.add_column('device_model', sa.Column('meta_description', sa.String(300), nullable=True))
    op.add_column('device_model', sa.Column('meta_keywords', sa.String(300), nullable=True))

    conn = op.get_bind()
    for old_name, new_name in RENAME_MODELS:
        conn.execute(
            text('UPDATE device_model SET name = :new WHERE name = :old'),
            {'old': old_name, 'new': new_name},
        )
        conn.execute(
            text('UPDATE product SET model = :new WHERE model = :old'),
            {'old': old_name, 'new': new_name},
        )

    exists = conn.execute(
        text("SELECT id FROM device_model WHERE name = 'LIL SOLID 4.0'")
    ).fetchone()
    if not exists:
        conn.execute(
            text(
                "INSERT INTO device_model (name, sort_order, created_at) "
                "VALUES ('LIL SOLID 4.0', 6, :now)"
            ),
            {'now': datetime.utcnow()},
        )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(text("DELETE FROM device_model WHERE name = 'LIL SOLID 4.0'"))
    for old_name, new_name in RENAME_MODELS:
        conn.execute(
            text('UPDATE device_model SET name = :old WHERE name = :new'),
            {'old': old_name, 'new': new_name},
        )
        conn.execute(
            text('UPDATE product SET model = :old WHERE model = :new'),
            {'old': old_name, 'new': new_name},
        )
    op.drop_column('device_model', 'meta_keywords')
    op.drop_column('device_model', 'meta_description')
    op.drop_column('device_model', 'image_alt')
