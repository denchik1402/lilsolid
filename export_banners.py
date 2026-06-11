# -*- coding: utf-8 -*-
"""
Экспорт баннеров из локальной БД в JSON.
Запускать локально: py export_banners.py
Создаёт файл banners_export.json для переноса на прод.
"""
import json
import sqlite3
import os

DB_PATH = 'shop.db'
OUTPUT = 'banners_export.json'

def export_banners():
    if not os.path.isfile(DB_PATH):
        print(f"Ошибка: {DB_PATH} не найден")
        return
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id, b.image, b.title, b.subtitle, b.button_text, b.button_url,
               b.product_id, b.badge_type, b.sort_order, b.is_active, b.ab_test_group,
               p.name as product_name
        FROM banner b
        LEFT JOIN product p ON b.product_id = p.id
        ORDER BY b.sort_order, b.id
    """)
    rows = cursor.fetchall()
    data = []
    for r in rows:
        item = {
            'image': r['image'],
            'title': r['title'],
            'subtitle': r['subtitle'],
            'button_text': r['button_text'],
            'button_url': r['button_url'],
            'product_name': r['product_name'] if r['product_name'] else None,
            'badge_type': r['badge_type'],
            'sort_order': r['sort_order'],
            'is_active': bool(r['is_active']),
            'ab_test_group': r['ab_test_group'],
        }
        data.append(item)
    conn.close()
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Экспортировано {len(data)} баннеров в {OUTPUT}")

if __name__ == '__main__':
    export_banners()
