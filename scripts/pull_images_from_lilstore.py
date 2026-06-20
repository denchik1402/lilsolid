#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скачивает изображения товаров с lilstore.ru, если локального файла нет.
Запускается на сервере lilsolid после fix_product_images.py.
"""
from __future__ import annotations

import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PRODUCTS_BASE = 'static/images/products'
SOURCE_BASE = os.environ.get('LILSTORE_IMAGES_URL', 'https://lilstore.ru/static/images/products')


def _local_path(rel: str) -> str:
    return os.path.join(PRODUCTS_BASE, rel.replace('\\', '/'))


def _download(url: str, dest: str) -> bool:
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'lilsolid-sync/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        if len(data) < 200:
            return False
        with open(dest, 'wb') as f:
            f.write(data)
        return True
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        print(f'  skip {url}: {exc}')
        return False


def _candidates(product_name: str, rel: str | None) -> list[str]:
    paths: list[str] = []
    if rel:
        paths.append(rel.replace('\\', '/'))
    slugish = product_name.strip()
    for subdir in ('Devices', 'Sticks'):
        paths.append(f'{subdir}/{slugish}/1.webp')
        paths.append(f'{subdir}/{slugish}/1.jpg')
        paths.append(f'{subdir}/{slugish}/photo.webp')
    if rel and '/' not in rel:
        paths.append(rel)
    # dedupe
    seen = set()
    out = []
    for p in paths:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def main() -> int:
    from app import app, db
    from models import Product

    downloaded = 0
    with app.app_context():
        for p in Product.query.all():
            rel = (p.image or '').strip()
            if rel and os.path.isfile(_local_path(rel)):
                continue
            for cand in _candidates(p.name, rel):
                url = f'{SOURCE_BASE.rstrip("/")}/{cand}'
                dest = _local_path(cand)
                if _download(url, dest):
                    if p.image != cand:
                        print(f'  OK {p.name}: {cand}')
                        p.image = cand
                    downloaded += 1
                    break
        if downloaded:
            db.session.commit()
            print(f'Downloaded/linked: {downloaded}')
        else:
            print('All product images present locally')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
