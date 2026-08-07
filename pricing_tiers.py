# -*- coding: utf-8 -*-
"""Оптовые ступени цены.

Стики TEREA/HEETS: от 2 шт −5%, от 5 шт −10%.
Устройства (IQOS / LIL): от 2 шт −10%.
"""
from __future__ import annotations

from typing import Optional

# (min_qty, discount_fraction) — порядок: сначала больший qty
STICK_WHOLESALE_TIERS: list[tuple[int, float]] = [
    (5, 0.10),
    (2, 0.05),
]

DEVICE_WHOLESALE_TIERS: list[tuple[int, float]] = [
    (2, 0.10),
]

# backward-compatible alias
WHOLESALE_TIERS = STICK_WHOLESALE_TIERS

STICK_CATEGORY_SLUGS = frozenset({'terea-sticks', 'heets', 'sticks'})
DEVICE_CATEGORY_SLUGS = frozenset({'iqos-iluma', 'lil', 'exclusive', 'devices', 'iqos'})


def _cat_slug(product) -> str:
    cat = getattr(product, 'category', None)
    return (getattr(cat, 'slug', None) or '').lower()


def _name_l(product) -> str:
    return (getattr(product, 'name', None) or '').lower()


def is_stick_wholesale_product(product) -> bool:
    slug = _cat_slug(product)
    if slug in STICK_CATEGORY_SLUGS:
        return True
    name = _name_l(product)
    return (
        name.startswith('terea ')
        or ' terea ' in f' {name} '
        or name.startswith('heets ')
        or name.startswith('fiit ')
    )


def is_device_wholesale_product(product) -> bool:
    if is_stick_wholesale_product(product):
        return False
    slug = _cat_slug(product)
    if slug in DEVICE_CATEGORY_SLUGS:
        return True
    name = _name_l(product)
    return (
        'iqos' in name
        or 'iluma' in name
        or 'lil solid' in name
        or name.startswith('lil ')
    )


def is_wholesale_product(product) -> bool:
    """Любой товар с оптовой лестницей (стики или устройства)."""
    return is_stick_wholesale_product(product) or is_device_wholesale_product(product)


def wholesale_kind(product) -> Optional[str]:
    if is_stick_wholesale_product(product):
        return 'sticks'
    if is_device_wholesale_product(product):
        return 'devices'
    return None


def tiers_for_product(product) -> list[tuple[int, float]]:
    kind = wholesale_kind(product)
    if kind == 'sticks':
        return STICK_WHOLESALE_TIERS
    if kind == 'devices':
        return DEVICE_WHOLESALE_TIERS
    return []


def discount_for_qty(qty: int, tiers: Optional[list[tuple[int, float]]] = None) -> float:
    qty = max(1, int(qty or 1))
    for min_qty, frac in (tiers if tiers is not None else STICK_WHOLESALE_TIERS):
        if qty >= min_qty:
            return frac
    return 0.0


def discount_for_product(product, qty: int = 1) -> float:
    tiers = tiers_for_product(product)
    if not tiers:
        return 0.0
    return discount_for_qty(qty, tiers)


def unit_price(product, qty: int = 1) -> float:
    base = float(getattr(product, 'price', 0) or 0)
    disc = discount_for_product(product, qty)
    if not disc:
        return base
    return round(base * (1.0 - disc), 2)


def line_subtotal(product, qty: int) -> float:
    qty = max(1, int(qty or 1))
    return round(unit_price(product, qty) * qty, 2)


def wholesale_tiers_view(product) -> Optional[list[dict]]:
    """Данные для блока на карточке товара."""
    kind = wholesale_kind(product)
    tiers = tiers_for_product(product)
    if not kind or not tiers:
        return None
    base = float(product.price or 0)
    if kind == 'sticks':
        unit_word = 'блок'
        intro = 'Чем больше блоков стиков — тем ниже цена за блок.'
        label_one = 'от 1 блока'
    else:
        unit_word = 'шт.'
        intro = 'При покупке от 2 устройств — скидка 10% на каждое.'
        label_one = 'от 1 шт.'
    rows = [{
        'qty': 1,
        'discount_pct': 0,
        'unit': base,
        'label': label_one,
        'kind': kind,
        'unit_word': unit_word,
        'intro': intro,
    }]
    for min_qty, frac in sorted(tiers, key=lambda x: x[0]):
        if kind == 'sticks':
            label = f'от {min_qty} блоков'
        else:
            label = f'от {min_qty} шт.'
        rows.append({
            'qty': min_qty,
            'discount_pct': int(frac * 100),
            'unit': round(base * (1.0 - frac), 2),
            'label': label,
            'kind': kind,
            'unit_word': unit_word,
            'intro': intro,
        })
    return rows


def apply_cart_pricing(items: list[dict]) -> tuple[list[dict], float]:
    """Пересчёт позиций корзины с учётом опта. items: product, quantity."""
    total = 0.0
    out = []
    for item in items:
        product = item['product']
        qty = int(item.get('quantity') or 1)
        unit = unit_price(product, qty)
        sub = round(unit * qty, 2)
        disc = discount_for_product(product, qty)
        total += sub
        out.append({
            **item,
            'quantity': qty,
            'unit_price': unit,
            'base_price': float(product.price or 0),
            'wholesale_discount': disc,
            'wholesale_kind': wholesale_kind(product),
            'subtotal': sub,
        })
    return out, round(total, 2)
