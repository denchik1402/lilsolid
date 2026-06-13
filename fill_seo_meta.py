#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Заполнение SEO-полей (image_alt, meta_description, meta_keywords) для товаров, категорий и моделей.

Использование:
  python fill_seo_meta.py           # только пустые поля
  python fill_seo_meta.py --force   # перезаписать все SEO-поля
  python fill_seo_meta.py --refresh-keywords  # обновить meta_keywords у всех товаров
"""
import argparse
import sys

from app import app
from extensions import db
from models import Category, Product, DeviceModel, BlogPost
from seo_utils import generate_category_seo, generate_product_seo, generate_device_model_seo, device_model_slug, CATEGORY_HOME, SITE


def _should_set(current: str | None, force: bool) -> bool:
    return force or not (current or '').strip()


def fill_seo(force: bool = False, refresh_keywords: bool = False) -> tuple[int, int, int, int]:
    categories_updated = 0
    products_updated = 0
    models_updated = 0
    blog_updated = 0

    for category in Category.query.order_by(Category.id).all():
        seo = generate_category_seo(category)
        home = CATEGORY_HOME.get(category.slug or '', {})
        changed = False
        if _should_set(category.meta_description, force):
            category.meta_description = seo['meta_description']
            changed = True
        if _should_set(category.meta_keywords, force) or refresh_keywords:
            category.meta_keywords = seo['meta_keywords']
            changed = True
        if _should_set(category.description, force) and seo.get('seo_text'):
            category.description = seo['seo_text']
            changed = True
        if home.get('image') and (force or category.image != home['image']):
            category.image = home['image']
            changed = True
        if changed:
            categories_updated += 1

    for product in Product.query.order_by(Product.id).all():
        seo = generate_product_seo(product)
        changed = False
        if _should_set(product.image_alt, force):
            product.image_alt = seo['image_alt']
            changed = True
        if _should_set(product.meta_description, force):
            product.meta_description = seo['meta_description']
            changed = True
        if _should_set(product.meta_keywords, force) or refresh_keywords:
            product.meta_keywords = seo['meta_keywords']
            changed = True
        if changed:
            products_updated += 1

    for device_model in DeviceModel.query.order_by(DeviceModel.id).all():
        seo = generate_device_model_seo(device_model)
        changed = False
        if _should_set(device_model.image_alt, force):
            device_model.image_alt = seo['image_alt']
            changed = True
        slug = device_model_slug(device_model.name)
        if slug and (force or not device_model.slug):
            device_model.slug = slug
            changed = True
        if _should_set(device_model.meta_description, force):
            device_model.meta_description = seo['meta_description']
            changed = True
        if _should_set(device_model.meta_keywords, force) or refresh_keywords:
            device_model.meta_keywords = seo['meta_keywords']
            changed = True
        if _should_set(device_model.seo_text, force) and seo.get('seo_text'):
            device_model.seo_text = seo['seo_text']
            changed = True
        if changed:
            models_updated += 1

    for post in BlogPost.query.order_by(BlogPost.id).all():
        changed = False
        if _should_set(post.meta_description, force) and post.excerpt:
            post.meta_description = (post.excerpt or '')[:300]
            changed = True
        if _should_set(post.meta_keywords, force) and post.title:
            post.meta_keywords = post.meta_keywords or f'{post.title}, IQOS, TEREA, ILUMA, {SITE}, блог, илюма, айкос'
            changed = True
        if changed:
            blog_updated += 1

    db.session.commit()
    return categories_updated, products_updated, models_updated, blog_updated


def main() -> int:
    parser = argparse.ArgumentParser(description='Fill SEO meta fields for products and categories')
    parser.add_argument('--force', action='store_true', help='Overwrite existing SEO values')
    parser.add_argument('--refresh-keywords', action='store_true', help='Refresh meta_keywords from seo_utils for all items')
    args = parser.parse_args()

    with app.app_context():
        cats, prods, models, blog = fill_seo(force=args.force, refresh_keywords=args.refresh_keywords)
        print(f'Updated categories: {cats}')
        print(f'Updated products: {prods}')
        print(f'Updated device models: {models}')
        print(f'Updated blog posts: {blog}')
        total = Category.query.count()
        filled_c = Category.query.filter(Category.meta_description.isnot(None)).count()
        filled_p = Product.query.filter(Product.meta_description.isnot(None)).count()
        filled_m = DeviceModel.query.filter(DeviceModel.meta_description.isnot(None)).count()
        print(f'Categories with meta_description: {filled_c}/{total}')
        print(f'Products with meta_description: {filled_p}/{Product.query.count()}')
        print(f'Device models with meta_description: {filled_m}/{DeviceModel.query.count()}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
