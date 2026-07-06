# -*- coding: utf-8 -*-
"""SEO, каталог, PDP — общие хелперы для усиления витрин."""
from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from flask import Flask
    from models import Product


def discount_percent(product) -> int | None:
    if not product or not product.old_price or product.old_price <= product.price:
        return None
    return int(round((1 - product.price / product.old_price) * 100))


def get_model_catalog_tiles(app, db, Product, DeviceModel, Category, url_for, cache_bust=None):
    """Плитки моделей и стиков для главной."""
    from image_utils import resolve_product_image, product_image_exists

    tiles = []
    for dm in DeviceModel.query.order_by(DeviceModel.sort_order, DeviceModel.name).all():
        count = Product.query.filter(
            db.func.lower(Product.model) == dm.name.lower()
        ).count()
        if count == 0:
            continue
        img = None
        sample = Product.query.filter(
            db.func.lower(Product.model) == dm.name.lower()
        ).order_by(Product.views.desc()).first()
        if sample:
            img = resolve_product_image(sample.name, sample.image, app.static_folder)
            if img and not product_image_exists(app.static_folder, img):
                img = None
        url = url_for('catalog', category_slug=dm.slug) if dm.slug else url_for('catalog', model=dm.name)
        tiles.append({
            'name': dm.name,
            'count': count,
            'url': url,
            'image': img,
        })

    stick_groups = [
        ('terea-sticks', 'Стики TEREA'),
        ('terea-kz', 'TEREA Казахстан'),
        ('heets-sticks', 'Стики HEETS'),
        ('heets-kz', 'HEETS Казахстан'),
    ]
    for slug, label in stick_groups:
        cat = Category.query.filter_by(slug=slug).first()
        if not cat:
            continue
        t_count = Product.query.filter_by(category_id=cat.id).count()
        if not t_count:
            continue
        sample = Product.query.filter_by(category_id=cat.id).order_by(Product.views.desc()).first()
        t_img = None
        if sample:
            t_img = resolve_product_image(sample.name, sample.image, app.static_folder)
        tiles.append({
            'name': label,
            'count': t_count,
            'url': url_for('catalog', category_slug=slug),
            'image': t_img,
        })
    return tiles


def get_product_siblings(product, Product, db, limit=50):
    """Prev/next в той же модели или категории."""
    if not product:
        return None, None
    q = Product.query.filter(Product.id != product.id, Product.in_stock == True)
    if product.model:
        q = q.filter(db.func.lower(Product.model) == product.model.lower())
    elif product.category_id:
        q = q.filter_by(category_id=product.category_id)
    else:
        return None, None
    siblings = q.order_by(Product.name, Product.id).all()
    ids = [p.id for p in siblings]
    if product.id not in ids:
        ordered = sorted(siblings + [product], key=lambda p: (p.name or '', p.id))
    else:
        ordered = siblings
        if product not in ordered:
            ordered = sorted(siblings + [product], key=lambda p: (p.name or '', p.id))
    try:
        idx = next(i for i, p in enumerate(ordered) if p.id == product.id)
    except StopIteration:
        ordered = sorted(siblings + [product], key=lambda p: (p.name or '', p.id))
        idx = next(i for i, p in enumerate(ordered) if p.id == product.id)
    prev_p = ordered[idx - 1] if idx > 0 else None
    next_p = ordered[idx + 1] if idx < len(ordered) - 1 else None
    return prev_p, next_p


def get_stick_upsell_products(product, Product, db, limit=4):
    """Апселл стиков на карточке устройства."""
    if not product:
        return []
    name_l = (product.name or '').lower()
    model_l = (product.model or '').lower()
    is_device = 'terea' not in name_l and 'heets' not in name_l
    if not is_device:
        return []
    q = Product.query.filter(Product.in_stock == True)
    if 'iluma' in model_l or 'iluma' in name_l:
        q = q.filter(db.func.lower(Product.name).like('%terea%'))
    elif 'lil' in model_l or 'solid' in model_l:
        q = q.filter(db.func.lower(Product.name).like('%heets%'))
    else:
        q = q.filter(
            db.or_(
                db.func.lower(Product.name).like('%terea%'),
                db.func.lower(Product.name).like('%heets%'),
            )
        )
    items = q.order_by(Product.views.desc()).limit(limit * 2).all()
    seen = set()
    out = []
    for p in items:
        key = (p.model or p.name or '')[:40]
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
        if len(out) >= limit:
            break
    return out


def product_card_image_url(product, url_for, static_folder):
    from image_utils import resolve_product_image
    raw = product.all_images[0] if getattr(product, 'all_images', None) else product.image
    if not raw:
        return url_for('static', filename='LOGO3.png')
    path = resolve_product_image(product.name, raw, static_folder) or raw
    if path.startswith('http'):
        return path
    return url_for('static', filename=f'images/products/{path}' if not path.startswith('images/') else path)


def home_faq_items(brand: str, city: str = 'Москва') -> list[dict[str, str]]:
    return [
        {
            'q': f'Как выбрать устройство IQOS в {brand}?',
            'a': (
                'Для линейки ILUMA подходят только стики TEREA — без лезвия и чистки. '
                'Iluma i One — компактный моноблок, Standart — с кейсом, Prime — премиум и автономность. '
                'LIL SOLID совместим со стиками HEETS. Поможем подобрать в каталоге или в Telegram.'
            ),
        },
        {
            'q': 'Можно ли купить с доставкой по всей России?',
            'a': (
                f'Да. {city} и МО — курьер в день заказа или на следующий день. '
                'В регионы отправляем СДЭК и другими ТК от 1–2 дней. Оплата при получении.'
            ),
        },
        {
            'q': 'TEREA, HEETS и Fiit — в чём разница?',
            'a': (
                'TEREA — только для IQOS ILUMA (индукционный нагрев). '
                'HEETS и Fiit — для LIL SOLID и классических IQOS с лезвием. '
                'Несовместимые стики не вставляются в устройство — это защита от ошибки.'
            ),
        },
        {
            'q': 'Гарантия и оригинальность',
            'a': (
                f'В {brand} только сертифицированная продукция в заводской упаковке. '
                'На устройства — гарантия производителя. При получении можно проверить пломбы и комплектацию.'
            ),
        },
        {
            'q': 'Как оформить заказ в один клик?',
            'a': (
                'На карточке товара нажмите «Покупка в 1 клик», укажите имя и телефон — '
                'менеджер перезвонит для подтверждения. Также доступны корзина, Telegram, WhatsApp и MAX.'
            ),
        },
        {
            'q': 'Сколько стоит доставка?',
            'a': (
                'Москва и МО — от 1 000 ₽ (экспресс в день заказа). По России — от 800 ₽, '
                'точная сумма зависит от города и способа доставки. Указана на карточке товара.'
            ),
        },
    ]


def home_seo_html(brand: str, city: str = 'Москва', domain: str = '') -> str:
    dom = domain or brand.lower().replace(' ', '-')
    return (
        f'<p><strong>{brand}</strong> — специализированный интернет-магазин оригинальных устройств '
        f'IQOS ILUMA, LIL SOLID и стиков TEREA в {city}. Если вы ищете, где <strong>iqos купить</strong> '
        f'с быстрой доставкой — вы на правильном сайте. Только подлинная продукция с гарантией производителя.</p>'
        f'<h2>Полный каталог IQOS: устройства и стики</h2>'
        f'<p>На {dom} представлены флагманские <strong>IQOS ILUMA</strong> с технологией SMARTCORE INDUCTION™, '
        f'компактные <strong>Iluma i One</strong>, <strong>LIL SOLID 3.0, DUAL и 4.0</strong>, '
        f'а также стики <strong>TEREA</strong> (KZ, EU) и <strong>HEETS</strong> для совместимых устройств.</p>'
        f'<h2>Почему выбирают {brand}</h2>'
        f'<ul>'
        f'<li><strong>Оригинальный IQOS</strong> — заводская упаковка, без подделок</li>'
        f'<li><strong>Доставка айкос {city.lower()}</strong> — курьер в день заказа, по РФ от 1–2 дней</li>'
        f'<li><strong>Бронь на сайте</strong> — оплата при получении</li>'
        f'<li><strong>Консультация</strong> — Telegram, WhatsApp, телефон</li>'
        f'</ul>'
        f'<p>Изучите каталог, сравните модели и оформите заказ за несколько минут. '
        f'<strong>Iqos купить москва</strong> и регионы — с {brand} просто и безопасно.</p>'
    )
