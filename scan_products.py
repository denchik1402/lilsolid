# -*- coding: utf-8 -*-
"""Сканирует папки products и выводит маппинг product_name -> image_path"""
import os
import json

base = 'static/images/products'
result = {}

for root, dirs, files in os.walk(base):
    rel = os.path.relpath(root, base)
    if rel == '.':
        continue
    imgs = sorted([f for f in files if f.lower().endswith(('.jpg','.jpeg','.png','.webp'))])
    if not imgs:
        continue
    path = rel.replace('\\', '/') + '/' + imgs[0]
    folder_name = os.path.basename(root)
    result[folder_name] = path

# Сохраняем в JSON для использования
with open('product_images_map.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("Маппинг сохранён в product_images_map.json")
for k, v in sorted(result.items()):
    print(f"  {k!r} -> {v!r}")
