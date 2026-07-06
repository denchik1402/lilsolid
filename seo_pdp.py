# -*- coding: utf-8 -*-
"""Длинные SEO-тексты для карточек товаров (2500+ знаков, структура как у лидеров ниши)."""
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

_COLOR_PHRASES = (
    'Breeze Blue', 'Midnight Black', 'Vivid Terracotta', 'Digital Violet',
    'Moss Green', 'Pebble Grey', 'Leaf Green', 'Garnet Red', 'Aspen Green',
    'White Chrome', 'Black Titanium', 'Green Cobalt', 'Red Copper',
)

_COLOR_BLURBS: dict[str, str] = {
    'breeze blue': 'свежий, лёгкий и универсальный оттенок — отлично смотрится в повседневном использовании',
    'midnight black': 'классический тёмный вариант для тех, кто предпочитает строгий стиль',
    'vivid terracotta': 'яркий тёплый оттенок для любителей выразительных акцентов',
    'digital violet': 'современный фиолетовый цвет с технологичным характером',
    'moss green': 'природный зелёный оттенок в актуальной палитре ILUMA',
    'pebble grey': 'сдержанный серый — универсальный выбор на каждый день',
    'leaf green': 'насыщенный зелёный для выразительного образа',
    'garnet red': 'глубокий красный с премиальным характером',
    'aspen green': 'светло-зелёный оттенок в современной гамме',
    'white chrome': 'светлый хромированный корпус — чистый и технологичный вид',
    'black titanium': 'титановый чёрный с матовой фактурой',
    'green cobalt': 'насыщенный кобальтовый зелёный',
    'red copper': 'тёплый медно-красный оттенок',
}


def _seo_city_in() -> str:
    try:
        import config as _cfg
        city = getattr(_cfg, 'SITE_CITY', None) or CITY_RU
    except ImportError:
        city = CITY_RU
    return city_prepositional(city)


def _fix_city_grammar(html: str) -> str:
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


def _pdp_sections(*sections: str) -> str:
    if not sections:
        return ''
    return f'<div class="pdp-seo-sections">{"".join(sections)}</div>'


def _pdp_ul(items: list[str]) -> str:
    if not items:
        return ''
    return '<ul class="pdp-seo-list">' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'


def _plain_len(html: str) -> int:
    return len(re.sub(r'<[^>]+>', '', html or '').strip())


def _parse_color_en(name: str) -> str:
    n = name or ''
    for phrase in sorted(_COLOR_PHRASES, key=len, reverse=True):
        if phrase.lower() in n.lower():
            return phrase
    return ''


def _color_blurb(color_en: str) -> str:
    if not color_en:
        return 'стильный оттенок корпуса, подчёркивающий индивидуальность устройства'
    return _COLOR_BLURBS.get(color_en.lower(), 'популярный цвет в линейке IQOS ILUMA')


def _iluma_model_key(m: str) -> str:
    ml = (m or '').lower()
    if 'one' in ml:
        return 'one'
    if 'standart' in ml or 'standard' in ml:
        return 'standart'
    if 'prime' in ml:
        return 'prime'
    return 'generic'


def _iluma_model_label(model_key: str) -> str:
    return {
        'one': 'IQOS Iluma i One',
        'standart': 'IQOS Iluma i Standart',
        'prime': 'IQOS Iluma i Prime',
    }.get(model_key, 'IQOS ILUMA')


def _sibling_color_names(product) -> list[str]:
    from models import Product
    colors: list[str] = []
    current = _parse_color_en(product.name or '') or (product.color or '')
    if current:
        colors.append(current)
    if not product.model:
        return colors
    siblings = Product.query.filter(
        Product.model == product.model,
        Product.id != product.id,
    ).limit(12).all()
    for p in siblings:
        c = _parse_color_en(p.name or '') or (p.color or '')
        if c and c not in colors:
            colors.append(c)
    return colors[:8]


def _color_compare_section(model_label: str, colors: list[str], current_color: str) -> str:
    if len(colors) < 2:
        return ''
    items = []
    for c in colors:
        blurb = _color_blurb(c)
        prefix = '<strong>Текущий выбор — </strong>' if c == current_color else ''
        items.append(f'{prefix}<strong>{c}</strong> — {blurb}.')
    title = f'{model_label}: сравнение расцветок'
    if current_color:
        title = f'{model_label} 2025: расцветки ({", ".join(colors[:4])}{"…" if len(colors) > 4 else ""})'
    return _pdp_section(
        title,
        f'<p>Модельный ряд {model_label} представлен несколькими популярными цветами. '
        f'На сайте можно выбрать оттенок и оформить заказ.</p>{_pdp_ul(items)}',
    )


def _iluma_usage_section(model_label: str) -> str:
    return _pdp_section(
        f'{model_label}: инструкция по использованию',
        _pdp_ul([
            'Полностью зарядите устройство перед первым запуском.',
            'Вставьте стик TEREA в нагреватель до ограничителя.',
            'Нажмите и удерживайте кнопку до вибрации и включения индикатора.',
            'Дождитесь сигнала готовности и начните сессию.',
            'После окончания аккуратно извлеките стик; при необходимости дайте устройству остыть.',
        ])
        + '<p>SMARTCORE INDUCTION™ не требует лезвия и сложной чистки — уход сводится к зарядке и аккуратному использованию.</p>',
    )


def _iluma_features(model_key: str, color_en: str) -> list[str]:
    color_line = (
        f'Стильный цвет <strong>{color_en}</strong> — {_color_blurb(color_en)}.'
        if color_en else 'Современный дизайн корпуса в актуальной палитре ILUMA.'
    )
    common = [
        'Технология <strong>SMARTCORE INDUCTION™</strong> — нагрев табака внутри стика TEREA, без лезвия.',
        'Ровный нагрев, минимум запаха и комфорт при каждой сессии.',
        color_line,
    ]
    if model_key == 'one':
        return common + [
            'Компактный форм‑фактор «one device» — держатель и зарядка в одном корпусе, удобно носить каждый день.',
            'Простое управление — минимум кнопок, понятная индикация заряда и статуса нагрева.',
            'Оптимальная автономность для повседневного ритма без частой подзарядки.',
        ]
    if model_key == 'standart':
        return common + [
            'Держатель и зарядный кейс — золотая середина между компактным One и флагманским Prime.',
            'Увеличенный запас сессий за счёт кейса — удобно для полного рабочего дня.',
            'Сбалансированный размер и эргономика для ежедневного использования.',
        ]
    if model_key == 'prime':
        return common + [
            'Премиальный корпус и увеличенная ёмкость зарядного кейса.',
            'Максимальная автономность в линейке Iluma i — для активного ритма без подзарядки.',
            'Флагманские материалы и статусная подача модели.',
        ]
    return common + [
        'Совместимость только со стиками TEREA для IQOS ILUMA.',
        'Оригинальная продукция в заводской упаковке.',
    ]


def _iluma_whats_new(model_key: str, model_label: str, color_en: str) -> str:
    form = {
        'one': 'максимально простом и компактном формате «всё в одном»',
        'standart': 'формате держателя с зарядным кейсом — баланс размера и автономности',
        'prime': 'премиальном формате с увеличенным кейсом и флагманской автономностью',
    }.get(model_key, 'современном формате нагревания табака')
    color_part = f' в оттенке <strong>{color_en}</strong>' if color_en else ''
    return _pdp_section(
        f'Купить {model_label}: что нового в линейке 2025',
        f'<p>Линейка <strong>{model_label} 2025</strong> получила обновлённый дизайн корпуса, '
        f'улучшенную автономность и более стабильный нагрев. Устройство рассчитано на пользователей, '
        f'которым важен привычный опыт IQOS в {form}. '
        f'{model_label}{color_part} обеспечивает ровное нагревание стика TEREA и комфорт при каждом использовании.</p>',
    )


def _iluma_audience(model_key: str, model_label: str, color_en: str) -> str:
    color_part = f' <strong>{color_en}</strong>' if color_en else ''
    targets = {
        'one': [
            'Компактный формат без отдельного кейса и держателя.',
            'Стильный дизайн и выразительный цвет корпуса.',
            'Простое управление без лишних настроек.',
            'Достаточную автономность на весь день.',
        ],
        'standart': [
            'Баланс компактности и автономности с зарядным кейсом.',
            'Ежедневное использование без частой подзарядки.',
            'Классический формат IQOS с держателем и кейсом.',
            'Надёжную работу SMARTCORE INDUCTION™.',
        ],
        'prime': [
            'Максимальную автономность и премиальный дизайн.',
            'Активный образ жизни без привязки к розетке.',
            'Флагманский статус и увеличенный зарядный кейс.',
            'Стабильный вкус и комфорт длительных сессий.',
        ],
    }.get(model_key, [
        'Переход на нагревание табака без горения.',
        'Оригинальное устройство IQOS ILUMA со стиками TEREA.',
        'Простой уход без лезвия и чистки.',
    ])
    return _pdp_section(
        f'Обзор {model_label}{color_part}: кому подойдёт',
        f'<p>Обзор показывает, что устройство подходит тем, кто ищет:</p>{_pdp_ul(targets)}'
        f'<p>{model_label} — удачный выбор как для опытных пользователей IQOS, '
        f'так и для тех, кто только переходит на систему нагревания стиков.</p>',
    )


def _why_buy_section(product_name: str) -> str:
    return _pdp_section(
        f'Почему стоит купить {product_name} у нас',
        _pdp_ul([
            f'Официальные устройства и актуальные модели IQOS ILUMA в {SITE}.',
            'Консультации и помощь в подборе модели и расцветки.',
            'Постоянное наличие популярных цветов и стиков TEREA.',
            f'Удобное оформление на сайте — корзина и покупка в 1 клик.',
        ]),
    )


def _order_section(product_name: str, price: str, city_in: str) -> str:
    return _pdp_section(
        f'{product_name}: заказ в {city_in}',
        f'<p>У нас вы можете купить <strong>{product_name}</strong> в {city_in} с удобным оформлением на сайте. '
        f'Актуальная цена — <strong>{price} ₽</strong>. Добавьте устройство в корзину или нажмите «Покупка в 1 клик» — '
        f'менеджер свяжется при необходимости уточнения деталей. '
        f'Условия и сроки доставки — в блоке «Доставка» на этой странице.</p>'
        f'<p>Стики TEREA — в <a href="/catalog/terea-sticks">каталоге стиков</a>.</p>',
    )


def _build_iluma_device_seo(
    product: 'Product',
    name: str,
    price: str,
    city_in: str,
    m: str,
) -> str:
    model_key = _iluma_model_key(m)
    model_label = _iluma_model_label(model_key)
    color_en = _parse_color_en(name)
    color_ru = (product.color or '').strip()
    colors = _sibling_color_names(product)

    lead = (
        f'<p><strong>{name}</strong> — обновлённая модель линейки IQOS ILUMA с технологией SMARTCORE INDUCTION™ '
        f'и современным дизайном. '
        f'{"Устройство выполнено в оттенке <strong>" + color_en + "</strong> — " + _color_blurb(color_en) + "." if color_en else ""} '
        f'Идеально подходит для повседневного использования со стиками TEREA. '
        f'Заказывайте {name} в {SITE} — оформление займёт пару минут.</p>'
    )

    sections = [
        _iluma_whats_new(model_key, model_label, color_en),
        _pdp_section(
            f'Особенности {model_label}' + (f' {color_en}' if color_en else ''),
            _pdp_ul(_iluma_features(model_key, color_en)),
        ),
        _order_section(name, price, city_in),
        _color_compare_section(model_label, colors, color_en),
        _iluma_usage_section(model_label),
        _iluma_audience(model_key, model_label, color_en),
        _why_buy_section(name),
    ]
    if model_key == 'one':
        sections.insert(3, _pdp_section(
            'Какую модель ILUMA выбрать',
            '<p><strong>Iluma i One</strong> — компактный моноблок без кейса. '
            '<strong>Standart</strong> — держатель и кейс, баланс автономности. '
            '<strong>Prime</strong> — флагман с максимальным запасом заряда. '
            'Сравните модели в <a href="/catalog/iqos-iluma">каталоге IQOS ILUMA</a>.</p>',
        ))

    return _pdp_article(
        _pdp_header(f'{name}: купить в {city_in} с быстрой доставкой'),
        _pdp_lead(lead),
        _pdp_sections(*sections),
    )


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


def _build_terea_seo(
    product: 'Product',
    name: str,
    price: str,
    city_in: str,
    color_part: str,
    specs: dict,
) -> str:
    flavor = _stick_flavor_text(product)
    flavor_detail = _terea_flavor_block(name, specs)
    strength = specs.get('Крепость', '')
    strength_line = f' Крепость: {strength}.' if strength else ''

    lead = (
        f'<p><strong>{name}</strong> — оригинальные стики TEREA для IQOS ILUMA.{color_part} '
        f'{flavor}.{strength_line} В блоке 20 стиков, заводская упаковка Terea KZ с маркировкой. '
        f'Технология SMARTCORE: нагреватель внутри стика, устройство ILUMA не требует лезвия и чистки. '
        f'Закажите {name} в {SITE} — подберём вкусы и поможем с оформлением.</p>'
    )

    sections = [
        _pdp_section('Вкусовой профиль', f'<p>{flavor_detail} Стики TEREA совместимы только с '
                     f'<a href="/catalog/iqos-iluma">IQOS ILUMA</a> — не подходят для IQOS 3, Lil Solid и HEETS-устройств.</p>'),
        _pdp_section(
            'Как выбрать вкус TEREA',
            _pdp_ul([
                'Новичкам — Amber или Yellow: сбалансированный табачный профиль.',
                'Любителям ментола — Blue, Turquoise, Zing Wave.',
                'Для экспериментов — 2–3 блока разных вкусов в одном заказе.',
                'Не уверены? Напишите консультанту в Telegram или на сайте.',
            ]),
        ),
        _order_section(name, price, city_in),
        _pdp_section(
            'Совместимость и хранение',
            _pdp_ul([
                'TEREA — только для IQOS Iluma i One, Standart и Prime.',
                'HEETS и Fiit — для LIL SOLID и классических IQOS с лезвием; форматы не смешиваются.',
                'Храните блоки в сухом месте, вдали от солнца, до даты на упаковке.',
            ]),
        ),
        _pdp_section(
            'TEREA vs HEETS',
            '<p>HEETS — для устройств с лезвием. TEREA — нагреватель встроен в стик. '
            'При переходе на ILUMA закажите устройство в <a href="/catalog/iqos-iluma">каталоге</a> '
            'и блоки TEREA подходящих вкусов.</p>',
        ),
        _pdp_section(
            'Миксы и рекомендации',
            '<p>Опытные пользователи чередуют табачные и ментоловые вкусы в течение дня. '
            'Для вечера — Pearl с капсулой, для утра — Amber или Yellow.</p>',
        ),
        _why_buy_section(name),
    ]

    return _pdp_article(
        _pdp_header(f'{name}: купить в {city_in} с доставкой'),
        _pdp_lead(lead),
        _pdp_sections(*sections),
    )


def _build_lil_seo(
    product: 'Product',
    name: str,
    price: str,
    city_in: str,
    color_part: str,
) -> str:
    line = _device_line(product)
    dual = 'DUAL' in name.upper()
    colors = _sibling_color_names(product)

    lead = (
        f'<p><strong>{name}</strong> — оригинальное устройство {line}{color_part}. '
        f'Совместимо со стиками HEETS и Fiit. '
        f'{"Комплект с зарядным кейсом DUAL — два режима интенсивности." if dual else "Компактный моноблок — удобен для ежедневного ношения."} '
        f'Проверенная эргономика и доступная цена. Закажите в {SITE} онлайн или в 1 клик.</p>'
    )

    sections = [
        _pdp_section(
            f'Особенности {line}',
            _pdp_ul([
                'Два режима интенсивности сеанса на моделях DUAL.',
                'Съёмный нагревательный элемент и простое обслуживание.',
                'Совместимость со стиками HEETS и Fiit.',
                'Оригинальная продукция в заводской упаковке.',
                'Подходит для первого знакомства с нагреванием табака.',
            ]),
        ),
        _order_section(name, price, city_in),
    ]
    if len(colors) >= 2:
        items = [f'<strong>{c}</strong> — {_color_blurb(c)}.' for c in colors]
        sections.append(_pdp_section(
            f'Цвета {line}',
            f'<p>В каталоге доступны оттенки:</p>{_pdp_ul(items)}',
        ))
    sections.append(_why_buy_section(name))

    return _pdp_article(
        _pdp_header(f'{name}: купить в {city_in}'),
        _pdp_lead(lead),
        _pdp_sections(*sections),
    )


def build_product_pdp_seo(product: 'Product') -> str:
    """Полный HTML для SEO-блока на PDP (цель 2500+ знаков)."""
    intro_db = product.get_intro_text() if product else ''
    if _plain_len(intro_db) >= 2200:
        return _fix_city_grammar(intro_db)

    name = (product.name or '').strip()
    price = _format_price(product.price)
    specs = _specs_dict(product)
    category = product.category
    color = (product.color or '').strip()
    color_part = f' в оттенке <strong>{color}</strong>' if color else ''
    city_in = _seo_city_in()

    if _is_terea(product, category):
        return _build_terea_seo(product, name, price, city_in, color_part, specs)

    if _is_lil(product, category):
        return _build_lil_seo(product, name, price, city_in, color_part)

    if _is_exclusive(product, category):
        line = _device_line(product)
        return _pdp_article(
            _pdp_header(f'{name}: купить в {city_in} с быстрой доставкой'),
            _pdp_lead(
                f'<p><strong>{name}</strong> — эксклюзивная модель {line}{color_part}. '
                f'Лимитированная серия IQOS ILUMA, оригинальная упаковка. '
                f'Цена — <strong>{price} ₽</strong>. Оформите заказ в {SITE}.</p>'
            ),
            _pdp_sections(
                _order_section(name, price, city_in),
                _why_buy_section(name),
            ),
        )

    m = normalize_device_model_name(product.model or '')
    cat_slug = (category.slug or '') if category else ''
    if 'iluma' in (name + m + _device_line(product) + cat_slug).lower():
        return _build_iluma_device_seo(product, name, price, city_in, m)

    return _build_iluma_device_seo(product, name, price, city_in, m)


def get_product_pdp_seo(product: 'Product') -> str:
    if not product:
        return ''
    return build_product_pdp_seo(product)
