# -*- coding: utf-8 -*-
"""Выравнивание цен с табачка24.рф (идемпотентно, для деплоя).

LIL SOLID 4.0 → 3999
LIL SOLID 3.0 → 3799
IQOS ILUMA i One (базовые цвета, без LE) → 7999
TEREA (все блоки) → 3700

При снижении цены старый price пишется в old_price (если old_price пуст или ниже).
"""
from __future__ import annotations

import re
import sys

from app import app, db
from models import Product

LIMITED_RE = re.compile(
    r'limited|seletti|anniversary|exclusive|remix|skylens|together|travel',
    re.I,
)


def _norm(s: str) -> str:
    return (s or '').replace('ё', 'е').lower()


def _is_lil40(p: Product) -> bool:
    n = _norm(p.name)
    m = _norm(p.model or '')
    return 'lil solid 4.0' in n or 'lil solid 4.0' in m or 'solid 4.0' in n


def _is_lil30(p: Product) -> bool:
    n = _norm(p.name)
    m = _norm(p.model or '')
    if 'dual' in n or 'dual' in m:
        return False
    if '4.0' in n or '4.0' in m:
        return False
    return 'lil solid 3.0' in n or 'lil solid 3.0' in m or (
        'lil solid 3' in n and '4.0' not in n
    )


def _is_base_i_one(p: Product) -> bool:
    n = _norm(p.name)
    m = _norm(p.model or '')
    if 'i one' not in n and 'i one' not in m and 'iluma i one' not in n:
        return False
    if LIMITED_RE.search(p.name or ''):
        return False
    if getattr(p, 'is_exclusive', False):
        return False
    return True


def _is_terea_block(p: Product) -> bool:
    n = _norm(p.name)
    slug = ''
    if p.category:
        slug = (p.category.slug or '').lower()
    return slug == 'terea-sticks' or n.startswith('terea ') or n.startswith('terea')


def _set_price(p: Product, new_price: float, touched: list) -> None:
    old = float(p.price or 0)
    if abs(old - new_price) < 0.01:
        return
    if old > new_price:
        prev_old = float(p.old_price or 0)
        if prev_old < old:
            p.old_price = old
    p.price = float(new_price)
    touched.append(f'{p.id}:{p.name}: {old:g} -> {new_price:g}')


def run() -> int:
    touched: list[str] = []
    with app.app_context():
        products = Product.query.all()
        for p in products:
            if _is_lil40(p):
                _set_price(p, 3999.0, touched)
            elif _is_lil30(p):
                _set_price(p, 3799.0, touched)
            elif _is_base_i_one(p):
                _set_price(p, 7999.0, touched)
            elif _is_terea_block(p):
                _set_price(p, 3700.0, touched)
        if touched:
            db.session.commit()
        print(f'align_prices_vs_tabachka: updated {len(touched)} products')
        for line in touched:
            print(' ', line)
    return 0


if __name__ == '__main__':
    sys.exit(run())
