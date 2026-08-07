# -*- coding: utf-8 -*-
"""Ролевые SEO-пресеты: коммерция по всему каталогу + усиление ILUMA/илюма.

Роли:
  hub        — lilstore.ru: приоритет продаж IQOS ILUMA (илюма), полный каталог
  premium    — iqos-store.ru: премиум ILUMA + полный каталог
  lil        — lilsolid.ru: LIL SOLID + ILUMA/стики
  specialist — iluma-iqos.ru: специалист ILUMA/TEREA + полный каталог
"""
from __future__ import annotations

CITY = 'Москва'

# Разговорные / транслит-запросы (Яндекс)
ILUMA_VARIANTS = [
    'илюма', 'ильюма', 'iluma', 'IQOS ILUMA', 'iqos iluma',
    'купить илюма', 'купить ильюма', 'купить iluma', 'купить IQOS ILUMA',
    'илюма купить', 'айкос илюма', 'купить айкос илюма',
    'купить илюма в Москве', 'купить ильюма в Москве', 'илюма Москва',
    'Iluma i One', 'Iluma i Prime', 'Iluma i Standart',
    'стики для илюма', 'тереа для илюма', 'TEREA для ILUMA',
]

QUERY_VARIANTS = [
    *ILUMA_VARIANTS,
    'купить IQOS', 'iqos купить', 'купить айкос', 'айкос купить', 'айкос Москва',
    'купить LIL SOLID', 'купить лил солид', 'купить лил', 'лил солид купить',
    'купить LIL SOLID в Москве', 'купить лил солид в Москве', 'лил солид Москва',
    'стики TEREA', 'купить TEREA', 'купить тереа', 'тереа купить', 'стики тереа',
    'стики HEETS', 'купить HEETS', 'купить хитс', 'heets купить',
    'купить стики', 'стики для IQOS',
    'IQOS Москва',
]


def commercial_keywords(*extra: str) -> str:
    parts = list(QUERY_VARIANTS) + [p for p in extra if p]
    seen: set[str] = set()
    out: list[str] = []
    for p in parts:
        key = p.casefold().strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(p.strip())
    return ', '.join(out)


def product_keyword_boost() -> list[str]:
    return list(QUERY_VARIANTS)


def _buy(what: str, site: str, tail: str = '') -> str:
    base = f'Купить {what} в {site}, {CITY}.'
    return f'{base} {tail}'.strip()


def build_category_seo(site: str, role: str) -> dict:
    if role == 'hub':
        iluma_lead = (
            f'{site} рекомендует <strong>IQOS ILUMA</strong> (илюма / ильюма): без лезвия, SMARTCORE, стики TEREA. '
            f'Если сейчас на LIL — сравните комфорт ILUMA на одной витрине.'
        )
    elif role == 'premium':
        iluma_lead = f'{site} — премиум IQOS ILUMA (илюма); в каталоге также LIL SOLID, TEREA и HEETS.'
    elif role == 'lil':
        iluma_lead = f'{site} — магазин LIL SOLID; IQOS ILUMA (илюма) и TEREA доступны в том же каталоге.'
    else:
        iluma_lead = f'{site} — специалист IQOS ILUMA и TEREA; также LIL SOLID и HEETS.'

    return {
        'iqos-iluma': {
            'meta_description': _buy(
                'IQOS ILUMA, илюма, ильюма и айкос',
                site,
                'Оригинал Iluma i One, Standart и Prime без лезвия, SMARTCORE. '
                'Бронь на сайте, быстрая доставка по России.',
            ),
            'meta_keywords': commercial_keywords(
                'купить илюма', 'купить ильюма', 'Iluma i One', 'Iluma i Prime',
                site, CITY, 'original IQOS',
            ),
            'seo_text': (
                f'<p><strong>Купить илюма</strong> / <strong>купить IQOS ILUMA</strong> в {site}, {CITY}. {iluma_lead}</p>'
                f'<p>Линейка <strong>IQOS ILUMA</strong>: <strong>Iluma i One</strong> (компакт), '
                f'<strong>Iluma i Standart</strong> (баланс), <strong>Iluma i Prime</strong> (максимум автономности). '
                f'Только стики <strong>TEREA</strong> — HEETS к ILUMA не подходят.</p>'
                f'<p>Бронь на сайте, оплата при получении, доставка по {CITY.lower()} и России. '
                f'Актуальные цвета и цены — в карточках ниже.</p>'
            ),
        },
        'terea-sticks': {
            'meta_description': _buy(
                'стики TEREA (тереа) для IQOS ILUMA и илюма',
                site,
                'Оригинал Terea KZ: Purple Wave, Amber, Pearl, Blue. Блок / пачки. Бронь, доставка.',
            ),
            'meta_keywords': commercial_keywords(
                'TEREA', 'купить тереа', 'стики для илюма', 'Terea KZ', site, CITY,
            ),
            'seo_text': (
                f'<p><strong>Купить стики TEREA</strong> (тереа) в {site} — расходка для <strong>илюма / IQOS ILUMA</strong>. '
                f'Классика, ментол и Pearl. Оригинал KZ, бронь на сайте.</p>'
                f'<p>Для LIL SOLID берите HEETS отдельно — форматы несовместимы.</p>'
            ),
        },
        'lil': {
            'meta_description': _buy(
                'LIL SOLID, лил солид 3.0 / DUAL / 4.0',
                site,
                'Оригинал LIL, HEETS/Fiit. Рядом в каталоге — IQOS ILUMA (илюма) и TEREA. Бронь, доставка.',
            ),
            'meta_keywords': commercial_keywords(
                'купить LIL SOLID', 'купить лил солид', 'купить лил',
                'LIL SOLID 4.0', site, CITY,
            ),
            'seo_text': (
                f'<p><strong>Купить LIL SOLID</strong> (лил солид) в {site}: 3.0, DUAL и 4.0 — оригинал PMI, стики HEETS.</p>'
                f'<p>Хотите без чистки лезвия — смотрите <strong>IQOS ILUMA (илюма)</strong> и стики TEREA в том же магазине. '
                f'Бронь на сайте, доставка по России.</p>'
            ),
        },
        'exclusive': {
            'meta_description': _buy(
                'лимитированные IQOS ILUMA и илюма',
                site,
                'Seletti, Anniversary и редкие серии. Оригинал, бронь, доставка.',
            ),
            'meta_keywords': commercial_keywords(
                'IQOS Seletti', 'limited edition ILUMA', 'купить илюма', site, CITY,
            ),
            'seo_text': (
                f'<p>Эксклюзивные <strong>IQOS ILUMA</strong> (илюма) в {site}: Seletti и лимитки. Оригинал PMI.</p>'
            ),
        },
    }


def build_device_model_seo(site: str, role: str) -> dict:
    photo = f'фото {site}'
    hub_tip = ' Рекомендуем линейку ILUMA (илюма) покупателям, которые хотят комфорт без чистки.' if role == 'hub' else ''

    def entry(label: str, extra_kw: str, alt: str, tip: str = '', iluma: bool = False) -> dict:
        tip_bit = f' {tip}' if tip else ''
        extra_iluma = ' купить илюма, ильюма, iluma' if iluma else ''
        return {
            'meta_description': _buy(
                label + (' / илюма' if iluma else ''),
                site,
                f'{tip_bit}{hub_tip if iluma else ""} Оригинал, бронь, быстрая доставка по России.',
            ),
            'meta_keywords': commercial_keywords(label, extra_kw + extra_iluma, site, CITY),
            'image_alt': alt if photo in alt else f'{alt}, {photo}',
        }

    data = {
        'IQOS ILUMA I ONE': entry(
            'IQOS ILUMA i One',
            'Iluma i One, компактный илюма, SMARTCORE',
            f'IQOS ILUMA i One — компактный илюма, {photo}',
            'Компактный IQOS ILUMA без лезвия.',
            iluma=True,
        ),
        'IQOS ILUMA I': entry(
            'IQOS ILUMA i Standart',
            'Iluma i Standart, илюма стандарт',
            f'IQOS ILUMA i Standart — илюма, {photo}',
            'Сбалансированная модель IQOS ILUMA i.',
            iluma=True,
        ),
        'IQOS ILUMA I PRIME': entry(
            'IQOS ILUMA i Prime',
            'Iluma i Prime, флагман илюма',
            f'IQOS ILUMA i Prime — премиум илюма, {photo}',
            'Флагман IQOS ILUMA i, макс. автономность.',
            iluma=True,
        ),
        'IQOS ILUMA ONE': entry(
            'IQOS ILUMA ONE', 'IQOS ILUMA ONE, илюма', f'IQOS ILUMA ONE, {photo}',
            'Первое поколение ILUMA.', iluma=True,
        ),
        'IQOS ILUMA PRIME': entry(
            'IQOS ILUMA PRIME', 'IQOS ILUMA PRIME, илюма', f'IQOS ILUMA PRIME, {photo}',
            'Премиум первого поколения ILUMA.', iluma=True,
        ),
        'IQOS ILUMA STANDART': entry(
            'IQOS ILUMA STANDART', 'IQOS ILUMA STANDART, илюма', f'IQOS ILUMA STANDART, {photo}',
            'Классический IQOS ILUMA.', iluma=True,
        ),
        'LIL SOLID DUAL': entry(
            'LIL SOLID DUAL',
            'LIL DUAL, купить лил солид dual, HEETS',
            f'LIL SOLID DUAL, {photo}',
            'Кейс, два режима, HEETS/Fiit.',
        ),
        'LIL SOLID 3.0': entry(
            'LIL SOLID 3.0',
            'LIL 3.0, купить лил солид',
            f'LIL SOLID 3.0, {photo}',
            'Компактный LIL.',
        ),
        'LIL SOLID 4.0': entry(
            'LIL SOLID 4.0',
            'LIL 4.0, новинка LIL',
            f'LIL SOLID 4.0, {photo}',
            'Новое поколение LIL SOLID.',
        ),
    }
    data['IQOS Iluma i One'] = data['IQOS ILUMA I ONE']
    data['IQOS Iluma i Standart'] = data['IQOS ILUMA I']
    data['IQOS Iluma i Prime'] = data['IQOS ILUMA I PRIME']
    return data


def home_seo_html_for_role(
    role: str,
    brand: str,
    city: str = 'Москва',
    domain: str = '',
) -> str:
    from seo_utils import city_prepositional

    city_in = city_prepositional(city)
    defaults = {
        'hub': 'lilstore.ru',
        'premium': 'iqos-store.ru',
        'lil': 'lilsolid.ru',
        'specialist': 'iluma-iqos.ru',
    }
    dom = domain or defaults.get(role, brand.lower().replace(' ', '-'))

    if role == 'hub':
        return (
            f'<p><strong>{brand}</strong> — магазин, где выгодно <strong>купить илюма</strong> '
            f'(IQOS ILUMA / ильюма / iluma) и <strong>айкос</strong> в {city_in}. '
            f'Главный фокус витрины — устройства <strong>IQOS ILUMA</strong> без лезвия и стики <strong>TEREA</strong>. '
            f'LIL SOLID тоже в наличии, но для комфорта без чистки мы рекомендуем именно ILUMA.</p>'
            f'<h2>Купить илюма в {city_in}: One, Standart, Prime</h2>'
            f'<p>На {dom}: <strong>Iluma i One</strong>, <strong>Standart</strong> и <strong>Prime</strong> — оригинал PMI, SMARTCORE. '
            f'Запросы «купить илюма», «купить ильюма», «купить IQOS ILUMA», «айкос илюма» закрываем актуальными цветами и бронью на сайте.</p>'
            f'<h2>Стики TEREA и полный каталог</h2>'
            f'<p>К илюма — только <strong>TEREA</strong> (тереа). Также есть <strong>LIL SOLID</strong> и <strong>HEETS</strong>, '
            f'если сравниваете бюджет и формат. Один заказ — несколько линеек.</p>'
            f'<h2>Почему выбирают {brand}</h2>'
            f'<ul>'
            f'<li><strong>Приоритет IQOS ILUMA / илюма</strong> — помогаем выбрать модель</li>'
            f'<li><strong>Оригинал</strong> — заводская упаковка, без серых партий</li>'
            f'<li><strong>Доставка по {city_in}</strong> и России</li>'
            f'<li><strong>Бронь на сайте</strong> — оплата при получении</li>'
            f'</ul>'
            f'<p><strong>Купить илюма в {city_in}</strong>, подобрать TEREA и оформить заказ — в каталоге {brand}.</p>'
        )

    if role == 'premium':
        return (
            f'<p><strong>{brand}</strong> — премиальная витрина <strong>IQOS ILUMA</strong> в {city_in}. '
            f'<strong>Купить илюма / ильюма / айкос</strong>, стики TEREA и HEETS, LIL SOLID — оригинал и бронь.</p>'
            f'<h2>Каталог: ILUMA, TEREA, LIL, HEETS</h2>'
            f'<p>На {dom}: Iluma i One / Standart / Prime, лимитки, блоки TEREA, LIL SOLID и HEETS. '
            f'Акцент на статусные цвета и флагман Prime.</p>'
            f'<h2>Почему {brand}</h2>'
            f'<ul>'
            f'<li><strong>Премиум IQOS ILUMA</strong></li>'
            f'<li><strong>Полный каталог стиков и LIL</strong></li>'
            f'<li><strong>Доставка по {city_in}</strong> и России</li>'
            f'<li><strong>Бронь и оплата при получении</strong></li>'
            f'</ul>'
            f'<p><strong>Купить IQOS ILUMA в {city_in}</strong> — оформите заказ в {brand}.</p>'
        )

    if role == 'lil':
        return (
            f'<p><strong>{brand}</strong> — <strong>купить лил солид</strong> в {city_in}: 3.0, DUAL и 4.0. '
            f'В каталоге также <strong>IQOS ILUMA (илюма)</strong>, айкос, TEREA и HEETS.</p>'
            f'<h2>LIL SOLID и альтернатива ILUMA</h2>'
            f'<p>На {dom} — полный выбор LIL и рядом ILUMA для тех, кто хочет перейти на TEREA без лезвия.</p>'
            f'<h2>Почему {brand}</h2>'
            f'<ul>'
            f'<li><strong>Специализация на LIL SOLID</strong></li>'
            f'<li><strong>Илюма и стики</strong> в том же заказе</li>'
            f'<li><strong>Доставка по {city_in}</strong> и России</li>'
            f'<li><strong>Бронь на сайте</strong></li>'
            f'</ul>'
            f'<p><strong>Купить LIL SOLID в {city_in}</strong> или сравнить с илюма — в каталоге {brand}.</p>'
        )

    return (
        f'<p><strong>{brand}</strong> — специализированный магазин <strong>IQOS ILUMA</strong> и <strong>TEREA</strong> в {city_in}. '
        f'<strong>Купить илюма / ильюма / iluma / айкос</strong>; также LIL SOLID и HEETS.</p>'
        f'<h2>Специализация на илюма</h2>'
        f'<p>На {dom}: полная линейка Iluma i, блоки TEREA, консультация по вкусам и моделям.</p>'
        f'<h2>Почему {brand}</h2>'
        f'<ul>'
        f'<li><strong>Экспертиза ILUMA / TEREA</strong></li>'
        f'<li><strong>Оригинал PMI</strong></li>'
        f'<li><strong>Экспресс по {city_in}</strong>, доставка по России</li>'
        f'<li><strong>Бронь и оплата при получении</strong></li>'
        f'</ul>'
        f'<p><strong>Купить IQOS ILUMA (илюма) в {city_in}</strong> — в магазине {brand}.</p>'
    )
