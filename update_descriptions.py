#!/usr/bin/env python3
"""Обновление описаний товаров в БД (без потери заказов и отзывов)."""
import sys
sys.path.insert(0, '.')

# Импортируем данные из full_update
from full_update import STICKS, DEVICES

def update_descriptions():
    from app import app, db
    from models import Product
    
    with app.app_context():
        updated = 0
        # Обновляем стики
        for stick in STICKS:
            p = Product.query.filter_by(name=stick['name']).first()
            if p:
                p.description = stick['description']
                updated += 1
        # Обновляем устройства
        for device in DEVICES:
            p = Product.query.filter_by(name=device['name']).first()
            if p:
                p.description = device['description']
                updated += 1
        db.session.commit()
        print(f"Обновлено описаний: {updated}")

if __name__ == '__main__':
    update_descriptions()
