# -*- coding: utf-8 -*-
"""
Генерация SEO-полей (image_alt, meta_description, meta_keywords) для товаров и категорий.
RU + EN ключевые слова для Yandex и Google.
"""
from __future__ import annotations

import os
import re
from typing import Optional

SITE = 'LIL SOLID'
CITY_RU = 'Москва'
CITY_EN = 'Moscow'
DELIVERY = 'доставка по Москве 0–2 дня'

CYRILLIC_BRAND_KEYWORDS = {
    'iqos': ['айкос', 'ай qos', 'купить айкос', 'икос'],
    'iluma': ['илюма', 'ильюма', 'илума', 'купить илюма', 'айкос илюма', 'iluma'],
    'terea': ['тереа', 'тerea', 'стики tereа', 'стики для илюма', 'стики айкос', 'стики'],
    'lil': ['лил', 'лил солид', 'лилсолид', 'lil solid'],
    'heets': ['хитс', 'стики heets'],
    'fit': ['фит', 'стики fit'],
}


def _cyrillic_kw(*keys: str) -> list[str]:
    out: list[str] = []
    for key in keys:
        out.extend(CYRILLIC_BRAND_KEYWORDS.get(key, []))
    return out


def make_url_slug(text: str, max_len: int = 100) -> str:
    """ЧПУ-slug из названия (категория, модель, статья)."""
    s = (text or '').lower().strip()
    s = s.replace('ё', 'е')
    s = re.sub(r'[^\w\s-]', '', s, flags=re.UNICODE)
    s = re.sub(r'[\s_]+', '-', s).strip('-')
    return (s[:max_len] if s else 'item')

COLOR_RU_EN = {
    'чёрный': 'Black', 'черный': 'Black', 'чёрный титан': 'Black Titanium',
    'зелёный': 'Green', 'зеленый': 'Green', 'зелёный кобальт': 'Green Cobalt',
    'белый': 'White', 'белый хром': 'White Chrome',
    'красный': 'Red', 'красная медь': 'Red Copper',
    'золотой': 'Gold', 'синий': 'Blue',
    'фиолетовый': 'Violet', 'голубой': 'Blue', 'терракотовый': 'Terracotta',
    'небесно-голубой': 'Breeze Blue', 'черный': 'Black',
}

TEREA_VARIANTS = {
    'purple wave': {
        'flavor_ru': 'ягодный вкус с ментолом',
        'keywords': ['Terea Purple Wave', 'TEREA Purple Wave KZ', 'стики Purple Wave', 'Purple Wave menthol', 'TEREA berry'],
    },
    'silver': {
        'flavor_ru': 'мягкий табачный вкус с ореховыми нотами',
        'keywords': ['Terea Silver', 'TEREA Silver KZ', 'стики Terea Silver', 'TEREA tobacco sticks'],
    },
    'amber': {
        'flavor_ru': 'насыщенный табачный вкус, крепкие',
        'keywords': ['Terea Amber', 'TEREA Amber KZ', 'стики Amber', 'TEREA strong sticks'],
    },
    'zing wave': {
        'flavor_ru': 'цитрус и освежающий ментол',
        'keywords': ['Terea Zing Wave', 'TEREA Zing Wave KZ', 'TEREA citrus menthol'],
    },
    'turquoise': {
        'flavor_ru': 'мята с лёгкими фруктовыми нотами',
        'keywords': ['Terea Turquoise', 'TEREA Turquoise KZ', 'TEREA mint sticks'],
    },
    'summer wave': {
        'flavor_ru': 'тропические фрукты и ментол',
        'keywords': ['Terea Summer Wave', 'TEREA Summer Wave KZ', 'TEREA tropical'],
    },
    'yellow': {
        'flavor_ru': 'табак с цитрусовыми нотами',
        'keywords': ['Terea Yellow', 'TEREA Yellow KZ', 'TEREA citrus tobacco'],
    },
    'starling pearl': {
        'flavor_ru': 'клубника, базилик и ментол, капсула',
        'keywords': ['Terea Starling Pearl', 'TEREA Starling Pearl', 'TEREA Pearl sticks', 'TEREA capsule'],
    },
    'sun pearl': {
        'flavor_ru': 'арбуз и ментол',
        'keywords': ['Terea Sun Pearl', 'TEREA Sun Pearl KZ', 'TEREA watermelon'],
    },
    'twilight pearl': {
        'flavor_ru': 'табак с фруктовыми нотами, капсула',
        'keywords': ['Terea Twilight Pearl', 'TEREA Twilight Pearl KZ', 'TEREA Pearl'],
    },
    'blue': {
        'flavor_ru': 'освежающий ментол и мята',
        'keywords': ['Terea Blue', 'TEREA Blue KZ', 'TEREA menthol sticks', 'TEREA Blue menthol'],
    },
    'tidal pearl': {
        'flavor_ru': 'табак с нотами чая, капсула ментола',
        'keywords': ['Terea Tidal Pearl', 'TEREA Tidal Pearl', 'TEREA Briza Pearl', 'TEREA tea flavor'],
    },
    'provience pearl': {
        'flavor_ru': 'виноград и ментол, капсула',
        'keywords': ['Terea Provience Pearl', 'TEREA Province Pearl', 'TEREA grape menthol'],
    },
}

CATEGORY_SEO = {
    'iqos-iluma': {
        'meta_description': (
            'Купить IQOS ILUMA и IQOS Iluma i в LIL SOLID, Москва. '
            'Оригинальные устройства i One, i Standard и i Prime без лезвия, SMARTCORE. '
            'Бронь на сайте, доставка по Москве 0–2 дня; в регионы — по срокам службы доставки.'
        ),
        'meta_keywords': (
            'IQOS ILUMA, IQOS Iluma i, Iluma i One, Iluma i Prime, Iluma i Standard, '
            'купить IQOS ILUMA, buy IQOS ILUMA, нагреватель IQOS, IQOS без лезвия, '
            'SMARTCORE, LIL SOLID, Москва, original IQOS, '
            'илюма, ильюма, айкос илюма, купить илюма, купить айкос'
        ),
        'seo_text': (
            '<p><strong>IQOS ILUMA</strong> — линейка нагревателей нового поколения без лезвия и без необходимости '
            'чистки. Технология SMARTCORE INDUCTION™ нагревает табак изнутри стика TEREA, сохраняя вкус и снижая '
            'запах по сравнению с обычным курением.</p>'
            '<p>В LIL SOLID представлены три форм-фактора: компактный <strong>Iluma i One</strong>, сбалансированный '
            '<strong>Iluma i Standart</strong> и премиальный <strong>Iluma i Prime</strong> с увеличенной автономностью. '
            'Все устройства — оригинальная продукция с гарантией производителя.</p>'
            '<p>Оформите бронь на сайте — менеджер свяжется для подтверждения. Доставка по Москве 0–2 дня; в регионы — по срокам службы доставки, уточняет менеджер, '
            'оплата при получении. Актуальные цвета и наличие — в каталоге ниже.</p>'
        ),
    },
    'terea-sticks': {
        'meta_description': (
            'Купить стики TEREA для IQOS ILUMA в LIL SOLID, Москва. '
            'Оригинальные Terea KZ: Purple Wave, Amber, Pearl, Blue и другие вкусы. '
            '20 стиков в блоке, доставка по Москве 0–2 дня, бронь на lilsolid.ru.'
        ),
        'meta_keywords': (
            'TEREA, стики TEREA, TEREA sticks, стики для IQOS ILUMA, Terea KZ, '
            'купить TEREA, buy TEREA sticks, Terea Purple Wave, Terea Amber, '
            'Terea Pearl, IQOS ILUMA sticks, LIL SOLID, Москва, original TEREA, '
            'тереа, стики тереа, стики для илюма, стики айкос, купить стики'
        ),
        'seo_text': (
            '<p><strong>TEREA</strong> — стики, разработанные специально для IQOS ILUMA. В отличие от HEETS, '
            'они содержат металлический нагреваемый элемент внутри и не требуют лезвия в устройстве. '
            'В блоке 20 стиков, срок годности и оригинальная упаковка PMI.</p>'
            '<p>В ассортименте LIL SOLID — классические табачные вкусы (Amber, Silver, Yellow), '
            'освежающие ментоловые (Blue, Turquoise, Zing Wave) и линейка Pearl с капсулами '
            '(Purple Wave, Sun Pearl, Twilight Pearl и др.). Все позиции — оригинал Terea KZ.</p>'
            '<p>Выберите вкус в каталоге и оформите бронь. Москва 0–2 дня; регионы — уточняет менеджер по России. '
            'Не уверены, какой вкус подойдёт? Напишите в Telegram @iluma_prime_bot — подскажем.</p>'
        ),
    },
    'lil': {
        'meta_description': (
            'Купить LIL SOLID, LIL SOLID DUAL и LIL SOLID 4.0 в LIL SOLID, Москва. '
            'Оригинальные устройства LIL для нагревания табака. '
            'Все модели и цвета в наличии. Москва 0–2 дня; регионы — уточняет менеджер.'
        ),
        'meta_keywords': (
            'LIL SOLID, LIL SOLID DUAL, LIL SOLID 3.0, LIL SOLID 4.0, LIL device, '
            'купить LIL SOLID, buy LIL SOLID, нагреватель LIL, LIL tobacco heating, '
            'LIL SOLID, Москва, original LIL, лил солид, лилсолид, купить лил'
        ),
        'seo_text': (
            '<p><strong>LIL SOLID</strong> — доступная линейка нагревателей табака от PMI. '
            'Устройства совместимы со стиками HEETS и аналогами, подходят тем, кто ищет '
            'компактный и надёжный формат без премиальной цены ILUMA.</p>'
            '<p>В каталоге — <strong>LIL SOLID 3.0</strong> (компактный корпус, два режима нагрева), '
            '<strong>LIL SOLID DUAL</strong> (с зарядным кейсом) и новинка <strong>LIL SOLID 4.0</strong> '
            'с обновлённым дизайном. Все цвета в наличии — чёрный, синий, зелёный, золотой и лимитированные.</p>'
            '<p>Бронь на сайте, доставка по Москве 0–2 дня, оплата при получении. Оригинальная продукция, работаем с 2020 года.</p>'
        ),
    },
    'exclusive': {
        'meta_description': (
            'Эксклюзивные и лимитированные IQOS ILUMA в LIL SOLID, Москва. '
            'Seletti Limited Edition, Anniversary Model и редкие серии. '
            'Оригинальная продукция, бронь на сайте, доставка по Москве 0–2 дня.'
        ),
        'meta_keywords': (
            'IQOS limited edition, IQOS Seletti, Iluma Seletti, эксклюзивный IQOS, '
            'лимитированный IQOS, IQOS Anniversary, rare IQOS ILUMA, '
            'купить IQOS limited, LIL SOLID, Москва, collector IQOS'
        ),
    },
}

CATEGORY_HOME = {
    'iqos-iluma': {
        'image': 'iqos-iluma.png',
        'teaser': 'Устройства IQOS ILUMA — One, Standart, Prime. Оригинал, бронь на сайте.',
        'image_alt': 'IQOS ILUMA — Iluma i One, Standart и Prime',
    },
    'terea-sticks': {
        'image': 'terea-sticks.png',
        'teaser': 'Оригинальные стики TEREA для ILUMA — все вкусы, 20 стиков в блоке.',
        'image_alt': 'Стики TEREA для IQOS ILUMA',
    },
    'lil': {
        'image': 'lil.png',
        'teaser': 'LIL SOLID 3.0, DUAL и 4.0 — оригинальные устройства в наличии.',
        'image_alt': 'Устройства LIL SOLID 3.0, Dual и 4.0',
    },
}


def category_home_image_filename(slug: str, db_image: str | None = None) -> str:
    """Имя файла обложки категории для главной (CATEGORY_HOME приоритетнее БД)."""
    home = CATEGORY_HOME.get(slug or '', {})
    if home.get('image'):
        return home['image']
    raw = (db_image or '').strip().replace('\\', '/')
    if raw.startswith('images/categories/'):
        raw = raw.split('images/categories/', 1)[-1]
    return os.path.basename(raw) if raw else ''


DEVICE_MODEL_SEO = {
    'IQOS Iluma i One': {
        'meta_description': (
            'Купить IQOS Iluma i One в LIL SOLID, Москва. Компактное устройство IQOS ILUMA '
            'без лезвия, технология SMARTCORE. Оригинал, все цвета. Бронь на сайте, доставка по Москве 0–2 дня.'
        ),
        'meta_keywords': (
            'IQOS Iluma i One, купить Iluma i One, buy IQOS i One, IQOS ILUMA compact, '
            'SMARTCORE, IQOS без лезвия, original IQOS, оригинал IQOS, LIL SOLID, Москва'
        ),
        'image_alt': 'IQOS Iluma i One — компактное устройство IQOS ILUMA, фото LIL SOLID',
    },
    'IQOS Iluma i Standart': {
        'meta_description': (
            'Купить IQOS Iluma i Standart в LIL SOLID, Москва. Сбалансированная модель IQOS ILUMA '
            'без лезвия, SMARTCORE, увеличенная батарея. Оригинал, бронь на сайте, доставка по Москве 0–2 дня.'
        ),
        'meta_keywords': (
            'IQOS Iluma i Standart, IQOS Iluma i Standard, купить Iluma i Standart, '
            'buy IQOS i Standard, IQOS ILUMA, SMARTCORE, original IQOS, LIL SOLID, Москва'
        ),
        'image_alt': 'IQOS Iluma i Standart — устройство IQOS ILUMA, фото LIL SOLID',
    },
    'IQOS Iluma i Prime': {
        'meta_description': (
            'Купить IQOS Iluma i Prime в LIL SOLID, Москва. Премиальное устройство IQOS ILUMA '
            'без лезвия, SMARTCORE, максимальная автономность. Оригинал, доставка по Москве 0–2 дня.'
        ),
        'meta_keywords': (
            'IQOS Iluma i Prime, купить Iluma i Prime, buy IQOS i Prime, IQOS ILUMA premium, '
            'SMARTCORE, original IQOS, оригинал IQOS, LIL SOLID, Москва'
        ),
        'image_alt': 'IQOS Iluma i Prime — премиальное устройство IQOS ILUMA, фото LIL SOLID',
    },
    'LIL SOLID DUAL': {
        'meta_description': (
            'Купить LIL SOLID DUAL в LIL SOLID, Москва. Устройство LIL с зарядным кейсом, '
            'два режима нагрева, совместимость с HEETS и FIT. Оригинал, доставка по Москве 0–2 дня.'
        ),
        'meta_keywords': (
            'LIL SOLID DUAL, купить LIL SOLID DUAL, buy LIL SOLID DUAL, LIL dual mode, '
            'нагреватель LIL, LIL device, original LIL, LIL SOLID, Москва'
        ),
        'image_alt': 'LIL SOLID DUAL — устройство LIL с кейсом, фото LIL SOLID',
    },
    'LIL SOLID 3.0': {
        'meta_description': (
            'Купить LIL SOLID 3.0 в LIL SOLID, Москва. Компактное устройство LIL с двумя режимами '
            'интенсивности и съёмным нагревателем. Оригинал, бронь на сайте, доставка по Москве 0–2 дня.'
        ),
        'meta_keywords': (
            'LIL SOLID 3.0, купить LIL SOLID 3.0, buy LIL SOLID 3.0, LIL 3.0, '
            'нагреватель LIL, LIL device, original LIL, LIL SOLID, Москва'
        ),
        'image_alt': 'LIL SOLID 3.0 — компактное устройство LIL, фото LIL SOLID',
    },
    'LIL SOLID 4.0': {
        'meta_description': (
            'Купить LIL SOLID 4.0 в LIL SOLID, Москва. Новое поколение LIL SOLID — '
            'улучшенный нагреватель, стильный дизайн. Оригинальная продукция LIL, доставка по Москве 0–2 дня.'
        ),
        'meta_keywords': (
            'LIL SOLID 4.0, купить LIL SOLID 4.0, buy LIL SOLID 4.0, LIL SOLID new, '
            'LIL device, нагреватель LIL, LIL tobacco heating, original LIL, LIL SOLID, Москва'
        ),
        'image_alt': 'LIL SOLID 4.0 — устройство LIL нового поколения, фото LIL SOLID',
    },
}


def normalize_device_model_name(name: str) -> str:
    """LIL в названии модели — только заглавными."""
    name = ' '.join((name or '').split())
    return re.sub(r'\blil\s+solid\b', 'LIL SOLID', name, flags=re.IGNORECASE)


def device_model_slug(name: str) -> str:
    return make_url_slug(normalize_device_model_name(name) if name else '')


def _truncate(text: str, max_len: int) -> str:
    text = ' '.join(text.split())
    if len(text) <= max_len:
        return text
    cut = text[:max_len]
    if ' ' in cut[max_len // 2:]:
        cut = cut.rsplit(' ', 1)[0]
    elif ' ' in cut:
        cut = cut.rsplit(' ', 1)[0]
    return cut.rstrip('.,;:- ') + '…'


def _format_price(price: float) -> str:
    return f'{int(round(float(price))):,}'.replace(',', ' ')


def _dedupe_keywords(parts: list[str]) -> str:
    seen = set()
    result = []
    for p in parts:
        key = p.strip().lower()
        if key and key not in seen:
            seen.add(key)
            result.append(p.strip())
    return ', '.join(result)


def _specs_dict(product) -> dict[str, str]:
    return dict(product.get_characteristics())


def _is_terea(product, category) -> bool:
    if category and category.slug == 'terea-sticks':
        return True
    return 'terea' in (product.name or '').lower()


def _is_lil(product, category) -> bool:
    if category and category.slug == 'lil':
        return True
    return 'lil solid' in (product.name or '').lower() or (product.model or '').startswith('LIL')


def _is_exclusive(product, category) -> bool:
    if category and category.slug == 'exclusive':
        return True
    name = (product.name or '').lower()
    return bool(product.is_exclusive) or any(x in name for x in ('limited', 'seletti', 'anniversary', 'exclusive'))


def _device_line(product) -> Optional[str]:
    name = (product.name or '').lower()
    model = (product.model or '')
    if 'lil solid dual' in name or model == 'LIL SOLID DUAL':
        return 'LIL SOLID DUAL'
    if 'lil solid 4' in name or model == 'LIL SOLID 4.0':
        return 'LIL SOLID 4.0'
    if 'lil solid 3' in name or model == 'LIL SOLID 3.0':
        return 'LIL SOLID 3.0'
    if 'i prime' in name or 'i prime' in model.lower():
        return 'IQOS Iluma i Prime'
    if 'i standart' in name or 'i standard' in name:
        return 'IQOS Iluma i Standard'
    if 'i one' in name:
        return 'IQOS Iluma i One'
    if product.model:
        return normalize_device_model_name(product.model)
    return 'IQOS ILUMA'


def _terea_variant(name: str) -> Optional[dict]:
    lower = name.lower()
    for key, data in TEREA_VARIANTS.items():
        if key in lower:
            return data
    return None


def _extract_color_en(product) -> Optional[str]:
    name_lower = (product.name or '').lower()
    for ru, en in sorted(COLOR_RU_EN.items(), key=lambda x: -len(x[0])):
        if ru in name_lower:
            return en

    desc = product.description or ''
    match = re.search(r'<b>Цвет:</b>\s*([^\n<•]+)', desc, re.IGNORECASE)
    if match:
        raw = match.group(1).strip().rstrip('.')
        before_paren = raw.split('(')[0].strip()
        if before_paren:
            return before_paren
        paren = re.search(r'\(([^)]+)\)', raw)
        if paren:
            return paren.group(1).strip()

    if product.color:
        return product.color
    color_words = (
        'Breeze Blue', 'Midnight Black', 'Digital Violet', 'Leaf Green',
        'Vivid Terracotta', 'Garnet Red', 'Aspen Green',
    )
    name = product.name or ''
    for cw in color_words:
        if cw.lower() in name.lower():
            return cw
    return None


def _stick_flavor_text(product) -> str:
    variant = _terea_variant(product.name or '')
    if variant:
        return variant['flavor_ru']
    specs = _specs_dict(product)
    taste = specs.get('Вкус', '')
    strength = specs.get('Крепость', '')
    parts = []
    if taste:
        parts.append(taste)
    if strength:
        parts.append(f'крепость: {strength.lower()}')
    return ', '.join(parts) if parts else 'оригинальный вкус TEREA'


def generate_category_seo(category) -> dict[str, str]:
    slug = category.slug or ''
    preset = CATEGORY_SEO.get(slug)
    if preset:
        return {
            'meta_description': _truncate(preset['meta_description'], 300),
            'meta_keywords': _truncate(preset['meta_keywords'], 300),
            'seo_text': preset.get('seo_text', ''),
        }
    name = category.name or 'Каталог'
    return {
        'meta_description': _truncate(
            f'{name} — оригинальная продукция IQOS и TEREA в {SITE}, {CITY_RU}. '
            f'Бронь на сайте, {DELIVERY}.',
            300,
        ),
        'meta_keywords': _truncate(
            _dedupe_keywords([
                name, f'купить {name}', 'IQOS', 'TEREA', 'ILUMA', SITE, CITY_RU, CITY_EN,
            ]),
            300,
        ),
        'seo_text': '',
    }


def generate_device_model_seo(device_model) -> dict[str, str]:
    name = normalize_device_model_name(getattr(device_model, 'name', None) or str(device_model))
    preset = DEVICE_MODEL_SEO.get(name)
    if preset:
        return {
            'image_alt': _truncate(preset['image_alt'], 200),
            'meta_description': _truncate(preset['meta_description'], 300),
            'meta_keywords': _truncate(preset['meta_keywords'], 300),
            'seo_text': preset.get('seo_text', ''),
        }
    return {
        'image_alt': _truncate(f'{name} — устройство, фото {SITE}', 200),
        'meta_description': _truncate(
            f'Купить {name} в {SITE}, {CITY_RU}. Оригинальная продукция, бронь на сайте, {DELIVERY}.',
            300,
        ),
        'meta_keywords': _truncate(
            _dedupe_keywords([
                name, f'купить {name}', f'buy {name}', 'IQOS', 'LIL', 'ILUMA', SITE, CITY_RU, CITY_EN,
            ]),
            300,
        ),
        'seo_text': (
            f'<p>Купить <strong>{name}</strong> в {SITE}, {CITY_RU}. Оригинальная продукция, '
            f'бронь на сайте, {DELIVERY}. Актуальные цвета и наличие — в каталоге ниже.</p>'
        ),
    }


def generate_product_seo(product) -> dict[str, str]:
    category = product.category
    name = (product.name or '').strip()
    price = _format_price(product.price)
    specs = _specs_dict(product)

    if _is_terea(product, category):
        return _generate_terea_seo(product, name, price, specs)
    if _is_lil(product, category):
        return _generate_lil_seo(product, name, price)
    if _is_exclusive(product, category):
        return _generate_exclusive_seo(product, name, price)
    return _generate_iqos_seo(product, name, price)


def _generate_terea_seo(product, name: str, price: str, specs: dict) -> dict[str, str]:
    flavor = _stick_flavor_text(product)
    variant = _terea_variant(name)
    has_capsule = 'капсула' in (product.description or '').lower() or 'Pearl' in name

    meta_description = _truncate(
        f'Стики {name} для IQOS ILUMA — {flavor}. '
        f'Оригинал TEREA в {SITE}, {CITY_RU}. {price} ₽, 20 стиков в блоке. '
        f'Бронь на сайте, {DELIVERY}.',
        300,
    )

    kw = [
        name, f'купить {name}', f'buy {name}',
        'TEREA', 'стики TEREA', 'TEREA sticks', 'Terea KZ', 'TEREA KZ',
        'стики для IQOS ILUMA', 'IQOS ILUMA sticks', 'TEREA for ILUMA',
        'оригинал TEREA', 'original TEREA', SITE, CITY_RU, CITY_EN,
    ]
    if variant:
        kw.extend(variant['keywords'])
    if has_capsule:
        kw.extend(['TEREA Pearl', 'TEREA capsule', 'стики Terea с капсулой'])
    taste = specs.get('Вкус')
    if taste:
        kw.append(f'TEREA {taste}')
    kw.extend(_cyrillic_kw('terea', 'iqos', 'iluma'))

    meta_keywords = _truncate(_dedupe_keywords(kw), 300)

    image_alt = _truncate(
        f'Стики {name} — упаковка TEREA для IQOS ILUMA, {flavor}, фото {SITE}',
        200,
    )
    return {
        'image_alt': image_alt,
        'meta_description': meta_description,
        'meta_keywords': meta_keywords,
    }


def _generate_iqos_seo(product, name: str, price: str) -> dict[str, str]:
    line = _device_line(product)
    color_en = _extract_color_en(product)
    color_part = f', цвет {color_en}' if color_en else ''

    meta_description = _truncate(
        f'{name} — оригинальное устройство {line} без лезвия, SMARTCORE{color_part}. '
        f'{SITE}, {CITY_RU}. {price} ₽. Бронь на сайте, {DELIVERY}.',
        300,
    )

    kw = [
        name, f'купить {name}', f'buy {name}',
        line, 'IQOS ILUMA', 'IQOS Iluma i', 'ILUMA',
        'купить IQOS', 'buy IQOS ILUMA', 'нагреватель IQOS', 'IQOS без лезвия',
        'SMARTCORE', 'original IQOS', 'оригинал IQOS', SITE, CITY_RU, CITY_EN,
    ]
    if color_en:
        kw.extend([color_en, f'IQOS {color_en}', f'Iluma {color_en}'])
    if 'i one' in name.lower():
        kw.extend(['Iluma i One', 'IQOS i One compact'])
    elif 'standart' in name.lower() or 'standard' in name.lower():
        kw.extend(['Iluma i Standard', 'IQOS i Standard'])
    elif 'prime' in name.lower():
        kw.extend(['Iluma i Prime', 'IQOS i Prime premium'])
    kw.extend(_cyrillic_kw('iqos', 'iluma'))

    meta_keywords = _truncate(_dedupe_keywords(kw), 300)
    image_alt = _truncate(
        f'Устройство {name}{color_part} — фото IQOS ILUMA, оригинал, {SITE}',
        200,
    )
    return {
        'image_alt': image_alt,
        'meta_description': meta_description,
        'meta_keywords': meta_keywords,
    }


def _generate_exclusive_seo(product, name: str, price: str) -> dict[str, str]:
    line = _device_line(product)
    limited_hint = 'лимитированная серия' if 'limited' in name.lower() or 'seletti' in name.lower() else 'эксклюзивная модель'

    meta_description = _truncate(
        f'{name} — {limited_hint}, оригинальный {line}. '
        f'Эксклюзив в {SITE}, {CITY_RU}. {price} ₽. '
        f'Бронь на сайте, {DELIVERY}.',
        300,
    )

    kw = [
        name, f'купить {name}',
        'IQOS limited edition', 'IQOS Seletti', 'Iluma Seletti',
        'лимитированный IQOS', 'эксклюзивный IQOS', 'IQOS collector',
        line, 'IQOS ILUMA', 'original IQOS', SITE, CITY_RU, CITY_EN,
    ]
    if 'seletti' in name.lower():
        kw.extend(['Seletti IQOS', 'IQOS x Seletti', 'Iluma Seletti limited'])
    if 'anniversary' in name.lower():
        kw.extend(['IQOS Anniversary', 'Iluma Anniversary Model'])
    kw.extend(_cyrillic_kw('iqos', 'iluma'))

    meta_keywords = _truncate(_dedupe_keywords(kw), 300)
    image_alt = _truncate(
        f'{name} — эксклюзивное устройство IQOS ILUMA, фото {SITE}',
        200,
    )
    return {
        'image_alt': image_alt,
        'meta_description': meta_description,
        'meta_keywords': meta_keywords,
    }


def _generate_lil_seo(product, name: str, price: str) -> dict[str, str]:
    line = _device_line(product)
    color_en = _extract_color_en(product)
    dual = 'DUAL' in name.upper()
    mode = 'два режима нагрева' if dual else 'компактное устройство нагревания табака'

    meta_description = _truncate(
        f'{name} — {line}, {mode}. '
        f'Оригинал LIL в {SITE}, {CITY_RU}. {price} ₽. '
        f'Бронь на сайте, {DELIVERY}.',
        300,
    )

    kw = [
        name, f'купить {name}', f'buy {name}',
        line, 'LIL SOLID', 'LIL device', 'купить LIL SOLID', 'buy LIL SOLID',
        'нагреватель LIL', 'LIL tobacco heating', 'original LIL', 'оригинал LIL',
        SITE, CITY_RU, CITY_EN,
    ]
    if dual:
        kw.extend(['LIL SOLID DUAL', 'LIL dual mode'])
    elif '4.0' in line:
        kw.extend(['LIL SOLID 4.0', 'LIL 4.0'])
    else:
        kw.extend(['LIL SOLID 3.0', 'LIL 3.0'])
    if color_en:
        kw.append(f'LIL SOLID {color_en}')
    kw.extend(_cyrillic_kw('lil', 'iqos'))

    meta_keywords = _truncate(_dedupe_keywords(kw), 300)
    color_part = f', цвет {color_en}' if color_en else ''
    image_alt = _truncate(
        f'Устройство {name}{color_part} — фото LIL, оригинал, {SITE}',
        200,
    )
    return {
        'image_alt': image_alt,
        'meta_description': meta_description,
        'meta_keywords': meta_keywords,
    }
