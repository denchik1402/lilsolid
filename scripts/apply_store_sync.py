#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply store_sync.json from lilstore.ru — catalog, banners, blog + assets."""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SYNC_URL = os.environ.get('STORE_SYNC_URL', 'https://lilstore.ru/static/store_sync.json')
LOCAL_SYNC = ROOT / 'store_sync.json'
IMAGES = ROOT / 'static' / 'images'
SOURCE = os.environ.get('LILSTORE_IMAGES_URL', 'https://lilstore.ru/static/images')


def _load_payload() -> dict | None:
    for src in (SYNC_URL, str(LOCAL_SYNC)):
        try:
            if src.startswith('http'):
                req = urllib.request.Request(src, headers={'User-Agent': 'lilsolid-sync/1.0'})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = json.loads(resp.read().decode())
            else:
                data = json.loads(Path(src).read_text(encoding='utf-8'))
            if data.get('products'):
                print(f'[sync] loaded from {src}')
                return data
        except (urllib.error.URLError, OSError, json.JSONDecodeError, TimeoutError) as exc:
            print(f'[sync] skip {src}: {exc}')
    return None


def _download_asset(rel: str) -> bool:
    rel = rel.strip().lstrip('/')
    if rel.startswith('images/'):
        rel = rel[7:]
    dest = IMAGES / rel
    if dest.is_file() and dest.stat().st_size > 400:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = f'{SOURCE.rstrip("/")}/{quote(rel, safe="/")}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'lilsolid-sync/1.0'})
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = resp.read()
        if len(body) < 200:
            return False
        dest.write_bytes(body)
        return True
    except (urllib.error.URLError, OSError, TimeoutError):
        return False


def _apply_rows(model, rows: list[dict], clear: bool = True) -> None:
    from extensions import db
    if clear:
        db.session.query(model).delete()
        db.session.flush()
    for row in rows:
        clean = {k: v for k, v in row.items() if k != 'id' and hasattr(model, k)}
        db.session.add(model(**clean))


def main() -> int:
    payload = _load_payload()
    if not payload:
        print('[sync] no payload')
        return 1

    from app import app, db
    from models import Banner, BlogPost, Category, HomeBlock, Product

    assets = set(payload.get('assets') or [])
    for p in payload.get('products', []):
        if p.get('image'):
            assets.add(p['image'])
    for b in payload.get('banners', []):
        if b.get('image'):
            assets.add(b['image'])
    for post in payload.get('blog_posts', []):
        if post.get('cover_image'):
            assets.add(post['cover_image'])

    downloaded = sum(1 for a in assets if _download_asset(a))
    print(f'[sync] assets ok: {downloaded}/{len(assets)}')

    with app.app_context():
        db.session.query(Banner).delete()
        db.session.query(Product).delete()
        db.session.query(HomeBlock).delete()
        db.session.query(BlogPost).delete()
        db.session.query(Category).delete()
        db.session.flush()
        for row in payload.get('categories', []):
            db.session.add(Category(**{k: v for k, v in row.items() if hasattr(Category, k)}))
        db.session.flush()
        for row in payload.get('products', []):
            db.session.add(Product(**{k: v for k, v in row.items() if hasattr(Product, k)}))
        for row in payload.get('banners', []):
            db.session.add(Banner(**{k: v for k, v in row.items() if hasattr(Banner, k)}))
        for row in payload.get('home_blocks', []):
            db.session.add(HomeBlock(**{k: v for k, v in row.items() if hasattr(HomeBlock, k)}))
        for row in payload.get('blog_posts', []):
            db.session.add(BlogPost(**{k: v for k, v in row.items() if hasattr(BlogPost, k)}))
        db.session.commit()
        print(f'[sync] DB: {Product.query.count()} products, {Banner.query.count()} banners, '
              f'{BlogPost.query.count()} blog posts')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
