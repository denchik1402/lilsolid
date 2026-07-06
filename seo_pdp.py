# -*- coding: utf-8 -*-
"""Длинные SEO-тексты для карточек товаров (2500+ знаков)."""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

from seo_content import DELIVERY_RATES, format_delivery_moscow_price, format_delivery_rf_text
from seo_utils import (
    SITE,
    CITY_RU,
    city_prepositional,
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


def _seo_city_in() -> str:
    try:
        import config as _cfg
        city = getattr(_cfg, 'SITE_CITY', None) or CITY_RU
    except ImportError:
        city = CITY_RU
    return city_prepositional(city)


def _fix_city_grammar(html: str) -> str:
    """Исправляет «в Москва» в сохранённых SEO-текстах из БД."""
    if not html:
        return html
    city_in = _seo_city_in()
    for wrong, right in (
        (f'в {CITY_RU}', f'в {city_in}'),
        ('в Москва', 'в Москве'),
        ('в москва', 'в Москве'),
    ):
        html = html.replace(wrong, right)
    return html


def _pdp_article(*parts: str) -> str:
    return '<article class="pdp-seo-article">' + ''.join(parts) + '</article>'


def _pdp_header(seo_h2: str) -> str:
    return f'<header class="pdp-seo-header"><h2 class="pdp-seo-h2">{seo_h2}</h2></header>'


def _pdp_lead(html: str) -> str:
    body = html if html.strip().startswith('<') else f'<p>{html}</p>'
    return f'<div class="pdp-seo-lead">{body}</div>'


def _pdp_section(title: str, body: str) -> str:
    body_html = body if body.strip().startswith('<') else f'<p>{body}</p>'
    return (
        f'<section class="pdp-seo-section">'
        f'<h3 class="pdp-seo-section-title">{title}</h3>'
        f'<div class="pdp-seo-section-body">{body_html}</div>'
        f'</section>'
    )


def _pdp_facts(*items: tuple[str, str]) -> str:
    cards = ''.join(
        f'<div class="pdp-seo-fact">'
        f'<span class="pdp-seo-fact-label">{label}</span>'
        f'<span class="pdp-seo-fact-value">{value}</span>'
        f'</div>'
        for label, value in items
    )
    return f'<div class="pdp-seo-facts">{cards}</div>'


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
        return _fix_city_grammar(intro_db)

    name = (product.name or '').strip()
    price = _format_price(product.price)
    specs = _specs_dict(product)
    category = product.category
    color = (product.color or '').strip()
    color_part = f' в оттенке <strong>{color}</strong>' if color else ''
    moscow = format_delivery_moscow_price()
    rf = format_delivery_rf_text()
    same_day = DELIVERY_RATES.get('moscow_same_day', 'доставка сегодня по Москве')
    city_in = _seo_city_in()

    if _is_terea(product, category):
        flavor = _stick_flavor_text(product)
        flavor_detail = _terea_flavor_block(name, specs)
        strength = specs.get('Крепость', '')
        strength_line = f' Крепость: {strength}.' if strength else ''
        return (
            f'<h2>{name}: купить в {city_in} с доставкой</h2>'
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
            f'<h2>Хранение стиков TEREA</h2>'
            f'<p>Храните в сухом месте, вдали от солнца. Используйте до даты на упаковке. '
            f'Рекомендуем заказать устройство ILUMA, если ещё не пользуетесь — '
            f'<a href="/catalog/iqos-iluma">каталог IQOS ILUMA</a>.</p>'
            f'<h2>Почему покупать в {SITE}</h2>'
            f'<p>Оригинальная продукция, консультация в онлайн-чате. '
            f'Работаем с 2020 года, только сертифицированные стики Terea KZ с маркировкой.</p>'
            f'<h2>Совместимость</h2>'
            f'<p>TEREA подходят только к IQOS Iluma i One, Standart и Prime. '
            f'Не используйте с классическим IQOS 3 или Lil Solid — формат нагрева другой.</p>'
            f'<h2>Миксы и рекомендации</h2>'
            f'<p>Опытные пользователи чередуют табачные и ментоловые вкусы в течение дня. '
            f'Для вечера подойдут Pearl с капсулой, для утра — Amber или Yellow. '
            f'Закажите несколько блоков разных вкусов в одном заказе.</p>'
            f'<h2>Что нового в линейке TEREA 2025</h2>'
            f'<p>Линейка Terea KZ постоянно пополняется: сезонные лимитированные серии, обновлённая упаковка '
            f'с QR-маркировкой «Честный знак». Формат SMARTCORE остаётся единым для всех IQOS ILUMA — '
            f'стики {name.split()[0] if name else "TEREA"} совместимы с One, Standart и Prime без адаптеров.</p>'
            f'<h2>TEREA vs HEETS</h2>'
            f'<p>HEETS — для устройств с лезвием (IQOS 3, Lil Solid). TEREA — только для ILUMA: нагреватель '
            f'встроен в стик, устройство не требует чистки. Нельзя смешивать форматы — при переходе на ILUMA '
            f'закажите новый девайс в <a href="/catalog/iqos-iluma">каталоге</a> и блоки TEREA.</p>'
            f'<h2>Как оформить заказ {name} в {city_in}</h2>'
            f'<p>Добавьте блок в корзину или нажмите «Купить в 1 клик». Менеджер перезвонит '
            f'для подтверждения заказа.</p>'
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
            f'<h2>{name}: купить в {city_in}</h2>'
            f'<p><strong>{name}</strong> — оригинальное устройство {line}{color_part}. '
            f'Совместимо со стиками HEETS и Fiit. {"Комплект с зарядным кейсом." if dual else "Компактный моноблок."} '
            f'Проверенная эргономика, доступная цена.</p>'
            f'<h2>Особенности {line}</h2>'
            f'<p>Два режима интенсивности сеанса, съёмный нагревательный элемент, простое обслуживание. '
            f'Подходит для первого знакомства с нагреванием табака или как запасное устройство.</p>'
            f'{variants_block}'
            f'<h2>Цена и заказ</h2>'
            f'<p><strong>{price} ₽</strong> в {SITE}. Бронь на сайте, покупка в 1 клик.</p>'
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
        form = 'Подходит для ежедневного использования — без лезвия и сложного обслуживания.'
        compare = 'Сравните One, Standart и Prime в каталоге.'

    sections = []
    if variants:
        sections.append(_pdp_section(f'Цвета {m}', f'Доступны: {variants}.'))
    sections.append(_pdp_section('Какую модель выбрать', compare))

    intro = (
        f'<p><strong>{name}</strong> — оригинальное устройство {line}{color_part}. '
        f'SMARTCORE INDUCTION™: нагрев табака внутри стика TEREA, без лезвия. {form}</p>'
    )

    return _pdp_article(
        _pdp_header(f'{name}: купить в {city_in} с быстрой доставкой'),
        _pdp_lead(intro),
        f'<div class="pdp-seo-sections">{"".join(sections)}</div>' if sections else '',
        _pdp_facts(
            ('Цена', f'<strong>{price} ₽</strong> · {SITE}. Покупка в 1 клик, бронь на сайте.'),
            ('Стики TEREA', 'Добавьте блоки в <a href="/catalog/terea-sticks">каталоге стиков</a>.'),
        ),
    )


def get_product_pdp_seo(product: 'Product') -> str:
    if not product:
        return ''
    return build_product_pdp_seo(product)
