#!/usr/bin/env python3
"""Импорт LIL SOLID 4.0 из bundle (JSON + images)."""
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

from app import app, db
from models import Product, Category


def main(bundle_dir: Path) -> None:
    payload = json.loads((bundle_dir / 'lil40_products.json').read_text(encoding='utf-8'))
    img_src = bundle_dir / 'images'
    img_dst = Path('static/images/products')
    img_dst.mkdir(parents=True, exist_ok=True)
    for f in img_src.iterdir():
        if f.is_file():
            shutil.copy2(f, img_dst / f.name)

    with app.app_context():
        lil = Category.query.filter_by(slug='lil').first()
        if not lil:
            raise SystemExit('category lil not found')
        added = updated = 0
        for row in payload:
            existing = Product.query.get(row['id'])
            if existing:
                for key, val in row.items():
                    if key == 'category_id':
                        existing.category_id = lil.id
                    elif key != 'id':
                        setattr(existing, key, val)
                updated += 1
                continue
            p = Product(
                id=row['id'],
                name=row['name'],
                slug=row['slug'],
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
                model=row.get('model'),
                color=row.get('color'),
                is_exclusive=row.get('is_exclusive', False),
                is_hit=row.get('is_hit', True),
                meta_description=row.get('meta_description'),
                meta_keywords=row.get('meta_keywords'),
                category_id=lil.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.session.add(p)
            added += 1
        db.session.commit()
        print(f'done: {added} added, {updated} updated, total lil in stock:',
              Product.query.filter_by(category_id=lil.id, in_stock=True).count())


if __name__ == '__main__':
    main(Path(sys.argv[1] if len(sys.argv) > 1 else '/tmp/lil40_bundle'))
