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


def _norm_product_image(path: str | None) -> str | None:
    if not path:
        return path
    p = path.strip().replace('\\', '/').lstrip('/')
    if p.startswith('images/'):
        p = p[7:]
    if p.startswith('product_') and '/' not in p:
        return f'products/{p}'
    return p


def _norm_banner_image(path: str | None) -> str | None:
    if not path:
        return path
    p = path.strip().replace('\\', '/').lstrip('/')
    if p.startswith('images/'):
        p = p[7:]
    if p.startswith('banner_') and not p.startswith('banners/') and not p.startswith('products/'):
        return f'banners/{p}'
    return p


def _asset_candidates(rel: str) -> list[str]:
    rel = rel.strip().replace('\\', '/').lstrip('/')
    if rel.startswith('images/'):
        rel = rel[7:]
    out: list[str] = []
    seen: set[str] = set()

    def add(p: str) -> None:
        if p and p not in seen:
            seen.add(p)
            out.append(p)

    add(rel)
    if rel.startswith('banners/'):
        add(rel[8:])
    elif rel.startswith('banner_'):
        add(f'banners/{rel}')
    if rel.startswith('products/'):
        add(rel[9:])
    elif rel.startswith('product_'):
        add(f'products/{rel}')
    if rel.startswith('blog/covers/'):
        add(rel)
    return out


def _load_payload() -> dict | None:
    # Bundled file first — URL often 404 on lilstore static.
    for src in (str(LOCAL_SYNC), SYNC_URL):
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
    rel = rel.strip().replace('\\', '/').lstrip('/')
    if rel.startswith('images/'):
        rel = rel[7:]
    for candidate in _asset_candidates(rel):
        dest = IMAGES / candidate
        if dest.is_file() and dest.stat().st_size > 400:
            return True
        dest.parent.mkdir(parents=True, exist_ok=True)
        url = f'{SOURCE.rstrip("/")}/{quote(candidate, safe="/")}'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'lilsolid-sync/1.0'})
            with urllib.request.urlopen(req, timeout=45) as resp:
                body = resp.read()
            if len(body) >= 200:
                dest.write_bytes(body)
                return True
        except (urllib.error.URLError, OSError, TimeoutError):
            continue
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

    for p in payload.get('products', []):
        if p.get('image'):
            p['image'] = _norm_product_image(p['image'])
    for b in payload.get('banners', []):
        if b.get('image'):
            b['image'] = _norm_banner_image(b['image'])

    assets = set(payload.get('assets') or [])
    for p in payload.get('products', []):
        if p.get('image'):
            for c in _asset_candidates(p['image']):
                assets.add(c)
    for b in payload.get('banners', []):
        if b.get('image'):
            for c in _asset_candidates(b['image']):
                assets.add(c)
    for post in payload.get('blog_posts', []):
        if post.get('cover_image'):
            for c in _asset_candidates(post['cover_image']):
                assets.add(c)

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
