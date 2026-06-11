#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Список URL для ручного запроса индексирования (Google Search Console, Яндекс.Вебмастер).

Запуск:
  python generate_indexing_urls.py
  python generate_indexing_urls.py --out seo/google_indexing_urls.txt

Полный список товаров — в https://lilstore.ru/sitemap.xml (отправляйте sitemap один раз,
вручную — только приоритетные и новые страницы, лимит GSC ~10–20 URL в день).
"""
from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(ROOT, 'seo', 'google_indexing_urls.txt')
BASE = 'https://lilstore.ru'


def _base_url() -> str:
    try:
        import config
        url = getattr(config, 'SITE_URL', None)
        if url and str(url).startswith('http') and '127.0.0.1' not in url and 'localhost' not in url:
            return url.rstrip('/')
    except ImportError:
        pass
    return BASE


def collect_urls(base: str) -> tuple[list[str], list[str], list[str]]:
    from app import app
    from extensions import db
    from models import BlogPost, Category, DeviceModel, Product

    priority: list[str] = []
    catalog_pages: list[str] = []
    products: list[str] = []

    with app.app_context():
        priority.extend([
            base + '/',
            base + '/catalog',
            base + '/blog',
            base + '/about',
            base + '/delivery',
            base + '/contacts',
            base + '/faq',
            base + '/privacy',
        ])

        for cat in Category.query.order_by(Category.id).all():
            if cat.slug:
                catalog_pages.append(base + f'/catalog/{cat.slug}')

        for dm in DeviceModel.query.filter(DeviceModel.slug.isnot(None)).order_by(DeviceModel.id).all():
            catalog_pages.append(base + f'/catalog/{dm.slug}')

        for post in BlogPost.query.filter_by(is_published=True).order_by(BlogPost.created_at.desc()).all():
            priority.append(base + f'/blog/{post.slug}')

        for p in Product.query.filter_by(in_stock=True).order_by(Product.id).all():
            slug = p.get_url_slug()
            if slug:
                products.append(base + f'/product/{slug}')

    # dedupe preserving order
    def _uniq(items: list[str]) -> list[str]:
        seen = set()
        out = []
        for u in items:
            if u not in seen:
                seen.add(u)
                out.append(u)
        return out

    return _uniq(priority), _uniq(catalog_pages), _uniq(products)


def write_file(path: str, base: str, priority: list[str], catalog: list[str], products: list[str]) -> None:
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    lines = [
        '# URL для ручного запроса индексирования — LIL STORE',
        f'# Сгенерировано для: {base}',
        '#',
        '# Google Search Console → Проверка URL → «Запросить индексирование»',
        '# Яндекс.Вебмастер → Переобход страниц',
        '#',
        '# Sitemap (отправить один раз, не дублировать каждый URL):',
        f'# {base}/sitemap.xml',
        '#',
        '# Лимит GSC: ~10–20 URL в день. Сначала блок «Приоритет», затем каталог и товары.',
        '',
        '=== ПРИОРИТЕТ (главная, блог, статьи, статика) ===',
    ]
    lines.extend(priority)
    lines.extend(['', '=== КАТАЛОГ (категории и модели, ЧПУ) ==='])
    lines.extend(catalog)
    lines.extend([
        '',
        '=== ТОВАРЫ (в наличии; полный список также в sitemap.xml) ===',
        f'# Всего товаров: {len(products)}',
    ])
    lines.extend(products)
    lines.append('')

    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate URL list for manual search indexing')
    parser.add_argument('--out', default=DEFAULT_OUT, help='Output file path')
    parser.add_argument('--base', default=None, help='Override site base URL')
    args = parser.parse_args()

    base = (args.base or _base_url()).rstrip('/')
    try:
        priority, catalog, products = collect_urls(base)
    except Exception as exc:
        print(f'Ошибка: {exc}', file=sys.stderr)
        return 1

    write_file(args.out, base, priority, catalog, products)
    total = len(priority) + len(catalog) + len(products)
    print(f'Готово: {args.out}')
    print(f'  приоритет: {len(priority)}, каталог: {len(catalog)}, товары: {len(products)}, всего: {total}')
    print(f'  sitemap: {base}/sitemap.xml')
    return 0


if __name__ == '__main__':
    sys.exit(main())
