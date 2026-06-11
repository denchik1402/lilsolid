#!/usr/bin/env python
"""Конвертирует существующие изображения товаров в WebP. Запуск: py convert_images_to_webp.py"""
import os
import sys

folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images', 'products')
if not os.path.isdir(folder):
    print("Папка не найдена:", folder)
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("Установите Pillow: pip install Pillow")
    sys.exit(1)

exts = ('.jpg', '.jpeg', '.png', '.gif')
converted = 0
for f in os.listdir(folder):
    base, ext = os.path.splitext(f)
    if ext.lower() not in exts:
        continue
    webp_path = os.path.join(folder, base + '.webp')
    if os.path.isfile(webp_path):
        continue
    img_path = os.path.join(folder, f)
    try:
        with Image.open(img_path) as img:
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGBA')
            else:
                img = img.convert('RGB')
            img.save(webp_path, 'WEBP', quality=85)
        converted += 1
        print("OK:", f, "->", base + '.webp')
    except Exception as e:
        print("Ошибка", f, ":", e)

print("Готово. Создано WebP:", converted)
