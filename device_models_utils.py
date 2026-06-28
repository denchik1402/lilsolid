"""Справочник моделей устройств, определение модели по названию, группы для каруселей."""
from __future__ import annotations

import re
from typing import Optional

# Порядок в фильтре каталога (name, sort_order)
CANONICAL_DEVICE_MODELS: list[tuple[str, int]] = [
    ('IQOS ILUMA I ONE', 1),
    ('IQOS ILUMA I', 2),
    ('IQOS ILUMA I PRIME', 3),
    ('IQOS ILUMA ONE', 4),
    ('IQOS ILUMA PRIME', 5),
    ('IQOS ILUMA STANDART', 6),
    ('LIL SOLID DUAL', 7),
    ('LIL SOLID 3.0', 8),
    ('LIL SOLID 4.0', 9),
]

# Старые названия → канонические (миграция и импорт)
LEGACY_MODEL_NAMES: dict[str, str] = {
    'IQOS Iluma i One': 'IQOS ILUMA I ONE',
    'IQOS Iluma i Standart': 'IQOS ILUMA I',
    'IQOS Iluma i Standard': 'IQOS ILUMA I',
    'IQOS Iluma i Prime': 'IQOS ILUMA I PRIME',
}

MODEL_MAP: list[tuple[str, str]] = [
    (r'\blil\s+solid\s+dual\b', 'LIL SOLID DUAL'),
    (r'\bsolid\s+dual\b', 'LIL SOLID DUAL'),
    (r'\blil\s+solid\s+4\.0\b', 'LIL SOLID 4.0'),
    (r'\bsolid\s+4\.0\b', 'LIL SOLID 4.0'),
    (r'\blil\s+solid\s+3\.0\b', 'LIL SOLID 3.0'),
    (r'\bsolid\s+3\.0\b', 'LIL SOLID 3.0'),
    (r'\biluma\s+i\s+one\b', 'IQOS ILUMA I ONE'),
    (r'\bi\s+one\b', 'IQOS ILUMA I ONE'),
    (r'\biluma\s+i\s+prime\b', 'IQOS ILUMA I PRIME'),
    (r'\bi\s+prime\b', 'IQOS ILUMA I PRIME'),
    (r'\biluma\s+i\s+standart\s+seletti\b', 'IQOS ILUMA I'),
    (r'\biluma\s+i\s+standart\b', 'IQOS ILUMA I'),
    (r'\biluma\s+i\s+standard\b', 'IQOS ILUMA I'),
    (r'\bi\s+standart\b', 'IQOS ILUMA I'),
    (r'\bi\s+standard\b', 'IQOS ILUMA I'),
    (r'\biluma\s+one\b', 'IQOS ILUMA ONE'),
    (r'\biluma\s+prime\b', 'IQOS ILUMA PRIME'),
    (r'\biqos\s+iluma\b', 'IQOS ILUMA STANDART'),
]

# Относительная «новизна» для карусели «Новинки» (выше = новее)
MODEL_NEWNESS: dict[str, int] = {
    'LIL SOLID 4.0': 100,
    'IQOS ILUMA I ONE': 92,
    'IQOS ILUMA I': 92,
    'IQOS ILUMA I PRIME': 92,
    'LIL SOLID 3.0': 78,
    'LIL SOLID DUAL': 72,
    'IQOS ILUMA ONE': 55,
    'IQOS ILUMA PRIME': 55,
    'IQOS ILUMA STANDART': 50,
}

TEREA_NEWNESS_HINTS: list[tuple[str, int]] = [
    ('starling pearl', 88),
    ('sun pearl', 87),
    ('twilight pearl', 87),
    ('tidal pearl', 86),
    ('provience pearl', 85),
    ('pearl', 84),
    ('summer wave', 70),
    ('zing wave', 65),
]


def normalize_legacy_model(name: Optional[str]) -> Optional[str]:
    if not name:
        return name
    stripped = name.strip()
    return LEGACY_MODEL_NAMES.get(stripped, stripped)


def detect_device_model(name: str, description: str = '') -> Optional[str]:
    """Определяет каноническую модель устройства по названию."""
    text = f'{name or ""} {description or ""}'.lower()
    if 'terea' in text and 'iluma' not in text:
        return None
    for pattern, model in MODEL_MAP:
        if re.search(pattern, text, re.IGNORECASE):
            return model
    return None


def product_catalog_family(product, category=None) -> Optional[str]:
    """Группа для каруселей: iluma | lil | terea."""
    cat = category or getattr(product, 'category', None)
    cat_slug = (getattr(cat, 'slug', None) or '').lower()
    name = (product.name or '').lower()
    model = (product.model or '').lower()

    if cat_slug == 'terea-sticks' or (name.startswith('terea ') or ' terea ' in name):
        return 'terea'
    if cat_slug == 'lil' or 'lil solid' in name or model.startswith('lil'):
        return 'lil'
    if cat_slug == 'iqos-iluma' or ('iluma' in name and 'terea' not in name):
        return 'iluma'
    return None


def product_newness_score(product, category=None) -> int:
    """Чем выше — тем «новее» для сортировки в «Новинках»."""
    name = (product.name or '').lower()
    model = normalize_legacy_model(product.model) or product.model or ''
    score = MODEL_NEWNESS.get(model, 45)

    for hint, bonus in TEREA_NEWNESS_HINTS:
        if hint in name:
            score = max(score, bonus)
            break

    if product.created_at:
        score += min(product.created_at.year - 2020, 5)
    return score
