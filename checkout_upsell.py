# -*- coding: utf-8 -*-
"""Подбор стиков на checkout: ILUMA → TEREA, LIL → HEETS."""
from __future__ import annotations

from models import Category, Product, db

STICK_SLUGS_TEREA = ('terea-sticks',)
STICK_SLUGS_HEETS = ('heets-sticks', 'heets', 'fiit-sticks')

ILUMA_DEVICE_SLUGS = ('iqos-iluma',)
LIL_DEVICE_SLUGS = ('lil', 'lil-solid-30', 'lil-solid-40', 'lil-solid-dual')


def _slug_prefix_match(slug: str, prefixes: tuple[str, ...]) -> bool:
    if not slug:
        return False
    for p in prefixes:
        if slug == p or slug.startswith(p + '-'):
            return True
    return False


def is_stick_product(product, category=None) -> bool:
    category = category or product.category
    slug = (category.slug or '') if category else ''
    if slug in STICK_SLUGS_TEREA + STICK_SLUGS_HEETS or 'stick' in slug:
        return True
    name = (product.name or '').lower()
    return any(x in name for x in ('terea', 'heets', 'fiit'))


def stick_family(product, category=None) -> str | None:
    category = category or product.category
    slug = (category.slug or '') if category else ''
    name = (product.name or '').lower()
    if slug in STICK_SLUGS_TEREA or 'terea' in name:
        return 'terea'
    if slug in STICK_SLUGS_HEETS or 'heets' in name or 'fiit' in name:
        return 'heets'
    return None


def device_stick_family(product, category=None) -> str | None:
    """Какие стики нужны к устройству: terea (ILUMA) или heets (LIL / blade IQOS)."""
    category = category or product.category
    slug = (category.slug or '') if category else ''
    name = (product.name or '').lower()
    model = (product.model or '').lower()

    if _slug_prefix_match(slug, ILUMA_DEVICE_SLUGS) or ('iluma' in name and 'terea' not in name):
        return 'terea'
    if _slug_prefix_match(slug, LIL_DEVICE_SLUGS) or 'lil solid' in name or model.startswith('lil'):
        return 'heets'
    if 'iqos' in name and 'iluma' not in name:
        return 'heets'
    return None


def _section_copy(family: str) -> dict[str, str]:
    if family == 'terea':
        return {
            'title': 'Добавить стики TEREA?',
            'hint': 'IQOS ILUMA работает только со стиками TEREA — удобно взять сразу с устройством.',
            'empty_text': '',
        }
    return {
        'title': 'Добавить стики HEETS?',
        'hint': 'LIL SOLID и классические IQOS используют стики HEETS — добавьте к заказу, чтобы сразу начать.',
        'empty_text': (
            'Стики HEETS скоро появятся в каталоге. Напишите желаемые вкусы в комментарии к заказу — '
            'менеджер добавит их в заказ.'
        ),
    }


def _fetch_stick_products(family: str, limit: int = 6, exclude_ids: set | None = None):
    exclude_ids = exclude_ids or set()
    q = Product.query.filter(Product.in_stock.is_(True))

    if family == 'terea':
        cat_ids = [c.id for c in Category.query.filter(Category.slug.in_(STICK_SLUGS_TEREA)).all()]
        filters = [Product.name.ilike('%TEREA%')]
        if cat_ids:
            filters.append(Product.category_id.in_(cat_ids))
        q = q.filter(db.or_(*filters))
    else:
        cat_ids = [
            c.id for c in Category.query.filter(
                db.or_(
                    Category.slug.in_(STICK_SLUGS_HEETS),
                    Category.slug.ilike('%heets%'),
                )
            ).all()
        ]
        filters = [Product.name.ilike('%HEETS%'), Product.name.ilike('%Fiit%')]
        if cat_ids:
            filters.append(Product.category_id.in_(cat_ids))
        q = q.filter(db.or_(*filters))

    if exclude_ids:
        q = q.filter(~Product.id.in_(list(exclude_ids)))

    return (
        q.order_by(Product.is_hit.desc(), Product.views.desc(), Product.id)
        .limit(limit)
        .all()
    )


def get_checkout_stick_upsell(cart_dict, get_cart_products_fn, limit: int = 6) -> list[dict]:
    """
    Секции upsell для checkout.
    Каждая секция: family, title, hint, products, empty_catalog.
    """
    cart_items, _ = get_cart_products_fn(cart_dict or {})
    if not cart_items:
        return []

    needed: set[str] = set()
    has_sticks: set[str] = set()
    cart_ids: set[int] = set()

    for item in cart_items:
        product = item['product']
        cart_ids.add(product.id)
        if is_stick_product(product):
            fam = stick_family(product)
            if fam:
                has_sticks.add(fam)
        else:
            fam = device_stick_family(product)
            if fam:
                needed.add(fam)

    to_suggest = needed - has_sticks
    if not to_suggest:
        return []

    sections: list[dict] = []
    for family in sorted(to_suggest, key=lambda f: (f != 'terea', f)):
        copy = _section_copy(family)
        products = _fetch_stick_products(family, limit=limit, exclude_ids=cart_ids)
        if not products and family != 'heets':
            continue
        sections.append({
            'family': family,
            'title': copy['title'],
            'hint': copy['hint'],
            'empty_text': copy['empty_text'],
            'products': products,
            'empty_catalog': not products,
        })
    return sections
