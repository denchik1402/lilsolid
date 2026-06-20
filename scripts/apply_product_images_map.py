#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Применяет product_images_map.json и скачивает файлы с lilstore.ru.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

MAP_FILE = ROOT / 'product_images_map.json'
PRODUCTS_BASE = ROOT / 'static' / 'images' / 'products'
SOURCE_BASE = os.environ.get('LILSTORE_IMAGES_URL', 'https://lilstore.ru/static/images/products')


def _norm(name: str) -> str:
    return ' '.join(name.lower().split())


def _load_map() -> dict[str, str]:
    if not MAP_FILE.exists():
        print(f'[images] map not found: {MAP_FILE}')
        return {}
    data = json.loads(MAP_FILE.read_text(encoding='utf-8'))
    return {_norm(k): v for k, v in data.items()}


def _url(path: str) -> str:
    from urllib.parse import quote
    return f'{SOURCE_BASE.rstrip("/")}/{quote(path, safe="/")}'


def _download(rel: str) -> bool:
    dest = PRODUCTS_BASE / rel
    if dest.is_file() and dest.stat().st_size > 500:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = _url(rel)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'lilsolid-images/1.0'})
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = resp.read()
        if len(data) < 200:
            return False
        dest.write_bytes(data)
        print(f'  dl {rel} ({len(data)} bytes)')
        return True
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        print(f'  fail {rel}: {exc}')
        return False


def _match_path(name: str, image_map: dict[str, str]) -> str | None:
    key = _norm(name)
    if key in image_map:
        return image_map[key]
    for mk, path in image_map.items():
        if mk in key or key in mk:
            return path
    return None


def main() -> int:
    from app import app, db
    from models import Product

    image_map = _load_map()
    if not image_map:
        return 1

    updated = 0
    downloaded = 0
    with app.app_context():
        for p in Product.query.all():
            rel = _match_path(p.name, image_map)
            if not rel:
                print(f'  ? no map for {p.name!r}')
                continue
            if _download(rel):
                downloaded += 1
                if p.image != rel:
                    p.image = rel
                    updated += 1
        if updated:
            db.session.commit()
        print(f'[images] map entries={len(image_map)} updated={updated} downloaded={downloaded}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
