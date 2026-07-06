# -*- coding: utf-8 -*-
"""Контент и константы для SEO-блоков."""

DELIVERY_RATES = {
    'moscow_price': 1000,
    'moscow_note': 'курьер по Москве и МО',
    'moscow_same_day': 'Экспресс: доставка сегодня по Москве',
    'moscow_cutoff': '14:00',
    'rf_from': 800,
    'rf_note': 'СДЭК и другие ТК по России',
    'days_moscow': 'сегодня при заказе до 14:00',
    'days_rf': 'от 1–2 дней',
    'warranty_devices': 'Гарантия производителя',
}


def format_delivery_moscow_price(rates=None) -> str:
    """Текст цены доставки по Москве для сайта и SEO."""
    r = rates or DELIVERY_RATES
    price = r.get('moscow_price', 0)
    if price in (0, None, ''):
        return 'от 0 ₽'
    return f'от {int(price)} ₽'


def format_delivery_rf_text(rates=None) -> str:
    """Текст доставки по РФ."""
    r = rates or DELIVERY_RATES
    rf_from = r.get('rf_from')
    if rf_from not in (None, '', 0):
        days = r.get('days_rf', 'от 1–2 дней')
        return f'от {int(rf_from)} ₽ ({days})'
    note = r.get('rf_manager_note') or 'стоимость доставки сообщит менеджер при подтверждении заказа'
    days = r.get('days_rf', 'от 1–2 дней')
    return f'{note} ({days})'
