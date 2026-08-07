# -*- coding: utf-8 -*-
"""Оптовые ступени цены: от 2 шт −5%, от 5 шт −10% (стики TEREA/HEETS)."""
from __future__ import annotations

from typing import Optional

# (min_qty, discount_fraction)
WHOLESALE_TIERS: list[tuple[int, float]] = [
    (5, 0.10),
    (2, 0.05),
]

WHOLESALE_CATEGORY_SLUGS = frozenset({'terea-sticks', 'heets', 'sticks'})


def is_wholesale_product(product) -> bool:
    """Стики подлежат оптовой лестнице."""
    cat = getattr(product, 'category', None)
    slug = (getattr(cat, 'slug', None) or '').lower()
    if slug in WHOLESALE_CATEGORY_SLUGS:
        return True
    name = (getattr(product, 'name', None) or '').lower()
    return name.startswith('terea ') or ' terea ' in f' {name} ' or name.startswith('heets ')


def discount_for_qty(qty: int) -> float:
    qty = max(1, int(qty or 1))
    for min_qty, frac in WHOLESALE_TIERS:
        if qty >= min_qty:
            return frac
    return 0.0


def unit_price(product, qty: int = 1) -> float:
    base = float(getattr(product, 'price', 0) or 0)
    if not is_wholesale_product(product):
        return base
    return round(base * (1.0 - discount_for_qty(qty)), 2)


def line_subtotal(product, qty: int) -> float:
    qty = max(1, int(qty or 1))
    return round(unit_price(product, qty) * qty, 2)


def wholesale_tiers_view(product) -> Optional[list[dict]]:
    """Данные для блока на карточке товара."""
    if not is_wholesale_product(product):
        return None
    base = float(product.price or 0)
    rows = [{'qty': 1, 'discount_pct': 0, 'unit': base, 'label': 'от 1 шт.'}]
    for min_qty, frac in sorted(WHOLESALE_TIERS, key=lambda x: x[0]):
        rows.append({
            'qty': min_qty,
            'discount_pct': int(frac * 100),
            'unit': round(base * (1.0 - frac), 2),
            'label': f'от {min_qty} шт.',
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
        disc = discount_for_qty(qty) if is_wholesale_product(product) else 0.0
        total += sub
        out.append({
            **item,
            'quantity': qty,
            'unit_price': unit,
            'base_price': float(product.price or 0),
            'wholesale_discount': disc,
            'subtotal': sub,
        })
    return out, round(total, 2)
