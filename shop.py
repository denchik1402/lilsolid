#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Запуск приложения — алиас для app.py.
Используйте: py app.py  или  py shop.py
Основное приложение: app.py (полная версия с админкой, ботом, фильтрами).
"""
from app import app

if __name__ == '__main__':
    import os
    with app.app_context():
        from extensions import db
        from models import Category
        from app import (
            migrate_default_banners,
            migrate_special_banners,
            populate_product_colors,
            populate_promo_and_hits,
        )
        try:
            from alembic_runner import run_alembic
            run_alembic()
        except Exception:
        db.create_all()
        migrate_default_banners()
        migrate_special_banners()
        populate_product_colors()
        if Category.query.count() == 0:
            from create_test_data import create_test_data
            create_test_data()
        populate_promo_and_hits()

    debug = os.environ.get('FLASK_DEBUG', 'false').lower() in ('1', 'true', 'yes')
    app.run(debug=debug)
    