#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run ORM queries used by index/catalog and report errors."""
import traceback

from app import app, db
from models import Banner, Category, HomeBlock, Product, Review


def _try(label, fn):
    try:
        fn()
        print(f'OK {label}')
    except Exception as exc:
        print(f'FAIL {label}: {exc}')
        traceback.print_exc()


def main() -> int:
    failed = 0
    with app.app_context():
        def run(label, fn):
            nonlocal failed
            try:
                fn()
                print(f'OK {label}')
            except Exception as exc:
                failed += 1
                print(f'FAIL {label}: {exc}')
                traceback.print_exc()

        run('Category.count', lambda: Category.query.count())
        run('Product.count', lambda: Product.query.count())
        run('Product.list', lambda: Product.query.limit(3).all())
        run('Product.views sort', lambda: Product.query.order_by(Product.views.desc()).limit(4).all())
        run('Banner.active', lambda: Banner.query.filter_by(is_active=True).limit(5).all())
        run('Review.approved', lambda: Review.query.filter_by(status='approved').limit(5).all())
        run('HomeBlock.active', lambda: HomeBlock.query.filter_by(is_active=True).limit(3).all())
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
