# -*- coding: utf-8 -*-
"""
Обновляет поле images у товаров — собирает все изображения из папки товара.
Запускать после full_update.py, когда image содержит путь вида Devices/.../ или Sticks/.../
"""
import os
import json
import sqlite3

PRODUCTS_BASE = 'static/images/products'

def update_galleries():
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, image FROM product WHERE image LIKE '%/%'")
    rows = cursor.fetchall()
    updated = 0
    for pid, name, image_path in rows:
        folder = os.path.join(PRODUCTS_BASE, os.path.dirname(image_path))
        if not os.path.isdir(folder):
            continue
        files = sorted([f for f in os.listdir(folder) 
                       if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
        if not files:
            continue
        rel_dir = os.path.dirname(image_path).replace('\\', '/')
        all_paths = [f"{rel_dir}/{f}" for f in files]
        # Главное фото: если текущее не существует — берём первое из папки
        main_path = image_path
        main_full = os.path.join(PRODUCTS_BASE, image_path)
        if not os.path.isfile(main_full):
            main_path = all_paths[0]
        # Доп. изображения — все кроме основного
        extra = [p for p in all_paths if p != main_path]
        # Обновляем image (если битый) и images
        if main_path != image_path:
            cursor.execute("UPDATE product SET image = ?, images = ? WHERE id = ?", 
                          (main_path, json.dumps(extra), pid))
        else:
            cursor.execute("UPDATE product SET images = ? WHERE id = ?", 
                          (json.dumps(extra), pid))
        updated += 1
    conn.commit()
    conn.close()
    print(f"Обновлено галерей: {updated}")

if __name__ == "__main__":
    update_galleries()
