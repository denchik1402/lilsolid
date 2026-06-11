# -*- coding: utf-8 -*-
"""
Единый стиль названий товаров: IQOS, ILUMA, TEREA, LIL, LIL SOLID — заглавными.
"""
from __future__ import annotations

import re

_BRAND_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r'\blil\s+solid\s+dual\b', re.I), 'LIL SOLID DUAL'),
    (re.compile(r'\blil\s+solid\s+4\.0\b', re.I), 'LIL SOLID 4.0'),
    (re.compile(r'\blil\s+solid\s+3\.0\b', re.I), 'LIL SOLID 3.0'),
    (re.compile(r'\blil\s+solid\b', re.I), 'LIL SOLID'),
    (re.compile(r'\bterea\b', re.I), 'TEREA'),
    (re.compile(r'\biqos\b', re.I), 'IQOS'),
    (re.compile(r'\biluma\b', re.I), 'ILUMA'),
]

_UPPER_TOKENS = frozenset({'TEREA', 'IQOS', 'ILUMA', 'LIL', 'SOLID', 'DUAL', 'KZ'})
_TITLE_WORDS = frozenset({
    'limited', 'edition', 'model', 'anniversary', 'seletti', 'one', 'prime',
    'purple', 'wave', 'silver', 'amber', 'zing', 'turquoise', 'summer', 'yellow',
    'starling', 'pearl', 'sun', 'twilight', 'blue', 'tidal', 'provience',
    'breeze', 'vivid', 'midnight', 'digital', 'leaf', 'green', 'terracotta',
    'garnet', 'red', 'aspen', 'black', 'violet',
})


def _apply_brands(text: str) -> str:
    for pattern, replacement in _BRAND_PATTERNS:
        text = pattern.sub(replacement, text)
    text = re.sub(r'\bILUMA I\b', 'ILUMA i', text)
    return text


def _capitalize_cyrillic(word: str) -> str:
    if not word:
        return word
    if word.isupper() and len(word) > 1:
        return word[0] + word[1:].lower()
    if word.islower():
        return word[0].upper() + word[1:]
    return word


def _capitalize_english_word(word: str) -> str:
    if word.isupper() and len(word) > 1:
        return word.capitalize()
    if word.islower():
        return word.capitalize()
    if word[0].isupper() and word[1:].islower():
        return word
    return word.capitalize()


def normalize_product_name(name: str) -> str:
    """Приводит название товара к единому стилю брендов и регистра."""
    if not name:
        return name
    s = ' '.join(name.split())
    s = _apply_brands(s)

    words = s.split()
    result: list[str] = []
    for word in words:
        upper = word.upper()
        if upper in _UPPER_TOKENS:
            result.append(upper)
            continue
        if re.match(r'^[34]\.0$', word):
            result.append(word)
            continue
        if word.lower() == 'i':
            result.append('i')
            continue
        wl = word.lower()
        if wl in ('standard', 'standart'):
            result.append('Standart')
            continue
        if re.search(r'[а-яё]', word, re.IGNORECASE):
            result.append(_capitalize_cyrillic(word))
            continue
        if wl in _TITLE_WORDS or word.isupper():
            result.append(_capitalize_english_word(word))
            continue
        result.append(_capitalize_english_word(word))

    return ' '.join(result)


def normalize_description_brands(text: str) -> str:
    """Заменяет бренды в HTML-описании на канонический регистр."""
    if not text:
        return text
    return _apply_brands(text)
