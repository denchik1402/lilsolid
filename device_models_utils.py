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

STICK_NAME_RE = re.compile(r'^\s*(terea|heets|fiit)\b', re.IGNORECASE)

DEVICE_MODEL_DISPLAY_NAMES: dict[str, str] = {
    'IQOS ILUMA I ONE': 'IQOS ILUMA i One',
    'IQOS ILUMA I': 'IQOS ILUMA i Standart',
    'IQOS ILUMA I PRIME': 'IQOS ILUMA i Prime',
    'IQOS ILUMA ONE': 'IQOS ILUMA One',
    'IQOS ILUMA PRIME': 'IQOS ILUMA Prime',
}

LEGACY_DEVICE_MODEL_SLUGS: dict[str, str] = {
    'iqos-iluma-standart': 'iqos-iluma-i',
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
]

# Относительная «новизна» для карусели «Новинки» (выше = новее)
ILUMA_I_MODELS = frozenset({
    'IQOS ILUMA I ONE',
    'IQOS ILUMA I',
    'IQOS ILUMA I PRIME',
})
LIL_LEGACY_MODELS = frozenset({'LIL SOLID 3.0', 'LIL SOLID DUAL'})

MODEL_NEWNESS: dict[str, int] = {
    'LIL SOLID 4.0': 100,
    'IQOS ILUMA I ONE': 88,
    'IQOS ILUMA I': 87,
    'IQOS ILUMA I PRIME': 86,
    'LIL SOLID 3.0': 72,
    'LIL SOLID DUAL': 68,
    'IQOS ILUMA ONE': 55,
    'IQOS ILUMA PRIME': 52,
}

TEREA_NEWNESS_HINTS: list[tuple[str, int]] = [
    ('starling pearl', 84),
    ('sun pearl', 83),
    ('twilight pearl', 83),
    ('tidal pearl', 82),
    ('provience pearl', 81),
    ('pearl', 80),
    ('summer wave', 74),
    ('zing wave', 70),
]


def normalize_legacy_model(name: Optional[str]) -> Optional[str]:
    if not name:
        return name
    stripped = name.strip()
    return LEGACY_MODEL_NAMES.get(stripped, stripped)


def is_stick_product_name(name: str) -> bool:
    """Стики TEREA/HEETS/Fiit не получают поле model устройства."""
    return bool(STICK_NAME_RE.search((name or '').strip()))


def device_model_display_name(name: str) -> str:
    return DEVICE_MODEL_DISPLAY_NAMES.get(name, name)


def resolve_device_model_slug(slug: str) -> str:
    return LEGACY_DEVICE_MODEL_SLUGS.get((slug or '').lower(), slug or '')


def detect_device_model(name: str, description: str = '') -> Optional[str]:
    """Определяет каноническую модель устройства по названию."""
    if is_stick_product_name(name):
        return None
    text = f'{name or ""} {description or ""}'.lower()
    if re.search(r'\b(terea|heets|fiit)\b', (name or '').lower()):
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


def resolve_product_model(product) -> Optional[str]:
    """Каноническая модель: из поля model или по названию."""
    model = normalize_legacy_model(getattr(product, 'model', None)) or getattr(product, 'model', None) or ''
    if model:
        return model
    return detect_device_model(getattr(product, 'name', '') or '', getattr(product, 'description', '') or '')


def product_terea_newness_tier(product) -> Optional[str]:
    """special = Pearl/Wave; classic = остальные TEREA."""
    if product_catalog_family(product) != 'terea':
        return None
    name = (product.name or '').lower()
    for hint, _score in TEREA_NEWNESS_HINTS:
        if hint in name:
            return 'special'
    return 'classic'


def product_newness_score(product, category=None) -> int:
    """Чем выше — тем «новее» для сортировки в «Новинках»."""
    name = (product.name or '').lower()
    model = resolve_product_model(product) or ''
    score = MODEL_NEWNESS.get(model, 40 if product_catalog_family(product) == 'terea' else 45)

    for hint, bonus in TEREA_NEWNESS_HINTS:
        if hint in name:
            score = max(score, bonus)
            break

    if product.created_at:
        score += min(product.created_at.year - 2020, 5)
    return score
