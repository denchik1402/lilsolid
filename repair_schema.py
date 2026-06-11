#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка и восстановление схемы БД после деплоя.
Добавляет отсутствующие таблицы/колонки (blog_post, cover_image, slug моделей).
"""
import sys

from sqlalchemy import inspect, text

from app import app
from extensions import db


def _table_columns(insp, table: str) -> set[str]:
    if table not in insp.get_table_names():
        return set()
    return {c['name'] for c in insp.get_columns(table)}


def _add_column_if_missing(table: str, column: str, ddl: str) -> bool:
    insp = inspect(db.engine)
    if table not in insp.get_table_names():
        return False
    if column in _table_columns(insp, table):
        return False
    db.session.execute(text(f'ALTER TABLE {table} ADD COLUMN {ddl}'))
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
