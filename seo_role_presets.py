# -*- coding: utf-8 -*-
"""Ролевые SEO-пресеты: коммерческие «Купить…» по всему каталогу + уникальный угол бренда.

Роли задают акцент и формулировки, но НЕ выкидывают линейки из выдачи:
  hub        — lilstore.ru: полный коммерческий охват (эталон, который работал в топе)
  premium    — iqos-store.ru: тот же каталог, акцент премиум ILUMA
  lil        — lilsolid.ru: тот же каталог, акцент LIL SOLID
  specialist — iluma-iqos.ru: тот же каталог, акцент ILUMA/TEREA
"""
from __future__ import annotations

CITY = 'Москва'

# Транслит и разговорные запросы (Яндекс часто ищет так)
QUERY_VARIANTS = [
    'купить IQOS', 'iqos купить', 'купить айкос', 'айкос купить',
    'купить ILUMA', 'купить илюма', 'купить ильюма', 'илюма купить',
    'купить IQOS ILUMA', 'купить айкос илюма',
    'купить LIL SOLID', 'купить лил солид', 'купить лил', 'лил солид купить',
    'купить LIL SOLID в Москве', 'купить лил солид в Москве',
    'стики TEREA', 'купить TEREA', 'купить тереа', 'тереа купить', 'стики тереа',
    'стики HEETS', 'купить HEETS', 'купить хитс', 'heets купить',
    'купить стики', 'стики для IQOS', 'стики для илюма',
    'IQOS Москва', 'айкос Москва', 'илюма Москва', 'лил солид Москва',
]


def commercial_keywords(*extra: str) -> str:
    """Сжатый блок ключевых под meta_keywords (≤ ~300 символов после truncate снаружи)."""
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
    """Добавка к meta_keywords товаров — единый коммерческий хвост."""
    return list(QUERY_VARIANTS)


def _buy(what: str, site: str, tail: str = '') -> str:
    base = f'Купить {what} в {site}, {CITY}.'
    return f'{base} {tail}'.strip()


def build_category_seo(site: str, role: str) -> dict:
    """Коммерческие meta по всем категориям; seo_text с углом роли."""
    angle = {
        'hub': f'{site} — полный каталог: IQOS ILUMA, LIL SOLID, TEREA и HEETS в одном заказе.',
        'premium': f'{site} — премиальная витрина IQOS ILUMA; в каталоге также LIL SOLID, TEREA и HEETS.',
        'lil': f'{site} — магазин LIL SOLID; в каталоге также IQOS ILUMA, TEREA и HEETS.',
        'specialist': f'{site} — специалист IQOS ILUMA и TEREA; в каталоге также LIL SOLID и HEETS.',
    }.get(role, site)

    return {
        'iqos-iluma': {
            'meta_description': _buy(
                'IQOS ILUMA и IQOS Iluma i',
                site,
                'Оригинал i One, Standart и Prime без лезвия, SMARTCORE. '
                'Также илюма / ильюма / айкос. Бронь на сайте, быстрая доставка по России.',
            ),
            'meta_keywords': commercial_keywords(
                'IQOS ILUMA', 'Iluma i One', 'Iluma i Prime', 'Iluma i Standart',
                site, CITY, 'original IQOS', angle.split('—')[0].strip(),
            ),
            'seo_text': (
                f'<p><strong>Купить IQOS ILUMA</strong> (илюма, ильюма, айкос) в {site}, {CITY}. {angle}</p>'
                f'<p><strong>IQOS ILUMA</strong> — нагрев без лезвия, SMARTCORE INDUCTION™, только стики TEREA. '
                f'В каталоге: <strong>Iluma i One</strong>, <strong>Iluma i Standart</strong>, <strong>Iluma i Prime</strong>.</p>'
                f'<p>Бронь на сайте, оплата при получении, быстрая доставка по всей России. '
                f'Сравните цвета и оформите заказ за несколько минут.</p>'
            ),
        },
        'terea-sticks': {
            'meta_description': _buy(
                'стики TEREA для IQOS ILUMA',
                site,
                'Оригинал Terea KZ: Purple Wave, Amber, Pearl, Blue и другие. '
                'Блок / пачки. Бронь, доставка по России.',
            ),
            'meta_keywords': commercial_keywords(
                'TEREA', 'стики TEREA', 'купить тереа', 'Terea KZ', 'стики для IQOS ILUMA',
                site, CITY, 'original TEREA',
            ),
            'seo_text': (
                f'<p><strong>Купить стики TEREA</strong> (тереа) в {site}: расходка только для IQOS ILUMA / илюма. '
                f'HEETS к ILUMA не подходят — для LIL SOLID смотрите HEETS отдельно.</p>'
                f'<p>Классика, ментол и Pearl с капсулой — оригинал KZ. Бронь на сайте, доставка по России.</p>'
            ),
        },
        'lil': {
            'meta_description': _buy(
                'LIL SOLID, LIL SOLID DUAL и LIL SOLID 4.0',
                site,
                'Оригинал LIL, все цвета. Купить лил солид / лил в Москве. '
                'Совместимость с HEETS и Fiit. Бронь, доставка по России.',
            ),
            'meta_keywords': commercial_keywords(
                'LIL SOLID', 'LIL SOLID 4.0', 'LIL SOLID DUAL', 'LIL SOLID 3.0',
                'купить лил', 'лил солид', site, CITY, 'original LIL',
            ),
            'seo_text': (
                f'<p><strong>Купить LIL SOLID</strong> (лил солид, лил) в {site}, {CITY}. {angle}</p>'
                f'<p>Модели <strong>3.0</strong>, <strong>DUAL</strong> и <strong>4.0</strong> — оригинал PMI, стики HEETS/Fiit. '
                f'Рядом в каталоге — IQOS ILUMA и TEREA, если сравниваете форматы.</p>'
                f'<p>Бронь на сайте, оплата при получении, быстрая доставка по России.</p>'
            ),
        },
        'exclusive': {
            'meta_description': _buy(
                'лимитированные IQOS ILUMA',
                site,
                'Seletti, Anniversary и редкие серии. Оригинал, бронь, доставка по России.',
            ),
            'meta_keywords': commercial_keywords(
                'IQOS Seletti', 'Anniversary IQOS', 'limited edition ILUMA', site, CITY,
            ),
            'seo_text': (
                f'<p>Эксклюзивные и лимитированные <strong>IQOS ILUMA</strong> в {site}. '
                f'Оригинал PMI, бронь на сайте.</p>'
            ),
        },
    }


def build_device_model_seo(site: str, role: str) -> dict:
    """Коммерческие meta моделей; роль влияет на хвост описания, не убирает «Купить»."""
    focus = {
        'hub': 'полный каталог ILUMA + LIL + TEREA',
        'premium': 'премиум-витрина IQOS ILUMA',
        'lil': 'магазин LIL SOLID',
        'specialist': 'специалист IQOS ILUMA',
    }.get(role, site)
    photo = f'фото {site}'

    def entry(label: str, extra_kw: str, alt: str, tip: str = '') -> dict:
        tip_bit = f' {tip}' if tip else ''
        return {
            'meta_description': _buy(
                label,
                site,
                f'{tip_bit} Оригинал, бронь на сайте, быстрая доставка по всей России. {focus.capitalize()}.',
            ),
            'meta_keywords': commercial_keywords(label, extra_kw, site, CITY, 'original'),
            'image_alt': alt if alt.endswith(photo) or photo in alt else f'{alt}, {photo}',
        }

    data = {
        'IQOS ILUMA I ONE': entry(
            'IQOS ILUMA i One',
            'Iluma i One, компактный IQOS ILUMA, SMARTCORE, купить илюма',
            f'IQOS ILUMA i One — компактный ILUMA, {photo}',
            'Компактный IQOS ILUMA без лезвия, SMARTCORE.',
        ),
        'IQOS ILUMA I': entry(
            'IQOS ILUMA i Standart',
            'Iluma i Standart, IQOS ILUMA i, SMARTCORE',
            f'IQOS ILUMA i Standart — устройство ILUMA, {photo}',
            'Сбалансированная модель IQOS ILUMA i без лезвия.',
        ),
        'IQOS ILUMA I PRIME': entry(
            'IQOS ILUMA i Prime',
            'Iluma i Prime, премиум IQOS ILUMA, флагман ILUMA',
            f'IQOS ILUMA i Prime — премиум ILUMA, {photo}',
            'Премиум IQOS ILUMA i, максимальная автономность.',
        ),
        'IQOS ILUMA ONE': entry(
            'IQOS ILUMA ONE',
            'IQOS ILUMA ONE, первое поколение ILUMA',
            f'IQOS ILUMA ONE, {photo}',
            'Первое поколение ILUMA без лезвия.',
        ),
        'IQOS ILUMA PRIME': entry(
            'IQOS ILUMA PRIME',
            'IQOS ILUMA PRIME',
            f'IQOS ILUMA PRIME, {photo}',
            'Премиум первого поколения ILUMA.',
        ),
        'IQOS ILUMA STANDART': entry(
            'IQOS ILUMA STANDART',
            'IQOS ILUMA STANDART, SMARTCORE',
            f'IQOS ILUMA STANDART, {photo}',
            'Классический IQOS ILUMA без лезвия.',
        ),
        'LIL SOLID DUAL': entry(
            'LIL SOLID DUAL',
            'LIL DUAL, купить лил солид dual, HEETS, Fiit',
            f'LIL SOLID DUAL — LIL с кейсом, {photo}',
            'Кейс, два режима, совместимость с HEETS и Fiit.',
        ),
        'LIL SOLID 3.0': entry(
            'LIL SOLID 3.0',
            'LIL 3.0, купить лил 3.0, купить лил солид',
            f'LIL SOLID 3.0 — компактный LIL, {photo}',
            'Компактный LIL, все цвета.',
        ),
        'LIL SOLID 4.0': entry(
            'LIL SOLID 4.0',
            'LIL 4.0, новинка LIL, купить лил солид 4.0',
            f'LIL SOLID 4.0 — новое поколение LIL, {photo}',
            'Новое поколение LIL SOLID.',
        ),
    }
    # title-case aliases (iluma-iqos)
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
    """Коммерческий SEO-блок главной: полный каталог + угол роли."""
    from seo_utils import city_prepositional

    city_in = city_prepositional(city)
    defaults = {
        'hub': 'lilstore.ru',
        'premium': 'iqos-store.ru',
        'lil': 'lilsolid.ru',
        'specialist': 'iluma-iqos.ru',
    }
    dom = domain or defaults.get(role, brand.lower().replace(' ', '-'))

    catalog = (
        f'На {dom}: <strong>IQOS ILUMA</strong> (One, Standart, Prime), '
        f'<strong>LIL SOLID 3.0 / DUAL / 4.0</strong>, стики <strong>TEREA</strong> и <strong>HEETS</strong>. '
        f'Запросы вроде купить илюма, купить лил солид, купить айкос, купить тереа — закрываем одним каталогом.'
    )

    if role == 'hub':
        lead = (
            f'<p><strong>{brand}</strong> — интернет-магазин оригинальных устройств '
            f'IQOS ILUMA, LIL SOLID и стиков TEREA в {city_in}. Если ищете, где <strong>iqos купить</strong>, '
            f'<strong>купить илюма</strong>, <strong>купить лил солид</strong> или <strong>стики TEREA / HEETS</strong> '
            f'с быстрой доставкой — вы на правильном сайте. Только оригинал PMI.</p>'
        )
        why = 'Почему выбирают {brand}'
        bullets = (
            f'<li><strong>Оригинальный IQOS / айкос / илюма</strong> — заводская упаковка</li>'
            f'<li><strong>Полный каталог</strong> — ILUMA, LIL SOLID, TEREA, HEETS</li>'
            f'<li><strong>Доставка по {city_in}</strong> и России — курьер и регионы</li>'
            f'<li><strong>Бронь на сайте</strong> — оплата при получении</li>'
        )
        close = (
            f'<p><strong>IQOS купить в {city_in}</strong>, купить LIL SOLID и стики — с {brand} просто и безопасно. '
            f'Сравните модели и оформите заказ за несколько минут.</p>'
        )
        h2_cat = 'Полный каталог: IQOS, ILUMA, LIL SOLID, стики'
    elif role == 'premium':
        lead = (
            f'<p><strong>{brand}</strong> — премиальная витрина <strong>IQOS ILUMA</strong> в {city_in}. '
            f'<strong>Купить IQOS</strong>, <strong>купить илюма / ильюма / айкос</strong>, стики TEREA и HEETS, '
            f'а также LIL SOLID — оригинал, бронь на сайте.</p>'
        )
        why = f'Почему {brand}'
        bullets = (
            f'<li><strong>Премиум IQOS ILUMA</strong> — Prime, Standart, One, лимитки</li>'
            f'<li><strong>Весь каталог</strong> — TEREA, HEETS, LIL SOLID</li>'
            f'<li><strong>Доставка по {city_in}</strong> и России</li>'
            f'<li><strong>Бронь и оплата при получении</strong></li>'
        )
        close = (
            f'<p>Оформите заказ в {brand}: <strong>купить IQOS ILUMA в {city_in}</strong> '
            f'и подобрать стики тереа / heets без серых партий.</p>'
        )
        h2_cat = 'Каталог: IQOS ILUMA, LIL, TEREA, HEETS'
    elif role == 'lil':
        lead = (
            f'<p><strong>{brand}</strong> — магазин <strong>LIL SOLID</strong> в {city_in}: '
            f'<strong>купить лил солид</strong>, <strong>купить лил</strong>, LIL 3.0 / DUAL / 4.0. '
            f'В том же каталоге — IQOS ILUMA (илюма), айкос, стики TEREA и HEETS.</p>'
        )
        why = f'Почему {brand}'
        bullets = (
            f'<li><strong>Специализация на LIL SOLID</strong> — 3.0, DUAL, 4.0</li>'
            f'<li><strong>Полный каталог</strong> — ILUMA, TEREA, HEETS</li>'
            f'<li><strong>Доставка по {city_in}</strong> и России</li>'
            f'<li><strong>Бронь на сайте</strong></li>'
        )
        close = (
            f'<p><strong>Купить LIL SOLID в {city_in}</strong> и сравнить с ILUMA — в каталоге {brand}.</p>'
        )
        h2_cat = 'Каталог: LIL SOLID, IQOS ILUMA, стики'
    else:  # specialist
        lead = (
            f'<p><strong>{brand}</strong> — специализированный магазин <strong>IQOS ILUMA</strong> и стиков '
            f'<strong>TEREA</strong> в {city_in}. <strong>Купить илюма / ильюма / iluma / айкос</strong>, '
            f'стики тереа; в каталоге также LIL SOLID и HEETS.</p>'
        )
        why = f'Почему {brand}'
        bullets = (
            f'<li><strong>Экспертиза ILUMA / TEREA</strong></li>'
            f'<li><strong>Весь ассортимент</strong> — LIL SOLID, HEETS</li>'
            f'<li><strong>Экспресс по {city_in}</strong>, доставка по России</li>'
            f'<li><strong>Бронь и оплата при получении</strong></li>'
        )
        close = (
            f'<p><strong>Купить IQOS ILUMA в {city_in}</strong> у специалиста {brand} — '
            f'подберём модель и вкусы TEREA.</p>'
        )
        h2_cat = 'Каталог: ILUMA, TEREA, LIL SOLID, HEETS'

    return (
        lead
        + f'<h2>{h2_cat}</h2>'
        + f'<p>{catalog}</p>'
        + f'<h2>{why.format(brand=brand)}</h2>'
        + '<ul>'
        + bullets
        + '</ul>'
        + close
    )
