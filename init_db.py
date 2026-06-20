#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Инициализация БД для продакшена (без запуска сервера). Схема — Alembic."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app import migrate_default_banners, migrate_special_banners, populate_promo_and_hits
from models import Category

with app.app_context():
    # Схема БД — Alembic
    try:
        from alembic_runner import run_alembic
        run_alembic()
    except Exception as e:
        print(f"Alembic: {e}, fallback: db.create_all()")
        db.create_all()
    migrate_default_banners()
    migrate_special_banners()
    if Category.query.count() == 0:
        try:
            import config
            site = getattr(config, 'SITE_URL', '') or ''
        except ImportError:
            site = ''
        if 'lilsolid.ru' in site:
            print("lilsolid.ru: пропуск тестовых данных (ожидается full_update).")
        else:
            from create_test_data import create_test_data
            create_test_data()
            print("Созданы тестовые данные.")
    populate_promo_and_hits()
    print("База данных инициализирована.")
