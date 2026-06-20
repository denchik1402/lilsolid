#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка и восстановление схемы БД после деплоя.
Добавляет отсутствующие таблицы/колонки.
"""
import sys

from sqlalchemy import inspect, text

from app import app
from extensions import db


def _table_columns(insp, table: str) -> set[str]:
    if table not in insp.get_table_names():
        return set()
    return {c['name'] for c in insp.get_columns(table)}


def _sql_table(table: str) -> str:
    return f'"{table}"' if table == 'order' else table


def _add_column_if_missing(table: str, column: str, ddl: str) -> bool:
    insp = inspect(db.engine)
    if table not in insp.get_table_names():
        return False
    if column in _table_columns(insp, table):
        return False
    db.session.execute(text(f'ALTER TABLE {_sql_table(table)} ADD COLUMN {ddl}'))
    print(f'[repair] ADD COLUMN {table}.{column}')
    return True


def repair() -> int:
    changed = 0
    with app.app_context():
        insp = inspect(db.engine)
        tables = set(insp.get_table_names())

        if 'blog_post' not in tables:
            db.create_all()
            insp = inspect(db.engine)
            tables = set(insp.get_table_names())
            if 'blog_post' in tables:
                print('[repair] created missing tables via create_all()')
                changed += 1

        if _add_column_if_missing('blog_post', 'cover_image', 'cover_image VARCHAR(300)'):
            changed += 1

        if _add_column_if_missing('device_model', 'slug', 'slug VARCHAR(100)'):
            changed += 1
        if _add_column_if_missing('device_model', 'seo_text', 'seo_text TEXT'):
            changed += 1

        for col, ddl in (
            ('promo_code', 'promo_code VARCHAR(50)'),
            ('discount_amount', 'discount_amount FLOAT DEFAULT 0'),
            ('courier_telegram_id', 'courier_telegram_id BIGINT'),
            ('status', "status VARCHAR(50) DEFAULT 'new'"),
        ):
            if _add_column_if_missing('order', col, ddl):
                changed += 1

        for col, ddl in (
            ('impressions', 'impressions INTEGER DEFAULT 0'),
            ('clicks', 'clicks INTEGER DEFAULT 0'),
            ('ab_test_group', 'ab_test_group VARCHAR(50)'),
            ('badge_type', 'badge_type VARCHAR(20)'),
            ('product_id', 'product_id INTEGER'),
        ):
            if _add_column_if_missing('banner', col, ddl):
                changed += 1

        if _add_column_if_missing('product', 'is_hit', 'is_hit BOOLEAN DEFAULT 0'):
            changed += 1

        if 'home_block' not in tables:
            db.create_all()
            print('[repair] created home_block table')
            changed += 1

        if _add_column_if_missing('review', 'status', "status VARCHAR(20) DEFAULT 'pending'"):
            changed += 1

        if 'bot_setting' not in tables or 'promo_code' not in tables:
            db.create_all()
            print('[repair] create_all() for missing tables (bot_setting, promo_code, …)')
            changed += 1

        if _add_column_if_missing('order', 'idempotency_key', 'idempotency_key VARCHAR(64)'):
            changed += 1
        try:
            db.session.execute(text(
                'CREATE UNIQUE INDEX IF NOT EXISTS ix_order_idempotency_key ON "order" (idempotency_key)'
            ))
        except Exception as e:
            print(f'[repair] idempotency index warning: {e}')

        db.session.commit()

        try:
            from alembic_runner import run_alembic
            run_alembic()
        except Exception as e:
            print(f'[repair] alembic upgrade warning: {e}')

    print(f'[repair] done, changes: {changed}')
    return 0


if __name__ == '__main__':
    sys.exit(repair())
