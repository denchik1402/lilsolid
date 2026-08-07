# -*- coding: utf-8 -*-
"""
Генерация SEO-полей (image_alt, meta_description, meta_keywords) для товаров и категорий.
RU + EN ключевые слова для Yandex и Google.
"""
from __future__ import annotations

import os
import re
from typing import Optional

from seo_role_presets import build_category_seo, build_device_model_seo

SITE = 'LIL SOLID'
try:
    import config as _cfg
    SITE = getattr(_cfg, 'SITE_BRAND_NAME', SITE)
except ImportError:
    pass
CITY_RU = 'Москва'
CITY_EN = 'Moscow'
DELIVERY = 'быстрая доставка по всей России'

_CITY_PREP: dict[str, str] = {
    'москва': 'Москве',
    'moscow': 'Москве',
    'санкт-петербург': 'Санкт-Петербурге',
    'санкт петербург': 'Санкт-Петербурге',
    'петербург': 'Петербурге',
    'спб': 'Санкт-Петербурге',
    'казань': 'Казани',
    'новосибирск': 'Новосибирске',
    'екатеринбург': 'Екатеринбурге',
    'нижний новгород': 'Нижнем Новгороде',
    'самара': 'Самаре',
    'ростов-на-дону': 'Ростове-на-Дону',
    'краснодар': 'Краснодаре',
    'воронеж': 'Воронеже',
}


def city_prepositional(city: str | None) -> str:
    """Предложный падеж для конструкций «в …»: Москва → Москве."""
    raw = (city or CITY_RU or 'Москва').strip()
    if not raw:
        return 'Москве'
    known = _CITY_PREP.get(raw.lower())
    if known:
        return known
    if raw.endswith('а'):
        return raw[:-1] + 'е'
    if raw.endswith('ь'):
        return raw[:-1] + 'и'
    if raw[-1] in 'бвгджзйклмнпрстфхцчшщ':
        return raw + 'е'
    return raw


def meta_city_site_phrase(city: str | None = None) -> str:
    """Грамотная вставка для meta: «в Москве — магазин»."""
    return f'в {city_prepositional(city or CITY_RU)} — {SITE}'

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

CATEGORY_SEO = build_category_seo(SITE, 'lil')

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


DEVICE_MODEL_SEO = build_device_model_seo(SITE, 'lil')


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
    if 'i prime' in name or model.upper() == 'IQOS ILUMA I PRIME':
        return 'IQOS ILUMA I PRIME'
    if 'i standart' in name or 'i standard' in name or model.upper() == 'IQOS ILUMA I':
        return 'IQOS ILUMA I'
    if 'i one' in name or model.upper() == 'IQOS ILUMA I ONE':
        return 'IQOS ILUMA I ONE'
    if 'iluma one' in name and 'i one' not in name:
        return 'IQOS ILUMA ONE'
    if 'iluma prime' in name and 'i prime' not in name:
        return 'IQOS ILUMA PRIME'
    if product.model:
        return normalize_device_model_name(product.model)
    return 'IQOS ILUMA STANDART'
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
    loc = meta_city_site_phrase()
    return {
        'meta_description': _truncate(
            f'{name} — оригинальная продукция IQOS и TEREA {loc}. '
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
            f'Купить {name} {meta_city_site_phrase()}. Оригинальная продукция, бронь на сайте, {DELIVERY}.',
            300,
        ),
        'meta_keywords': _truncate(
            _dedupe_keywords([
                name, f'купить {name}', f'buy {name}', 'IQOS', 'LIL', 'ILUMA', SITE, CITY_RU, CITY_EN,
            ]),
            300,
        ),
        'seo_text': (
            f'<p>Купить <strong>{name}</strong> {meta_city_site_phrase()}. Оригинальная продукция, '
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
        f'Оригинал TEREA {meta_city_site_phrase()}. {price} ₽, 20 стиков в блоке. '
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
        f'{meta_city_site_phrase()}. {price} ₽. Бронь на сайте, {DELIVERY}.',
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
        f'Эксклюзив {meta_city_site_phrase()}. {price} ₽. '
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
        f'Оригинал LIL {meta_city_site_phrase()}. {price} ₽. '
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
