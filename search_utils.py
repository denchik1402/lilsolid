# -*- coding: utf-8 -*-
"""Поиск товаров с альтернативными написаниями: илюма / iluma / ILUMA и т.д."""
from __future__ import annotations

import re

_QUERY_SUBSTITUTIONS = [
    ('ильюма', 'iluma'),
    ('илюма', 'iluma'),
    ('илума', 'iluma'),
    ('айкос', 'iqos'),
    ('икос', 'iqos'),
    ('тереа', 'terea'),
    ('тerea', 'terea'),
    ('лилсолид', 'lil solid'),
    ('лил солид', 'lil solid'),
    ('лит solid', 'lil solid'),
    ('standard', 'standart'),
    ('стандарт', 'standart'),
    ('хитс', 'heets'),
    ('heets', 'heets'),
    ('фит', 'fit'),
    ('стики', 'terea'),
    ('селетти', 'seletti'),
    ('пробуж', 'purple'),
    ('амбр', 'amber'),
    ('сильвер', 'silver'),
]

_QUERY_EXPANSIONS = {
    'iluma': ['iluma', 'iqos iluma', 'iluma i'],
    'iqos': ['iqos', 'iqos iluma'],
    'terea': ['terea', 'terea kz'],
    'lil': ['lil solid', 'lil'],
    'solid': ['lil solid', 'solid'],
    'standart': ['standart', 'standard'],
    'standard': ['standart', 'standard'],
    'prime': ['prime'],
    'heets': ['heets'],
    'fit': ['fit'],
    'dual': ['dual'],
    'seletti': ['seletti'],
}


def _normalize_query_text(text: str) -> str:
    s = (text or '').strip().lower()
    s = s.replace('ё', 'е')
    return re.sub(r'\s+', ' ', s)


def expand_search_terms(query: str) -> list[str]:
    raw = (query or '').strip()
    if not raw:
        return []

    terms: set[str] = {raw.lower(), _normalize_query_text(raw)}

    variants = set(terms)
    for _ in range(3):
        next_variants = set(variants)
        for v in variants:
            for src, dst in _QUERY_SUBSTITUTIONS:
                if src in v:
                    next_variants.add(v.replace(src, dst))
                    next_variants.add(v)
        variants = next_variants
    terms.update(variants)

    words = re.split(r'[\s,+/\\\-]+', _normalize_query_text(raw))
    for word in words:
        if len(word) < 2:
            continue
        terms.add(word)
        for key, extras in _QUERY_EXPANSIONS.items():
            if key in word or word == key:
                terms.update(extras)

    for key, extras in _QUERY_EXPANSIONS.items():
        if key in terms or any(key in w for w in words):
            terms.update(extras)

    result: list[str] = []
    seen: set[str] = set()
    for t in sorted(terms, key=len, reverse=True):
        t = t.strip()
        if len(t) < 2 and t != _normalize_query_text(raw):
            continue
        if t not in seen:
            seen.add(t)
            result.append(t)
        if len(result) >= 24:
            break
    return result


def escape_like(value: str) -> str:
    if not value:
        return value
    return value.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


def product_search_filter(query: str, Product, *, in_stock_only: bool = False):
    from sqlalchemy import and_, or_

    terms = expand_search_terms(query)
    if not terms:
        return None

    fields = (
        Product.name,
        Product.description,
        Product.meta_keywords,
        Product.model,
        Product.color,
    )
    conditions = []
    for term in terms:
        pattern = f'%{escape_like(term)}%'
        for field in fields:
            conditions.append(field.ilike(pattern, escape='\\'))

    expr = or_(*conditions)
    if in_stock_only:
        return and_(Product.in_stock.is_(True), expr)
    return expr
