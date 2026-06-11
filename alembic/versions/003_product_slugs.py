"""Fill product slugs for ЧПУ URLs

Revision ID: 003
Revises: 002
Create Date: 2025-03-02

"""
from typing import Sequence, Union
from alembic import op
from sqlalchemy import text
import re

revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _slugify(name):
    s = re.sub(r'[^\w\s-]', '', (name or '').lower())
    return re.sub(r'[-\s]+', '-', s).strip('-')[:180] or 'product'


def upgrade() -> None:
    conn = op.get_bind()
    rows = conn.execute(text("SELECT id, name, slug FROM product WHERE slug IS NULL OR slug = ''")).fetchall()
    for row in rows:
        pid, name, _ = row
        base = _slugify(name)
        slug = base
        n = 0
        while True:
            exists = conn.execute(text("SELECT 1 FROM product WHERE slug = :s AND id != :pid"), {"s": slug, "pid": pid}).fetchone()
            if not exists:
                break
            n += 1
            slug = f"{base}-{n}"
        conn.execute(text("UPDATE product SET slug = :s WHERE id = :pid"), {"s": slug, "pid": pid})


def downgrade() -> None:
    pass  # Не сбрасываем slug — данные сохраняются
