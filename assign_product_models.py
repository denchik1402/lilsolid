#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для присвоения моделей устройствам на основе названий.
Модели должны совпадать с DEVICE_MODELS в app.py.
"""

import re

# Маппинг: ключевые слова в названии -> модель (порядок важен — более специфичные первыми)
MODEL_MAP = [
    # lil SOLID DUAL (до lil SOLID 3.0)
    (r'\blil\s+solid\s+dual\b', 'lil SOLID DUAL'),
    (r'\bsolid\s+dual\b', 'lil SOLID DUAL'),
    # lil SOLID 3.0
    (r'\blil\s+solid\s+3\.0\b', 'lil SOLID 3.0'),
    (r'\bsolid\s+3\.0\b', 'lil SOLID 3.0'),
    # IQOS Iluma i Prime
    (r'\bi\s+prime\b', 'IQOS Iluma i Prime'),
    (r'\biluma\s+i\s+prime\b', 'IQOS Iluma i Prime'),
    (r'\biluma\s+i\s+standart\s+seletti\b', 'IQOS Iluma i Standart'),  # Seletti — Standart, не Prime
    # IQOS Iluma i Standart (включая опечатку Standard)
    (r'\bi\s+standart\b', 'IQOS Iluma i Standart'),
    (r'\bi\s+standard\b', 'IQOS Iluma i Standart'),
    (r'\biluma\s+i\s+standart\b', 'IQOS Iluma i Standart'),
    # IQOS Iluma i One
    (r'\bi\s+one\b', 'IQOS Iluma i One'),
    (r'\biluma\s+i\s+one\b', 'IQOS Iluma i One'),
]


def detect_model(name, description=''):
    """Определяет модель по названию и описанию товара."""
    text = (name or '') + ' ' + (description or '')
    text = text.lower()
    for pattern, model in MODEL_MAP:
        if re.search(pattern, text, re.IGNORECASE):
            return model
    return None


def run():
    from app import app
    from models import Product
    from extensions import db

    with app.app_context():
        products = Product.query.all()
        updated = 0
        no_model = []
        for p in products:
            model = detect_model(p.name, p.description)
            if model:
                if p.model != model:
                    p.model = model
                    updated += 1
                    print(f"  {p.name[:55]} -> {model}")
            else:
                no_model.append(p.name)
        db.session.commit()
        print(f"\nОбновлено: {updated} из {len(products)} товаров")
        if no_model:
            print(f"\nБез модели (не распознаны):")
            for n in no_model[:15]:
                print(f"  - {n}")
            if len(no_model) > 15:
                print(f"  ... и ещё {len(no_model) - 15}")


if __name__ == '__main__':
    run()
