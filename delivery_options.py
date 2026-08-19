# -*- coding: utf-8 -*-
"""Варианты доставки на оформлении заказа."""
from __future__ import annotations

DELIVERY_OPTIONS = {
    'tk': {
        'label': 'Службой доставки или ТК',
        'price': 500,
    },
    'courier_msk': {
        'label': 'Курьер по Москве',
        'price': 700,
    },
}

DEFAULT_DELIVERY = 'tk'


def normalize_delivery_code(raw) -> str:
    code = (raw or '').strip().lower().replace('-', '_')
    if code in DELIVERY_OPTIONS:
        return code
    if code in ('delivery', 'pickup', 'самовывоз', ''):
        return DEFAULT_DELIVERY
    if 'курьер' in code or 'msk' in code or 'moscow' in code:
        return 'courier_msk'
    if 'тк' in code or 'служб' in code:
        return 'tk'
    return DEFAULT_DELIVERY


def delivery_fee(code) -> int:
    return int(DELIVERY_OPTIONS[normalize_delivery_code(code)]['price'])


def delivery_label(code) -> str:
    return DELIVERY_OPTIONS[normalize_delivery_code(code)]['label']


def delivery_choices():
    return [
        (code, opt['label'], opt['price'])
        for code, opt in DELIVERY_OPTIONS.items()
    ]


def format_delivery_line(code, fee=None) -> str:
    code = normalize_delivery_code(code)
    price = int(fee) if fee is not None else delivery_fee(code)
    return f"{delivery_label(code)} — {price} ₽"
