#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Синхронизация product.image с файлами в static/images/products/.
Поддерживает: Devices/Имя/, Sticks/Имя/, плоские имена из full_update, поиск по имени файла.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PRODUCTS_BASE = 'static/images/products'
IMG_EXT = ('.jpg', '.jpeg', '.png', '.webp', '.gif')


def _is_image(name: str) -> bool:
    return name.lower().endswith(IMG_EXT)


def _rel(path: str) -> str:
    return path.replace('\\', '/')


def _file_exists(rel: str) -> bool:
    return os.path.isfile(os.path.join(PRODUCTS_BASE, rel))


def _pick_first(folder: str) -> str | None:
    if not os.path.isdir(folder):
        return None
    files = sorted(f for f in os.listdir(folder) if _is_image(f))
    return files[0] if files else None


def _find_by_folder_name(product_name: str) -> str | None:
    for subdir in ('Devices', 'Sticks'):
        folder = os.path.join(PRODUCTS_BASE, subdir, product_name)
        first = _pick_first(folder)
        if first:
            return _rel(f'{subdir}/{product_name}/{first}')
    return None


def _find_by_basename(basename: str) -> str | None:
    if not basename:
        return None
    base_lower = basename.lower()
    stem = base_lower.rsplit('.', 1)[0] if '.' in base_lower else base_lower
    for root, _dirs, files in os.walk(PRODUCTS_BASE):
        for fname in files:
            if not _is_image(fname):
                continue
            fl = fname.lower()
            if fl == base_lower or fl.startswith(stem):
                return _rel(os.path.relpath(os.path.join(root, fname), PRODUCTS_BASE))
    return None


def resolve_image(product_name: str, current: str | None) -> str | None:
    if current:
        cur = current.strip().replace('\\', '/')
        if _file_exists(cur):
            return cur
        found = _find_by_basename(os.path.basename(cur))
        if found:
            return found

    found = _find_by_folder_name(product_name)
    if found:
        return found

    # Поиск папки без учёта регистра
    for subdir in ('Devices', 'Sticks'):
        sub_path = os.path.join(PRODUCTS_BASE, subdir)
        if not os.path.isdir(sub_path):
            continue
        name_lower = product_name.lower()
        for entry in os.listdir(sub_path):
            if entry.lower() == name_lower:
                first = _pick_first(os.path.join(sub_path, entry))
                if first:
                    return _rel(f'{subdir}/{entry}/{first}')
    return None


def main() -> int:
    from app import app, db
    from models import Product

    with app.app_context():
        updated = 0
        missing = []
        for p in Product.query.all():
            new_path = resolve_image(p.name, p.image)
            if new_path and p.image != new_path:
                print(f'  OK {p.name}: {p.image!r} -> {new_path}')
                p.image = new_path
                updated += 1
            elif not new_path:
                missing.append(p.name)

        if updated:
            db.session.commit()
            print(f'\nОбновлено: {updated} товаров')
        else:
            print('Пути изображений актуальны')

        if missing:
            print(f'Без файла на диске: {len(missing)}')
            for name in missing[:8]:
                print(f'  - {name}')
            if len(missing) > 8:
                print(f'  ... и ещё {len(missing) - 8}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
