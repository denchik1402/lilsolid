# -*- coding: utf-8 -*-
"""Длинные SEO-тексты для карточек товаров (2500+ знаков)."""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

from seo_content import DELIVERY_RATES
from seo_utils import (
    SITE,
    CITY_RU,
    _device_line,
    _format_price,
    _is_exclusive,
    _is_lil,
    _is_terea,
    _specs_dict,
    _stick_flavor_text,
    normalize_device_model_name,
)

if TYPE_CHECKING:
    from models import Product


def _plain_len(html: str) -> int:
    return len(re.sub(r'<[^>]+>', '', html or '').strip())


def _color_variants_text(product) -> str:
    from models import Product
    if not product.model:
        return ''
    siblings = Product.query.filter(
        Product.model == product.model,
        Product.id != product.id,
    ).limit(8).all()
    if not siblings:
        return ''
    names = [product.color or product.name]
    names.extend([(p.color or p.name.split()[-1]) for p in siblings if p.color])
    unique = []
    for n in names:
        if n and n not in unique:
            unique.append(n)
    if len(unique) < 2:
        return ''
    return ', '.join(unique[:6])


def _terea_flavor_block(name: str, specs: dict) -> str:
    n = name.lower()
    taste = specs.get('Вкус', '')
    if 'amber' in n or 'amber' in taste.lower():
        return (
            'Amber — насыщенный табачный профиль с лёгкой ореховой нотой. '
            'Подходит тем, кто переходит с крепких сигарет.'
        )
    if 'yellow' in n:
        return 'Yellow — мягкий и сбалансированный табачный вкус, хороший старт для новичков.'
    if 'blue' in n or 'turquoise' in n or 'zing' in n:
        return 'Освежающий ментоловый профиль с прохладой — для любителей ментола.'
    if 'pearl' in n or 'purple' in n or 'wave' in n:
        return 'Линейка Pearl / капсульные вкусы — активируйте капсулу щелчком для аромата.'
    if 'silver' in n:
        return 'Silver — лёгкий табачный вкус с низкой крепостью.'
    return taste or 'Классический табачный или ментоловый профиль TEREA для IQOS ILUMA.'


def build_product_pdp_seo(product: 'Product') -> str:
    """Полный HTML для вкладки «Описание» на PDP (цель 2500+ знаков)."""
    intro_db = product.get_intro_text() if product else ''
    if _plain_len(intro_db) >= 2200:
        return intro_db

    name = (product.name or '').strip()
    price = _format_price(product.price)
    specs = _specs_dict(product)
    category = product.category
    color = (product.color or '').strip()
    color_part = f' в оттенке <strong>{color}</strong>' if color else ''
    moscow = DELIVERY_RATES['moscow_price']
    rf = DELIVERY_RATES['rf_from']
    same_day = DELIVERY_RATES.get('moscow_same_day', 'доставка сегодня по Москве')

    if _is_terea(product, category):
        flavor = _stick_flavor_text(product)
        flavor_detail = _terea_flavor_block(name, specs)
        strength = specs.get('Крепость', '')
        strength_line = f' Крепость: {strength}.' if strength else ''
        return (
            f'<h2>{name}: купить в {CITY_RU} с доставкой</h2>'
            f'<p><strong>{name}</strong> — оригинальные стики TEREA для IQOS ILUMA.{color_part} '
            f'{flavor}.{strength_line} В блоке 20 стиков, оригинальная упаковка Terea KZ. '
            f'Технология SMARTCORE: нагреватель внутри стика, без лезвия в устройстве.</p>'
            f'<h2>Вкусовой профиль</h2>'
            f'<p>{flavor_detail} Стики TEREA не совместимы с IQOS 3, Lil Solid и HEETS-устройствами — '
            f'только с линейкой <a href="/catalog/iqos-iluma">IQOS ILUMA</a>.</p>'
            f'<h2>Как выбрать вкус TEREA</h2>'
            f'<p>Если раньше курили сигареты — начните с Amber или Yellow. Любителям ментола подойдут '
            f'Blue, Turquoise или Zing Wave. Для экспериментов возьмите 2–3 блока разных вкусов в одном заказе. '
            f'Не уверены? Напишите консультанту в чат на сайте или в Telegram.</p>'
            f'<h2>Цена и наличие</h2>'
            f'<p>Цена в {SITE}: <strong>{price} ₽</strong> за блок. Актуальное наличие — на этой странице. '
            f'Оформите бронь или покупку в один клик.</p>'
            f'<h2>Доставка по Москве и России</h2>'
            f'<p><strong>{same_day}</strong> при заказе до {DELIVERY_RATES.get("moscow_cutoff", "14:00")}. '
            f'Курьер по Москве и МО — от {moscow} ₽. По России — от {rf} ₽, {DELIVERY_RATES["days_rf"]}. '
            f'Оплата при получении.</p>'
            f'<h2>Хранение стиков TEREA</h2>'
            f'<p>Храните в сухом месте, вдали от солнца. Используйте до даты на упаковке. '
            f'Рекомендуем заказать устройство ILUMA, если ещё не пользуетесь — '
            f'<a href="/catalog/iqos-iluma">каталог IQOS ILUMA</a>.</p>'
            f'<h2>Почему покупать в {SITE}</h2>'
            f'<p>Оригинальная продукция, {same_day}, консультация в онлайн-чате. '
            f'Работаем с 2020 года, только сертифицированные стики Terea KZ с маркировкой.</p>'
            f'<h2>Совместимость</h2>'
            f'<p>TEREA подходят только к IQOS Iluma i One, Standart и Prime. '
            f'Не используйте с классическим IQOS 3 или Lil Solid — формат нагрева другой.</p>'
            f'<h2>Миксы и рекомендации</h2>'
            f'<p>Опытные пользователи чередуют табачные и ментоловые вкусы в течение дня. '
            f'Для вечера подойдут Pearl с капсулой, для утра — Amber или Yellow. '
            f'Закажите несколько блоков — доставка {same_day} по Москве.</p>'
            f'<h2>Что нового в линейке TEREA 2025</h2>'
            f'<p>Линейка Terea KZ постоянно пополняется: сезонные лимитированные серии, обновлённая упаковка '
            f'с QR-маркировкой «Честный знак». Формат SMARTCORE остаётся единым для всех IQOS ILUMA — '
            f'стики {name.split()[0] if name else "TEREA"} совместимы с One, Standart и Prime без адаптеров.</p>'
            f'<h2>TEREA vs HEETS</h2>'
            f'<p>HEETS — для устройств с лезвием (IQOS 3, Lil Solid). TEREA — только для ILUMA: нагреватель '
            f'встроен в стик, устройство не требует чистки. Нельзя смешивать форматы — при переходе на ILUMA '
            f'закажите новый девайс в <a href="/catalog/iqos-iluma">каталоге</a> и блоки TEREA.</p>'
            f'<h2>Как оформить заказ {name} в {CITY_RU}</h2>'
            f'<p>Добавьте блок в корзину или нажмите «Купить в 1 клик». Укажите адрес — менеджер перезвонит '
            f'для подтверждения. При заказе до {DELIVERY_RATES.get("moscow_cutoff", "14:00")} — {same_day.lower()}. '
            f'Оплата курьеру при получении, без предоплаты.</p>'
        )

    if _is_lil(product, category):
        line = _device_line(product)
        variants = _color_variants_text(product)
        variants_block = (
            f'<h2>Доступные цвета</h2><p>В каталоге {line}: {variants}. '
            f'Переключайте оттенок на карточке товара.</p>'
        ) if variants else ''
        dual = 'DUAL' in name.upper()
        return (
            f'<h2>{name}: купить в {CITY_RU}</h2>'
            f'<p><strong>{name}</strong> — оригинальное устройство {line}{color_part}. '
            f'Совместимо со стиками HEETS и Fiit. {"Комплект с зарядным кейсом." if dual else "Компактный моноблок."} '
            f'Проверенная эргономика, доступная цена.</p>'
            f'<h2>Особенности {line}</h2>'
            f'<p>Два режима интенсивности сеанса, съёмный нагревательный элемент, простое обслуживание. '
            f'Подходит для первого знакомства с нагреванием табака или как запасное устройство.</p>'
            f'{variants_block}'
            f'<h2>Цена и заказ</h2>'
            f'<p><strong>{price} ₽</strong> в {SITE}. Бронь на сайте, {same_day}, по России от {rf} ₽.</p>'
            f'<h2>Доставка</h2>'
            f'<p>Москва и МО — от {moscow} ₽. Россия — от {rf} ₽, {DELIVERY_RATES["days_rf"]}. Оплата при получении.</p>'
            f'<h2>Гарантия и оригинальность</h2>'
            f'<p>Устройство в заводской упаковке с гарантией. {SITE} — только оригинальная продукция.</p>'
        )

    line = _device_line(product)
    m = normalize_device_model_name(product.model or '')
    variants = _color_variants_text(product)
    if 'one' in m.lower():
        form = 'Компактный моноблок без зарядного кейса — удобно носить в кармане.'
        compare = 'One компактнее Standart, но без кейса.'
    elif 'standart' in m.lower() or 'standard' in m.lower():
        form = 'Держатель и зарядный кейс — оптимальный баланс для ежедневного использования.'
        compare = 'Standart — золотая середина между One и Prime.'
    elif 'prime' in m.lower():
        form = 'Премиальный корпус, увеличенная ёмкость кейса.'
        compare = 'Prime — флагман линейки Iluma i.'
    else:
        form = 'Технология SMARTCORE INDUCTION™ без лезвия.'
        compare = 'Сравните One, Standart и Prime в каталоге.'

    variants_block = ''
    if variants:
        variants_block = f'<h2>Цвета {m}</h2><p>Доступны: {variants}.</p>'

    return (
        f'<h2>{name}: купить в {CITY_RU} с быстрой доставкой</h2>'
        f'<p><strong>{name}</strong> — оригинальное устройство {line}{color_part}. '
        f'SMARTCORE INDUCTION™: нагрев табака внутри стика TEREA, без лезвия. {form}</p>'
        f'{variants_block}'
        f'<h2>Какую модель выбрать</h2><p>{compare}</p>'
        f'<h2>Цена</h2><p><strong>{price} ₽</strong> в {SITE}. Покупка в 1 клик, бронь на сайте.</p>'
        f'<h2>Доставка</h2><p>{same_day}. Москва — {moscow} ₽, Россия — от {rf} ₽.</p>'
        f'<h2>Стики TEREA</h2><p>Добавьте блоки в <a href="/catalog/terea-sticks">каталоге стиков</a>.</p>'
        f'<h2>Гарантия</h2><p>Заводская упаковка, гарантия производителя. {SITE} — только оригинал.</p>'
    )


def get_product_pdp_seo(product: 'Product') -> str:
    if not product:
        return ''
    return build_product_pdp_seo(product)
