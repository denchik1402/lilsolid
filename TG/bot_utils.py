# -*- coding: utf-8 -*-
"""
Утилиты для Telegram-бота: расчёт прибыли из Product.cost на сайте, маршруты и т.д.
"""
import urllib.parse


def calc_profit_for_orders(orders):
    """
    Считает прибыль по заказам. Цены и себестоимость берутся из Product на сайте.
    """
    from app import app
    from models import Product, OrderItem

    total_revenue = 0
    total_cost = 0

    with app.app_context():
        for order in orders:
            if order.status == 'cancelled':
                continue
            total_revenue += order.total_amount
            for item in order.items:
                cost_per_unit = None
                if item.product and hasattr(item.product, 'cost'):
                    cost_per_unit = item.product.cost
                if cost_per_unit is None:
                    cost_per_unit = item.price * 0.6  # fallback ~60%
                total_cost += cost_per_unit * item.quantity

    return total_revenue - total_cost, total_revenue, total_cost


def build_yandex_route_url(addresses):
    """
    Строит URL для Яндекс.Карт/Навигатора с маршрутом по адресам.
    https://yandex.ru/maps/?rtext=addr1~addr2~addr3
    Для Москвы: если адрес без города — добавляем «Москва, ».
    """
    if not addresses:
        return None
    result = []
    for a in addresses:
        if not a:
            continue
        addr = str(a).strip()
        addr_lower = addr.lower()
        if addr and 'москва' not in addr_lower and 'мск' not in addr_lower and 'moscow' not in addr_lower:
            addr = f"Москва, {addr}"
        result.append(urllib.parse.quote(addr))
    if not result:
        return None
    return 'https://yandex.ru/maps/?rtext=' + '~'.join(result)


def format_price(val):
    if val is None:
        return '0'
    return "{:,.0f}".format(float(val)).replace(",", " ")
