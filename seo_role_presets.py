# -*- coding: utf-8 -*-
"""Ролевые SEO-пресеты категорий и моделей устройств.

Роли:
  hub      — lilstore.ru (LIL STORE): хаб ILUMA + LIL + TEREA
  premium  — iqos-store.ru (АЙКОС СТОР): премиум ILUMA
  lil      — lilsolid.ru (LIL SOLID): фокус LIL
  specialist — iluma-iqos.ru (ILUMA IQOS): специалист ILUMA/TEREA
"""
from __future__ import annotations


def build_category_seo(site: str, role: str) -> dict:
    city = 'Москва'
    if role == 'hub':
        return {
            'iqos-iluma': {
                'meta_description': (
                    f'Каталог IQOS ILUMA в {site}: Iluma i One, Standart и Prime — оригинал в одном хабе '
                    f'с LIL SOLID и TEREA. {city}, бронь на сайте, быстрая доставка по России.'
                ),
                'meta_keywords': (
                    f'IQOS ILUMA каталог, Iluma i One, Iluma i Prime, хаб IQOS, {site}, {city}, original IQOS'
                ),
                'seo_text': (
                    f'<p><strong>{site}</strong> — хаб оригинальных <strong>IQOS ILUMA</strong> рядом с LIL SOLID и стиками TEREA. '
                    f'Технология SMARTCORE INDUCTION™: без лезвия и без чистки.</p>'
                    f'<p>В каталоге — <strong>Iluma i One</strong>, <strong>Iluma i Standart</strong> и <strong>Iluma i Prime</strong>. '
                    f'Сравните модели на одной витрине и оформите бронь — менеджер подтвердит цвет и наличие.</p>'
                    f'<p>Быстрая доставка по всей России, оплата при получении. Актуальные цены — в карточках ниже.</p>'
                ),
            },
            'terea-sticks': {
                'meta_description': (
                    f'Стики TEREA для IQOS ILUMA в {site}: блок 10 пачек (20 стиков в пачке). '
                    f'Вкусы KZ — Purple Wave, Amber, Pearl и другие. {city}, бронь на сайте.'
                ),
                'meta_keywords': (
                    f'TEREA блок, стики TEREA KZ, TEREA для ILUMA, купить TEREA {site}, {city}, original TEREA'
                ),
                'seo_text': (
                    f'<p><strong>TEREA</strong> — стики только для IQOS ILUMA. В {site} продаём <strong>блоками по 10 пачек</strong> '
                    f'(в пачке 20 стиков): удобно для регулярного использования.</p>'
                    f'<p>Классика (Amber, Silver), ментол (Blue, Turquoise) и Pearl с капсулами — оригинал Terea KZ. '
                    f'Подберём вкус в Telegram или при подтверждении брони.</p>'
                ),
            },
            'lil': {
                'meta_description': (
                    f'LIL SOLID 3.0, DUAL и 4.0 в хабе {site}. Оригинальные устройства рядом с IQOS ILUMA и HEETS. '
                    f'{city}, бронь, быстрая доставка по России.'
                ),
                'meta_keywords': (
                    f'LIL SOLID хаб, LIL SOLID 4.0, LIL SOLID DUAL, купить LIL {site}, {city}, original LIL'
                ),
                'seo_text': (
                    f'<p>В {site} линейка <strong>LIL SOLID</strong> стоит рядом с ILUMA: удобно сравнить форматы и бюджет. '
                    f'<strong>3.0</strong>, <strong>DUAL</strong> с кейсом и новинка <strong>4.0</strong> — оригинал PMI.</p>'
                    f'<p>Совместимы с HEETS/Fiit. Бронь на сайте, оплата при получении.</p>'
                ),
            },
            'exclusive': {
                'meta_description': (
                    f'Лимитированные IQOS ILUMA в {site}: Seletti, Anniversary и редкие серии. '
                    f'Оригинал, бронь, доставка по России.'
                ),
                'meta_keywords': (
                    f'IQOS limited {site}, Seletti ILUMA, Anniversary IQOS, эксклюзив IQOS, {city}'
                ),
            },
        }

    if role == 'premium':
        return {
            'iqos-iluma': {
                'meta_description': (
                    f'Премиальные IQOS ILUMA в {site}: Iluma i Prime, Standart и One — оригинал, '
                    f'акцент на статусные цвета и лимитированные серии. {city}.'
                ),
                'meta_keywords': (
                    f'премиум IQOS ILUMA, Iluma i Prime купить, АЙКОС СТОР, luxury IQOS, {city}, original IQOS'
                ),
                'seo_text': (
                    f'<p><strong>{site}</strong> — премиальная витрина <strong>IQOS ILUMA</strong>. '
                    f'Фокус на качество сборки, редкие цвета и модели с максимальной автономностью.</p>'
                    f'<p>Линейка Iluma i: компактный <strong>One</strong>, сбалансированный <strong>Standart</strong> '
                    f'и флагман <strong>Prime</strong>. Только оригинал с гарантией производителя.</p>'
                    f'<p>Бронь на сайте, консультация по комплектации, быстрая доставка по России.</p>'
                ),
            },
            'terea-sticks': {
                'meta_description': (
                    f'Оригинальные стики TEREA к премиальным ILUMA в {site}. Блок 10 пачек. '
                    f'Подбор вкуса под ваше устройство. {city}.'
                ),
                'meta_keywords': (
                    f'TEREA премиум, стики к ILUMA Prime, TEREA блок {site}, {city}, original TEREA'
                ),
                'seo_text': (
                    f'<p>Стики <strong>TEREA</strong> — единственный формат для IQOS ILUMA. В {site} блоки по 10 пачек, '
                    f'оригинал KZ с актуальным сроком годности.</p>'
                    f'<p>Поможем подобрать вкус под ежедневное использование или редкую серию устройства.</p>'
                ),
            },
            'lil': {
                'meta_description': (
                    f'LIL SOLID в ассортименте {site} — компактная альтернатива ILUMA. '
                    f'Оригинал, бронь, доставка. Основной фокус витрины — премиум IQOS ILUMA.'
                ),
                'meta_keywords': (
                    f'LIL SOLID {site}, альтернатива ILUMA, LIL 4.0 оригинал, {city}'
                ),
                'seo_text': (
                    f'<p>На {site} устройства <strong>LIL SOLID</strong> — дополнительная линейка к премиум ILUMA: '
                    f'если нужен более компактный и доступный формат с HEETS.</p>'
                ),
            },
            'exclusive': {
                'meta_description': (
                    f'Коллекционные IQOS ILUMA в {site}: Seletti Limited, Anniversary и редкие издания. '
                    f'Премиум-витрина, оригинал, бронь.'
                ),
                'meta_keywords': (
                    f'IQOS Seletti {site}, limited edition ILUMA, коллекционный IQOS, {city}'
                ),
            },
        }

    if role == 'lil':
        return {
            'iqos-iluma': {
                'meta_description': (
                    f'IQOS ILUMA в {site} — дополнительная линейка к основному каталогу LIL SOLID. '
                    f'Оригинал, бронь. Главный фокус магазина — устройства LIL.'
                ),
                'meta_keywords': (
                    f'IQOS ILUMA {site}, ILUMA к LIL SOLID, original IQOS, {city}'
                ),
                'seo_text': (
                    f'<p>В {site} основной акцент — <strong>LIL SOLID</strong>. Линейка <strong>IQOS ILUMA</strong> '
                    f'доступна как дополнительный выбор для тех, кто переходит на TEREA и SMARTCORE.</p>'
                ),
            },
            'terea-sticks': {
                'meta_description': (
                    f'TEREA для IQOS ILUMA в {site}. Если пользуетесь LIL — смотрите HEETS/Fiit в каталоге. '
                    f'Блок 10 пачек, оригинал.'
                ),
                'meta_keywords': (
                    f'TEREA {site}, стики ILUMA, блок TEREA, {city}'
                ),
                'seo_text': (
                    f'<p>Стики <strong>TEREA</strong> подходят только к IQOS ILUMA. Для LIL SOLID берите HEETS или Fiit — '
                    f'их совместимость отличается. В {site} подскажем при брони.</p>'
                ),
            },
            'lil': {
                'meta_description': (
                    f'Купить LIL SOLID 3.0, DUAL и 4.0 в {site} — магазин устройств LIL. '
                    f'Все цвета, оригинал, бронь, быстрая доставка по России. {city}.'
                ),
                'meta_keywords': (
                    f'купить LIL SOLID, LIL SOLID 4.0, LIL SOLID DUAL, LIL SOLID 3.0, {site}, {city}, original LIL'
                ),
                'seo_text': (
                    f'<p><strong>{site}</strong> — магазин компактных нагревателей <strong>LIL SOLID</strong>. '
                    f'Модели <strong>3.0</strong>, <strong>DUAL</strong> с кейсом и новинка <strong>4.0</strong> — '
                    f'оригинал PMI, совместимость с HEETS и Fiit.</p>'
                    f'<p>Сравните поколения, выберите цвет и оформите бронь. Доставка по России, оплата при получении.</p>'
                ),
            },
            'exclusive': {
                'meta_description': (
                    f'Редкие и лимитированные устройства в {site}. Основной каталог — LIL SOLID; '
                    f'эксклюзивы ILUMA — по наличию.'
                ),
                'meta_keywords': (
                    f'лимитированный LIL, exclusive {site}, {city}'
                ),
            },
        }

    # specialist — iluma-iqos
    return {
        'iqos-iluma': {
            'meta_description': (
                f'{site}: специализированный магазин IQOS ILUMA — Iluma i One, Standart и Prime. '
                f'Только линейка ILUMA и стики TEREA. {city}, экспресс и доставка по России.'
            ),
            'meta_keywords': (
                f'ILUMA IQOS магазин, купить IQOS ILUMA специалист, Iluma i One, Iluma i Prime, {site}, {city}'
            ),
            'seo_text': (
                f'<p><strong>{site}</strong> заточен под <strong>IQOS ILUMA</strong> и стики <strong>TEREA</strong>. '
                f'Разбираемся в поколениях Iluma i, помогаем выбрать One / Standart / Prime под ваш ритм.</p>'
                f'<p>SMARTCORE без лезвия, оригинал PMI, бронь на сайте. Экспресс по Москве и отправка в регионы.</p>'
            ),
        },
        'terea-sticks': {
            'meta_description': (
                f'Стики TEREA в {site} — узкий ассортимент под ILUMA. Блок 10 пачек, вкусы KZ. '
                f'Консультация по совместимости. {city}.'
            ),
            'meta_keywords': (
                f'TEREA ILUMA IQOS, стики TEREA специалист, блок TEREA {site}, {city}, original TEREA'
            ),
            'seo_text': (
                f'<p>В {site} стики <strong>TEREA</strong> — ключевая расходка к ILUMA. Продаём блоками (10 пачек × 20 стиков), '
                f'оригинал KZ. Подскажем вкус под крепость и ментол.</p>'
            ),
        },
        'lil': {
            'meta_description': (
                f'LIL SOLID в {site} — вспомогательная линейка рядом со специализацией IQOS ILUMA. '
                f'Оригинал, бронь.'
            ),
            'meta_keywords': (
                f'LIL SOLID {site}, HEETS к LIL, {city}'
            ),
            'seo_text': (
                f'<p>Основная экспертиза {site} — ILUMA и TEREA. <strong>LIL SOLID</strong> есть в каталоге '
                f'как альтернатива на HEETS, если нужен другой форм-фактор.</p>'
            ),
        },
        'exclusive': {
            'meta_description': (
                f'Лимитированные IQOS ILUMA в {site}: редкие цвета и Seletti. '
                f'Специализированная витрина ILUMA IQOS.'
            ),
            'meta_keywords': (
                f'limited ILUMA {site}, Seletti IQOS, {city}'
            ),
        },
    }


def build_device_model_seo(site: str, role: str) -> dict:
    """Ключи как в seo_utils DEVICE_MODEL_SEO (UPPER для hub/premium/lil)."""
    city = 'Москва'
    photo = f'фото {site}'

    def entry(desc: str, kw: str, alt: str) -> dict:
        return {'meta_description': desc, 'meta_keywords': kw, 'image_alt': alt}

    if role == 'hub':
        return {
            'IQOS ILUMA I ONE': entry(
                f'IQOS ILUMA i One в хабе {site}: компактный ILUMA без лезвия. Оригинал, все цвета, бронь. {city}.',
                f'Iluma i One {site}, компактный IQOS ILUMA, SMARTCORE, {city}, original IQOS',
                f'IQOS ILUMA i One — компактный ILUMA, {photo}',
            ),
            'IQOS ILUMA I': entry(
                f'IQOS ILUMA i Standart в {site} — сбалансированная модель хаба ILUMA + LIL + TEREA. {city}.',
                f'Iluma i Standart {site}, IQOS ILUMA i, SMARTCORE, {city}',
                f'IQOS ILUMA i Standart — устройство ILUMA, {photo}',
            ),
            'IQOS ILUMA I PRIME': entry(
                f'IQOS ILUMA i Prime в {site}: премиум-автономность в общем каталоге с LIL и TEREA. {city}.',
                f'Iluma i Prime {site}, IQOS ILUMA premium, {city}, original IQOS',
                f'IQOS ILUMA i Prime — премиум ILUMA, {photo}',
            ),
            'IQOS ILUMA ONE': entry(
                f'IQOS ILUMA ONE в {site} — первое поколение ILUMA, оригинал. {city}.',
                f'IQOS ILUMA ONE {site}, {city}',
                f'IQOS ILUMA ONE, {photo}',
            ),
            'IQOS ILUMA PRIME': entry(
                f'IQOS ILUMA PRIME в {site} — премиум первого поколения ILUMA. {city}.',
                f'IQOS ILUMA PRIME {site}, {city}',
                f'IQOS ILUMA PRIME, {photo}',
            ),
            'IQOS ILUMA STANDART': entry(
                f'IQOS ILUMA STANDART в {site}. Оригинал, бронь, доставка. {city}.',
                f'IQOS ILUMA STANDART {site}, {city}',
                f'IQOS ILUMA STANDART, {photo}',
            ),
            'LIL SOLID DUAL': entry(
                f'LIL SOLID DUAL в хабе {site}: кейс + два режима, рядом с ILUMA. {city}.',
                f'LIL SOLID DUAL {site}, LIL с кейсом, {city}, original LIL',
                f'LIL SOLID DUAL, {photo}',
            ),
            'LIL SOLID 3.0': entry(
                f'LIL SOLID 3.0 в {site} — компактный LIL в общем каталоге. {city}.',
                f'LIL SOLID 3.0 {site}, купить LIL 3.0, {city}',
                f'LIL SOLID 3.0, {photo}',
            ),
            'LIL SOLID 4.0': entry(
                f'LIL SOLID 4.0 в {site} — новое поколение LIL на витрине хаба. {city}.',
                f'LIL SOLID 4.0 {site}, новинка LIL, {city}',
                f'LIL SOLID 4.0, {photo}',
            ),
        }

    if role == 'premium':
        return {
            'IQOS ILUMA I ONE': entry(
                f'Премиум-витрина {site}: IQOS ILUMA i One — компактный оригинал SMARTCORE. {city}.',
                f'Iluma i One премиум, {site}, luxury IQOS, {city}',
                f'IQOS ILUMA i One, {photo}',
            ),
            'IQOS ILUMA I': entry(
                f'IQOS ILUMA i Standart в {site} — премиальный баланс размера и батареи. {city}.',
                f'Iluma i Standart {site}, премиум IQOS, {city}',
                f'IQOS ILUMA i Standart, {photo}',
            ),
            'IQOS ILUMA I PRIME': entry(
                f'IQOS ILUMA i Prime в {site} — флагман премиум-линейки. Максимальная автономность. {city}.',
                f'Iluma i Prime {site}, флагман IQOS ILUMA, {city}',
                f'IQOS ILUMA i Prime, {photo}',
            ),
            'IQOS ILUMA ONE': entry(
                f'IQOS ILUMA ONE в премиум-каталоге {site}. Оригинал. {city}.',
                f'IQOS ILUMA ONE {site}, {city}',
                f'IQOS ILUMA ONE, {photo}',
            ),
            'IQOS ILUMA PRIME': entry(
                f'IQOS ILUMA PRIME в {site}. Премиум первого поколения. {city}.',
                f'IQOS ILUMA PRIME {site}, {city}',
                f'IQOS ILUMA PRIME, {photo}',
            ),
            'IQOS ILUMA STANDART': entry(
                f'IQOS ILUMA STANDART в {site}. Оригинал, бронь. {city}.',
                f'IQOS ILUMA STANDART {site}, {city}',
                f'IQOS ILUMA STANDART, {photo}',
            ),
            'LIL SOLID DUAL': entry(
                f'LIL SOLID DUAL в {site} — дополнительная линейка к премиум ILUMA. {city}.',
                f'LIL SOLID DUAL {site}, {city}',
                f'LIL SOLID DUAL, {photo}',
            ),
            'LIL SOLID 3.0': entry(
                f'LIL SOLID 3.0 в ассортименте {site}. Фокус витрины — IQOS ILUMA. {city}.',
                f'LIL SOLID 3.0 {site}, {city}',
                f'LIL SOLID 3.0, {photo}',
            ),
            'LIL SOLID 4.0': entry(
                f'LIL SOLID 4.0 в {site}. Компактная альтернатива премиум ILUMA. {city}.',
                f'LIL SOLID 4.0 {site}, {city}',
                f'LIL SOLID 4.0, {photo}',
            ),
        }

    if role == 'lil':
        return {
            'IQOS ILUMA I ONE': entry(
                f'IQOS ILUMA i One в {site} — дополнительная модель рядом с каталогом LIL SOLID. {city}.',
                f'Iluma i One {site}, {city}',
                f'IQOS ILUMA i One, {photo}',
            ),
            'IQOS ILUMA I': entry(
                f'IQOS ILUMA i Standart в магазине LIL SOLID ({site}). {city}.',
                f'Iluma i Standart {site}, {city}',
                f'IQOS ILUMA i Standart, {photo}',
            ),
            'IQOS ILUMA I PRIME': entry(
                f'IQOS ILUMA i Prime в {site}. Основной фокус — устройства LIL. {city}.',
                f'Iluma i Prime {site}, {city}',
                f'IQOS ILUMA i Prime, {photo}',
            ),
            'IQOS ILUMA ONE': entry(
                f'IQOS ILUMA ONE в {site}. {city}.',
                f'IQOS ILUMA ONE {site}, {city}',
                f'IQOS ILUMA ONE, {photo}',
            ),
            'IQOS ILUMA PRIME': entry(
                f'IQOS ILUMA PRIME в {site}. {city}.',
                f'IQOS ILUMA PRIME {site}, {city}',
                f'IQOS ILUMA PRIME, {photo}',
            ),
            'IQOS ILUMA STANDART': entry(
                f'IQOS ILUMA STANDART в {site}. {city}.',
                f'IQOS ILUMA STANDART {site}, {city}',
                f'IQOS ILUMA STANDART, {photo}',
            ),
            'LIL SOLID DUAL': entry(
                f'Купить LIL SOLID DUAL в {site} — магазин LIL: кейс, два режима, HEETS/Fiit. {city}.',
                f'купить LIL SOLID DUAL, LIL DUAL {site}, original LIL, {city}',
                f'LIL SOLID DUAL — устройство LIL с кейсом, {photo}',
            ),
            'LIL SOLID 3.0': entry(
                f'Купить LIL SOLID 3.0 в {site}: компактный нагреватель LIL, все цвета. {city}.',
                f'купить LIL SOLID 3.0, LIL 3.0 {site}, {city}, original LIL',
                f'LIL SOLID 3.0 — компактный LIL, {photo}',
            ),
            'LIL SOLID 4.0': entry(
                f'Купить LIL SOLID 4.0 в {site} — новинка линейки LIL, оригинал. {city}.',
                f'купить LIL SOLID 4.0, LIL 4.0 {site}, новинка LIL, {city}',
                f'LIL SOLID 4.0 — новое поколение LIL, {photo}',
            ),
        }

    # specialist — keys may be title-case on iluma; provide both styles
    base = {
        'IQOS ILUMA I ONE': entry(
            f'{site}: IQOS ILUMA i One — компактный специалитетный выбор без лезвия. {city}.',
            f'Iluma i One {site}, специалист IQOS ILUMA, SMARTCORE, {city}',
            f'IQOS ILUMA i One, {photo}',
        ),
        'IQOS ILUMA I': entry(
            f'{site}: IQOS ILUMA i Standart — экспертный подбор под ежедневное использование. {city}.',
            f'Iluma i Standart {site}, {city}',
            f'IQOS ILUMA i Standart, {photo}',
        ),
        'IQOS ILUMA I PRIME': entry(
            f'{site}: IQOS ILUMA i Prime — флагман для тех, кто выбирает только ILUMA. {city}.',
            f'Iluma i Prime {site}, флагман ILUMA, {city}',
            f'IQOS ILUMA i Prime, {photo}',
        ),
        'IQOS ILUMA ONE': entry(
            f'IQOS ILUMA ONE в специализированном магазине {site}. {city}.',
            f'IQOS ILUMA ONE {site}, {city}',
            f'IQOS ILUMA ONE, {photo}',
        ),
        'IQOS ILUMA PRIME': entry(
            f'IQOS ILUMA PRIME в {site}. {city}.',
            f'IQOS ILUMA PRIME {site}, {city}',
            f'IQOS ILUMA PRIME, {photo}',
        ),
        'IQOS ILUMA STANDART': entry(
            f'IQOS ILUMA STANDART в {site}. {city}.',
            f'IQOS ILUMA STANDART {site}, {city}',
            f'IQOS ILUMA STANDART, {photo}',
        ),
        'LIL SOLID DUAL': entry(
            f'LIL SOLID DUAL в {site} — вспомогательная модель рядом со специализацией ILUMA. {city}.',
            f'LIL SOLID DUAL {site}, {city}',
            f'LIL SOLID DUAL, {photo}',
        ),
        'LIL SOLID 3.0': entry(
            f'LIL SOLID 3.0 в {site}. Основной фокус — IQOS ILUMA и TEREA. {city}.',
            f'LIL SOLID 3.0 {site}, {city}',
            f'LIL SOLID 3.0, {photo}',
        ),
        'LIL SOLID 4.0': entry(
            f'LIL SOLID 4.0 в {site}. {city}.',
            f'LIL SOLID 4.0 {site}, {city}',
            f'LIL SOLID 4.0, {photo}',
        ),
    }
    # iluma title-case aliases
    base['IQOS Iluma i One'] = base['IQOS ILUMA I ONE']
    base['IQOS Iluma i Standart'] = base['IQOS ILUMA I']
    base['IQOS Iluma i Prime'] = base['IQOS ILUMA I PRIME']
    return base
