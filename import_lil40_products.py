#!/usr/bin/env python3
"""Импорт/обновление LIL SOLID 4.0 (4 цвета) из data/lil40_products.json."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from app import app, db
from image_utils import normalize_product_image_path, product_image_exists
from models import Category, Product

DATA_PATH = Path(__file__).resolve().parent / 'data' / 'lil40_products.json'
IMAGE_DIR = Path(__file__).resolve().parent / 'static' / 'images' / 'products'


def _normalize_row(row: dict) -> dict:
    row = dict(row)
    if row.get('image'):
        row['image'] = normalize_product_image_path(row['image'])
    return row


def _repair_lil40_images(static_folder: str) -> int:
    fixed = 0
    for product in Product.query.filter(Product.model == 'LIL SOLID 4.0').all():
        norm = normalize_product_image_path(product.image)
        if norm != product.image:
            product.image = norm
            fixed += 1
            continue
        if norm and not product_image_exists(static_folder, norm):
            stem = Path(norm).stem
            for candidate in IMAGE_DIR.glob(f'{stem}.*'):
                product.image = candidate.name
                fixed += 1
                break
    return fixed


def _find_product(row: dict) -> Product | None:
    name_key = (row.get('name') or '').strip().lower()
    slug = (row.get('slug') or '').strip().lower()
    for p in Product.query.filter(Product.name.ilike('%LIL SOLID 4.0%')).all():
        if (p.name or '').strip().lower() == name_key:
            return p
        if slug and (p.slug or '').strip().lower() == slug:
            return p
        if row.get('color') and row['color'].lower() in (p.name or '').lower():
            return p
    return None


def run() -> None:
    payload = json.loads(DATA_PATH.read_text(encoding='utf-8'))
    with app.app_context():
        lil = Category.query.filter_by(slug='lil').first()
        if not lil:
            raise SystemExit('category lil not found')
        added = updated = 0
        for row in (_normalize_row(r) for r in payload):
            product = _find_product(row)
            if product:
                for key, val in row.items():
                    if key == 'slug' and product.slug:
                        continue
                    if key == 'image' and val and not product_image_exists(app.static_folder, val):
                        continue
                    setattr(product, key, val)
                product.category_id = lil.id
                product.updated_at = datetime.utcnow()
                updated += 1
                continue
            product = Product(
                name=row['name'],
                slug=row.get('slug'),
                price=row['price'],
                cost=row.get('cost'),
                old_price=row.get('old_price'),
                description=row.get('description'),
                characteristics=row.get('characteristics'),
                image=row.get('image'),
                image_alt=row.get('image_alt'),
                images=row.get('images'),
                in_stock=row.get('in_stock', True),
                views=row.get('views', 0),
                model=row.get('model', 'LIL SOLID 4.0'),
                color=row.get('color'),
                is_exclusive=row.get('is_exclusive', False),
                is_hit=row.get('is_hit', True),
                meta_description=row.get('meta_description'),
                meta_keywords=row.get('meta_keywords'),
                category_id=lil.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.session.add(product)
            added += 1
        repaired = _repair_lil40_images(app.static_folder)
        db.session.commit()
        total = Product.query.filter(
            Product.model == 'LIL SOLID 4.0',
            Product.in_stock == True,
        ).count()
        print(f'lil40: added={added}, updated={updated}, repaired_images={repaired}, in_stock_total={total}')


if __name__ == '__main__':
    run()
