#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для присвоения цветов товарам на основе названий.
Цвета в формате фильтра каталога: Серый, Зеленый, Синий, Бежевый, Красный, Черный, Оранжевый, Фиолетовый, Желтый, Смешанный.
"""

import re
import os

# Маппинг: ключевые слова в названии/описании -> цвет (русский)
COLOR_MAP = [
    # Черный
    (r'\b(black|midnight black|чёрный|черный|black titan|чёрный титан)\b', 'Черный'),
    # Зеленый (до Синий, чтобы "Зелёный Кобальт" мапился на Зеленый)
    (r'\b(green|leaf green|aspen green|зелёный|зеленый|зелёный кобальт)\b', 'Зеленый'),
    # Синий
    (r'\b(blue|breeze blue|синий|turquoise|кобальт)\b', 'Синий'),
    # Красный
    (r'\b(red|garnet red|красн|медь|copper)\b', 'Красный'),
    # Фиолетовый
    (r'\b(violet|purple|фиолет|provience|provence)\b', 'Фиолетовый'),
    # Желтый
    (r'\b(yellow|gold|золот|золотой|sun|zing)\b', 'Желтый'),
    # Оранжевый
    (r'\b(amber|оранж)\b', 'Оранжевый'),
    # Бежевый / терракотовый
    (r'\b(terracotta|бежев|белый хром|white chrome)\b', 'Бежевый'),
    # Серый
    (r'\b(silver|серый|silver|grey|gray)\b', 'Серый'),
    # Смешанный (лимитированные, pearl, wave и т.д.)
    (r'\b(seletti|limited|anniversary|pearl|starling|twilight|tidal|wave)\b', 'Смешанный'),
]

def detect_color(name, description=''):
    """Определяет цвет по названию и описанию товара."""
    text = (name or '') + ' ' + (description or '')
    text = text.lower()
    for pattern, color in COLOR_MAP:
        if re.search(pattern, text, re.IGNORECASE):
            return color
    return None

def run():
    from app import app
    from models import Product

    with app.app_context():
        products = Product.query.all()
        updated = 0
        no_color = []
        for p in products:
            color = detect_color(p.name, p.description)
            if color:
                if p.color != color:
                    p.color = color
                    updated += 1
                    print(f"  {p.name[:50]} -> {color}")
            else:
                no_color.append(p.name)
        from extensions import db
        db.session.commit()
        print(f"\nОбновлено: {updated} из {len(products)} товаров")
        if no_color:
            print(f"\nБез цвета (не распознан): {no_color[0]}")

if __name__ == '__main__':
    run()
