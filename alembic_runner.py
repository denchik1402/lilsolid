# -*- coding: utf-8 -*-
"""Запуск миграций Alembic. Поддерживает существующие БД (stamp) и новые (upgrade)."""
import os
import sys


def run_alembic():
    """Запускает Alembic: stamp для существующей БД, upgrade для новой."""
    from sqlalchemy import create_engine, text
    from app import app

    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if not os.path.isabs(db_path):
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_path)

    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    has_tables = False
    has_alembic = False

    try:
        with engine.connect() as conn:
            r = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='category'"
            ))
            has_tables = r.fetchone() is not None
            r = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'"
            ))
            if r.fetchone():
                r2 = conn.execute(text("SELECT version_num FROM alembic_version"))
                has_alembic = r2.fetchone() is not None
    except Exception as e:
        print(f"[Alembic] Проверка БД: {e}")
        has_tables = False
        has_alembic = False

    import alembic.config
    alembic_cfg = alembic.config.Config(os.path.join(os.path.dirname(__file__), 'alembic.ini'))
    alembic_cfg.set_main_option('sqlalchemy.url', app.config['SQLALCHEMY_DATABASE_URI'].replace('%', '%%'))

    if has_tables and not has_alembic:
        # Существующая БД без Alembic — помечаем как текущую версию
        from alembic import command
        command.stamp(alembic_cfg, 'head')
        print("[Alembic] Существующая БД: stamp head (миграции уже применены)")
    else:
        from alembic import command
        command.upgrade(alembic_cfg, 'head')
        print("[Alembic] upgrade head")


if __name__ == '__main__':
    run_alembic()
