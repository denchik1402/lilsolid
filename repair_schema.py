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
        if _add_column_if_missing('device_model', 'sort_order', 'sort_order INTEGER DEFAULT 0'):
            changed += 1
        if _add_column_if_missing('device_model', 'image_alt', 'image_alt VARCHAR(200)'):
            changed += 1
        if _add_column_if_missing('device_model', 'meta_description', 'meta_description VARCHAR(300)'):
            changed += 1
        if _add_column_if_missing('device_model', 'meta_keywords', 'meta_keywords VARCHAR(300)'):
            changed += 1
        if 'device_model' not in tables:
            db.create_all()
            print('[repair] created device_model table')
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

        for col, ddl in (
            ('slug', 'slug VARCHAR(200)'),
            ('image_alt', 'image_alt VARCHAR(200)'),
            ('meta_description', 'meta_description VARCHAR(300)'),
            ('meta_keywords', 'meta_keywords VARCHAR(300)'),
            ('old_price', 'old_price FLOAT'),
            ('cost', 'cost FLOAT'),
            ('images', 'images TEXT'),
            ('model', 'model VARCHAR(50)'),
            ('color', 'color VARCHAR(50)'),
            ('views', 'views INTEGER DEFAULT 0'),
            ('is_hit', 'is_hit BOOLEAN DEFAULT 0'),
            ('is_exclusive', 'is_exclusive BOOLEAN DEFAULT 0'),
            ('in_stock', 'in_stock BOOLEAN DEFAULT 1'),
            ('characteristics', 'characteristics TEXT'),
            ('description', 'description TEXT'),
            ('updated_at', 'updated_at DATETIME'),
            ('created_at', 'created_at DATETIME'),
            ('category_id', 'category_id INTEGER'),
        ):
            if _add_column_if_missing('product', col, ddl):
                changed += 1

        for col, ddl in (
            ('slug', 'slug VARCHAR(100)'),
            ('meta_description', 'meta_description VARCHAR(300)'),
            ('meta_keywords', 'meta_keywords VARCHAR(300)'),
            ('image', 'image VARCHAR(200)'),
            ('description', 'description TEXT'),
            ('created_at', 'created_at DATETIME'),
            ('updated_at', 'updated_at DATETIME'),
        ):
            if _add_column_if_missing('category', col, ddl):
                changed += 1

        for col, ddl in (
            ('sort_order', 'sort_order INTEGER DEFAULT 0'),
            ('is_active', 'is_active BOOLEAN DEFAULT 1'),
            ('title', 'title VARCHAR(200)'),
            ('subtitle', 'subtitle VARCHAR(300)'),
            ('link_url', 'link_url VARCHAR(300)'),
            ('image', 'image VARCHAR(200)'),
        ):
            if _add_column_if_missing('banner', col, ddl):
                changed += 1

        for col, ddl in (
            ('created_at', 'created_at DATETIME'),
            ('product_id', 'product_id INTEGER'),
            ('rating', 'rating INTEGER DEFAULT 5'),
            ('text', 'text TEXT'),
            ('author_name', 'author_name VARCHAR(100)'),
        ):
            if _add_column_if_missing('review', col, ddl):
                changed += 1

        for col, ddl in (
            ('title', 'title VARCHAR(200)'),
            ('subtitle', 'subtitle VARCHAR(300)'),
            ('link_url', 'link_url VARCHAR(300)'),
            ('image', 'image VARCHAR(200)'),
            ('position', 'position INTEGER DEFAULT 0'),
            ('is_active', 'is_active BOOLEAN DEFAULT 1'),
        ):
            if _add_column_if_missing('home_block', col, ddl):
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
