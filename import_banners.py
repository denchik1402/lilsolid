# -*- coding: utf-8 -*-
"""
Импорт баннеров из banners_export.json в локальную БД.
Запускать на проде: python3 import_banners.py
Добавляет только те баннеры, которых ещё нет (по имени файла image).
Существующие баннеры на проде не трогаются.
"""
import json
import sqlite3
import os

DB_PATH = 'shop.db'
INPUT = 'banners_export.json'


def import_banners():
    if not os.path.isfile(INPUT):
        print(f"Ошибка: {INPUT} не найден. Сначала запустите export_banners.py локально и скопируйте файл на сервер.")
        return
    if not os.path.isfile(DB_PATH):
        print(f"Ошибка: {DB_PATH} не найден")
        return

    with open(INPUT, 'r', encoding='utf-8') as f:
        data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Какие image уже есть на проде
    cursor.execute("SELECT image FROM banner")
    existing_images = {row[0] for row in cursor.fetchall()}

    # Словарь product_name -> id для маппинга
    cursor.execute("SELECT id, name FROM product")
    name_to_id = {row[1]: row[0] for row in cursor.fetchall()}

    added = 0
    skipped = 0

    for item in data:
        img = item.get('image')
        if not img:
            continue
        if img in existing_images:
            skipped += 1
            continue

        product_id = None
        if item.get('product_name'):
            product_id = name_to_id.get(item['product_name'])

        button_url = item.get('button_url')
        if button_url == 'None' or button_url == '':
            button_url = None

        cursor.execute("""
            INSERT INTO banner (image, title, subtitle, button_text, button_url,
                               product_id, badge_type, sort_order, is_active, ab_test_group)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            img,
            item.get('title', ''),
            item.get('subtitle'),
            item.get('button_text', 'Купить сейчас'),
            button_url,
            product_id,
            item.get('badge_type'),
            item.get('sort_order', 0),
            1 if item.get('is_active', True) else 0,
            item.get('ab_test_group'),
        ))
        existing_images.add(img)
        added += 1
        print(f"  + {item.get('title', img)}")

    conn.commit()
    conn.close()
    print(f"\nДобавлено: {added}, пропущено (уже есть): {skipped}")


if __name__ == '__main__':
    import_banners()
