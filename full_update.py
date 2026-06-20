#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ПОЛНОЕ ОБНОВЛЕНИЕ БАЗЫ ДАННЫХ СО ВСЕМИ ТОВАРАМИ ИЗ EXCEL
Всего товаров: 35 (13 стиков + 22 устройства)
"""

import os
import sqlite3
import json
from datetime import datetime

# ===================== ВСЕ СТИКИ (13 ПОЗИЦИЙ) =====================

STICKS = [
    {
        'name': 'Terea Purple Wave KZ',
        'description': '''Стики TEREA Purple Wave для IQOS ILUMA — это насыщенный вкус с яркими ягодными нотами и освежающим ментоловым эффектом.

<b>Вкус:</b> Фруктовый, Ментол
<b>Крепость:</b> Средние
<b>Совместимость:</b> IQOS ILUMA
<b>Количество:</b> 20 стиков в упаковке

Отличный выбор для тех, кто предпочитает свежие и фруктовые ароматы с ноткой прохлады.''',
        'price': 3750,
        'category': 'Стики TEREA',
        'image': 'terea_purple_wave_kz.jpg',
        # 'images': ['terea_purple_wave_kz.jpg', 'terea_purple_detail.jpg'],  # доп. изображения
    },
    {
        'name': 'Terea Silver KZ',
        'description': '''Стики TEREA Silver для IQOS ILUMA — это мягкий табачный вкус с легкими ореховыми нотами.

<b>Вкус:</b> Табачный
<b>Крепость:</b> Средние
<b>Совместимость:</b> IQOS ILUMA
<b>Количество:</b> 20 стиков в упаковке

Обеспечивают комфортное использование благодаря технологии нагрева без лезвий и подойдут тем, кто предпочитает более мягкие ароматы.''',
        'price': 3750,
        'category': 'Стики TEREA',
        'image': 'terea_silver_kz.jpg'
    },
    {
        'name': 'Terea Amber KZ',
        'description': '''Стики TEREA Amber для IQOS ILUMA — это насыщенный табачный вкус с легкими древесными и ореховыми нотами.

<b>Вкус:</b> Табачный
<b>Крепость:</b> Крепкие
<b>Совместимость:</b> IQOS ILUMA
<b>Количество:</b> 20 стиков в упаковке

Идеально подходят для тех, кто ценит сбалансированные ароматы с глубиной и насыщенностью.''',
        'price': 3750,
        'category': 'Стики TEREA',
        'image': 'terea_amber_kz.jpg'
    },
    {
        'name': 'Terea Zing Wave KZ',
        'description': '''Стики TEREA Zing Wave для IQOS ILUMA — это яркое сочетание цитрусовых нот и освежающего ментола.

<b>Вкус:</b> Фруктовый (Цитрус), Ментол
<b>Крепость:</b> Легкие
<b>Совместимость:</b> IQOS ILUMA
<b>Количество:</b> 20 стиков в упаковке

Этот вкус идеально подойдет тем, кто любит насыщенные и свежие ароматы.''',
        'price': 3750,
        'category': 'Стики TEREA',
        'image': 'terea_zing_wave_kz.jpg'
    },
    {
        'name': 'Terea Turquoise KZ',
        'description': '''Стики TEREA Turquoise для IQOS ILUMA предлагают освежающее сочетание мяты с легкими фруктовыми нотками.

<b>Вкус:</b> Фруктовый, Ментол
<b>Крепость:</b> Средние
<b>Совместимость:</b> IQOS ILUMA
<b>Количество:</b> 20 стиков в упаковке

Идеальный выбор для тех, кто ищет баланс между яркостью аромата и мягкостью табачного вкуса.''',
        'price': 3750,
        'category': 'Стики TEREA',
        'image': 'terea_turquoise_kz.jpg'
    },
    {
        'name': 'Terea Summer Wave KZ',
        'description': '''Стики TEREA Summer Wave для IQOS ILUMA предлагают освежающее сочетание тропических фруктов и ментола.

<b>Вкус:</b> Экзотические (Тропические фрукты)
<b>Крепость:</b> Средние
<b>Совместимость:</b> IQOS ILUMA
<b>Количество:</b> 20 стиков в упаковке

Этот вкус идеально подходит для летних дней, когда хочется легкости и свежести.''',
        'price': 3750,
        'category': 'Стики TEREA',
        'image': 'terea_summer_wave_kz.jpg'
    },
    {
        'name': 'Terea Yellow KZ',
        'description': '''Стики TEREA Yellow для IQOS ILUMA — это мягкий табачный вкус, дополненный освежающими цитрусовыми нотками.

<b>Вкус:</b> Табачный, Фруктовый (Цитрус)
<b>Крепость:</b> Средние
<b>Совместимость:</b> IQOS ILUMA
<b>Количество:</b> 20 стиков в упаковке

Благодаря системе нагрева без лезвий обеспечивают чистоту и насыщенность вкуса без дыма и пепла.''',
        'price': 3750,
        'category': 'Стики TEREA',
        'image': 'terea_yellow_kz.jpg'
    },
    {
        'name': 'Terea Starling Pearl',
        'description': '''Стики TEREA Starling Pearl (Тереа Старлин Пёрл) для IQOS ILUMA с капсулой, со вкусом клубники с базиликом и ментолом.

<b>Вкус:</b> Табачный, Фруктовый (Клубника), Экзотические (Базилик), Ментол
<b>Крепость:</b> Средние
<b>Совместимость:</b> IQOS ILUMA
<b>Количество:</b> 20 стиков в упаковке
<b>Особенность:</b> Капсула внутри

Если не нажимать на кнопку, стик имеет насыщенный табачный аромат. При нажатии капсула добавляет освежающий вкус клубники с базиликом.''',
        'price': 3750,
        'category': 'Стики TEREA',
        'image': 'terea_starling_pearl.jpg'
    },
    {
        'name': 'Terea Sun Pearl KZ',
        'description': '''Стики TEREA Sun Pearl для IQOS ILUMA — это сочетание освежающего ментолового охлаждения и насыщенного аромата арбуза.

<b>Вкус:</b> Фруктовый (Арбуз), Ментол
<b>Крепость:</b> Средние
<b>Совместимость:</b> IQOS ILUMA
<b>Количество:</b> 20 стиков в упаковке

Идеальный выбор для любителей ярких и фруктовых вкусов. Обеспечивают чистый вкус благодаря инновационной технологии нагрева без лезвий.''',
        'price': 3750,
        'category': 'Стики TEREA',
        'image': 'terea_sun_pearl_kz.jpg'
    },
    {
        'name': 'Terea Twilight Pearl KZ',
        'description': '''Стики TEREA Twilight Pearl для IQOS ILUMA — это насыщенный табачный вкус с мягкими фруктовыми нотами.

<b>Вкус:</b> Табачный, Фруктовый
<b>Крепость:</b> Средние
<b>Совместимость:</b> IQOS ILUMA
<b>Количество:</b> 20 стиков в упаковке
<b>Особенность:</b> Капсула внутри

Прекрасный выбор для тех, кто предпочитает гармоничные сочетания аромата и крепости.''',
        'price': 3750,
        'category': 'Стики TEREA',
        'image': 'terea_twilight_pearl_kz.jpg'
    },
    {
        'name': 'Terea Blue KZ',
        'description': '''Стики TEREA Blue для IQOS ILUMA — это освежающий ментоловый вкус с легкими нотами мяты.

<b>Вкус:</b> Ментол
<b>Крепость:</b> Средние
<b>Совместимость:</b> IQOS ILUMA
<b>Количество:</b> 20 стиков в упаковке

Создают яркое и чистое ощущение прохлады. Идеально подходят для тех, кто ищет баланс между свежестью и насыщенностью.''',
        'price': 3750,
        'category': 'Стики TEREA',
        'image': 'terea_blue_kz.jpg'
    },
    {
        'name': 'Terea Tidal Pearl KZ',
        'description': '''Стики TEREA Tidal Pearl (Briza Pearl) для IQOS ILUMA — это насыщенный вкус поджаренного табака с тонкими древесными нотками и ароматом чая.

<b>Вкус:</b> Табачный, Древесные ноты, Чай
<b>Крепость:</b> Средние
<b>Совместимость:</b> IQOS ILUMA
<b>Количество:</b> 20 стиков в упаковке
<b>Особенность:</b> Капсула внутри

Одно нажатие активирует капсулу, превращая аромат в освежающий ментоловый вкус.''',
        'price': 3750,
        'category': 'Стики TEREA',
        'image': 'terea_tidal_pearl_kz.jpg'
    },
    {
        'name': 'Terea Provience Pearl KZ',
        'description': '''Стики TEREA Provience Pearl для IQOS ILUMA с капсулой, со вкусом винограда и ментола.

<b>Вкус:</b> Фруктовый (Виноград), Ментол
<b>Крепость:</b> Средние
<b>Совместимость:</b> IQOS ILUMA
<b>Количество:</b> 20 стиков в упаковке
<b>Особенность:</b> Капсула внутри

Насыщенный вкус винограда с освежающим ментоловым послевкусием.''',
        'price': 3750,
        'category': 'Стики TEREA',
        'image': 'terea_provience_pearl_kz.jpg'
    }
]

# ===================== ВСЕ УСТРОЙСТВА (22 ПОЗИЦИИ) =====================

DEVICES = [
    # IQOS Iluma i One (6 шт)
    {
        'name': 'IQOS Iluma i One Breeze Blue',
        'description': '''<b>IQOS Iluma i One</b> в цвете Breeze Blue — компактное устройство без лезвия с технологией SMARTCORE. Система нагрева табака изнутри обеспечивает насыщенный вкус без горения. Небесно-голубой цвет корпуса подойдёт тем, кто ценит стиль и лаконичность.

<b>Характеристики:</b>
• <b>Размеры:</b> 130 × 25 × 15 мм
• <b>Вес:</b> 45 г
• <b>Время зарядки:</b> 60 минут
• <b>Сеансов:</b> до 25
• <b>Цвет:</b> Breeze Blue (небесно-голубой)''',
        'price': 8499,
        'category': 'IQOS ILUMA',
        'image': 'iqos_iluma_i_one_breeze_blue.jpg'
    },
    {
        'name': 'IQOS Iluma i One Vivid Terracotta',
        'description': '''<b>IQOS Iluma i One</b> в цвете Vivid Terracotta — компактное устройство без лезвия. Терракотовый оттенок подойдёт для тех, кто предпочитает тёплые и сдержанные тона. Технология SMARTCORE обеспечивает стабильный вкус и простоту использования.

<b>Характеристики:</b>
• <b>Размеры:</b> 130 × 25 × 15 мм
• <b>Вес:</b> 45 г
• <b>Время зарядки:</b> 60 минут
• <b>Сеансов:</b> до 25
• <b>Цвет:</b> Vivid Terracotta (терракотовый)''',
        'price': 8499,
        'category': 'IQOS ILUMA',
        'image': 'iqos_iluma_i_one_vivid_terracotta.jpg'
    },
    {
        'name': 'IQOS Iluma i One Midnight Black',
        'description': '''<b>IQOS Iluma i One</b> в цвете Midnight Black — классический чёрный вариант. Устройство без лезвия с технологией SMARTCORE, компактное и удобное для ежедневного использования. Универсальный дизайн подойдёт для любого стиля.

<b>Характеристики:</b>
• <b>Размеры:</b> 130 × 25 × 15 мм
• <b>Вес:</b> 45 г
• <b>Время зарядки:</b> 60 минут
• <b>Сеансов:</b> до 25
• <b>Цвет:</b> Midnight Black (черный)''',
        'price': 8499,
        'category': 'IQOS ILUMA',
        'image': 'iqos_iluma_i_one_midnight_black.jpg'
    },
    {
        'name': 'IQOS Iluma i One Digital Violet',
        'description': '''<b>IQOS Iluma i One</b> в цвете Digital Violet — стильное устройство в фиолетовом исполнении. Компактный формат и технология SMARTCORE без лезвия. Яркий цвет для тех, кто хочет выделиться.

<b>Характеристики:</b>
• <b>Размеры:</b> 130 × 25 × 15 мм
• <b>Вес:</b> 45 г
• <b>Время зарядки:</b> 60 минут
• <b>Сеансов:</b> до 25
• <b>Цвет:</b> Digital Violet (фиолетовый)''',
        'price': 8499,
        'category': 'IQOS ILUMA',
        'image': 'iqos_iluma_i_one_digital_violet.jpg'
    },
    {
        'name': 'IQOS Iluma i One Leaf Green',
        'description': '''<b>IQOS Iluma i One</b> в цвете Leaf Green — компактное устройство в зелёном цвете. Технология без лезвия с керамическим нагревателем SMARTCORE. Свежий и приятный оттенок для повседневного использования.

<b>Характеристики:</b>
• <b>Размеры:</b> 130 × 25 × 15 мм
• <b>Вес:</b> 45 г
• <b>Время зарядки:</b> 60 минут
• <b>Сеансов:</b> до 25
• <b>Цвет:</b> Leaf Green (зеленый)''',
        'price': 8499,
        'category': 'IQOS ILUMA',
        'image': 'iqos_iluma_i_one_leaf_green.jpg'
    },
    {
        'name': 'IQOS Iluma i One Anniversary Model Limited edition',
        'description': '''<b>IQOS Iluma i One Anniversary Model</b> — лимитированная юбилейная версия с уникальным дизайном. Компактное устройство без лезвия в специальном исполнении. Идеальный вариант для коллекционеров и ценителей эксклюзива.

<b>Характеристики:</b>
• <b>Размеры:</b> 130 × 25 × 15 мм
• <b>Вес:</b> 45 г
• <b>Время зарядки:</b> 60 минут
• <b>Сеансов:</b> до 25
• <b>Особенность:</b> лимитированная серия''',
        'price': 13000,
        'category': 'IQOS ILUMA',
        'image': 'iqos_iluma_i_one_anniversary_limited.jpg'
    },
    {
        'name': 'IQOS Iluma i One Seletti Limited edition',
        'description': '''<b>IQOS Iluma i One Seletti Limited</b> — коллаборация с итальянским брендом Seletti. Уникальный дизайн в духе итальянского искусства. Лимитированная серия для тех, кто ценит эксклюзивность и стиль.

<b>Характеристики:</b>
• <b>Размеры:</b> 130 × 25 × 15 мм
• <b>Вес:</b> 45 г
• <b>Время зарядки:</b> 60 минут
• <b>Сеансов:</b> до 25
• <b>Особенность:</b> уникальный дизайн от Seletti''',
        'price': 14000,
        'category': 'IQOS ILUMA',
        'image': 'iqos_iluma_i_one_seletti_limited.jpg'
    },
    
    # IQOS Iluma i Standart (5 шт + лимитированная)
    {
        'name': 'IQOS Iluma i Standart Midnight Black',
        'description': '''<b>IQOS Iluma i Standart</b> в цвете Midnight Black — сбалансированная модель между компактностью i One и премиальностью i Prime. Технология SMARTCORE без лезвия, увеличенная батарея. Классический чёрный цвет.

<b>Характеристики:</b>
• <b>Размеры:</b> 113 × 24 × 14 мм
• <b>Вес:</b> 50 г
• <b>Время зарядки:</b> 90 минут
• <b>Сеансов:</b> до 25
• <b>Цвет:</b> Midnight Black''',
        'price': 14000,
        'category': 'IQOS ILUMA',
        'image': 'iqos_iluma_i_standart_midnight_black.jpg'
    },
    {
        'name': 'IQOS Iluma i Standart Digital violet',
        'description': '''<b>IQOS Iluma i Standart</b> в цвете Digital Violet — устройство без лезвия в фиолетовом исполнении. Удобный формат и стабильная работа. Яркий цвет для индивидуального стиля.

<b>Характеристики:</b>
• <b>Размеры:</b> 113 × 24 × 14 мм
• <b>Вес:</b> 50 г
• <b>Время зарядки:</b> 90 минут
• <b>Сеансов:</b> до 25
• <b>Цвет:</b> Digital Violet''',
        'price': 14000,
        'category': 'IQOS ILUMA',
        'image': 'iqos_iluma_i_standart_digital_violet.jpg'
    },
    {
        'name': 'IQOS Iluma i Standard Leaf Green',
        'description': '''<b>IQOS Iluma i Standart</b> в цвете Leaf Green — зелёный оттенок для любителей свежих и природных тонов. Технология SMARTCORE, до 25 сеансов без подзарядки.

<b>Характеристики:</b>
• <b>Размеры:</b> 113 × 24 × 14 мм
• <b>Вес:</b> 50 г
• <b>Время зарядки:</b> 90 минут
• <b>Сеансов:</b> до 25
• <b>Цвет:</b> Leaf Green''',
        'price': 14000,
        'category': 'IQOS ILUMA',
        'image': 'iqos_iluma_i_standart_leaf_green.jpg'
    },
    {
        'name': 'IQOS Iluma i Standart Breeze Blue',
        'description': '''<b>IQOS Iluma i Standart</b> в цвете Breeze Blue — небесно-голубой вариант. Устройство без лезвия с увеличенным временем работы. Стильный и практичный выбор.

<b>Характеристики:</b>
• <b>Размеры:</b> 113 × 24 × 14 мм
• <b>Вес:</b> 50 г
• <b>Время зарядки:</b> 90 минут
• <b>Сеансов:</b> до 25
• <b>Цвет:</b> Breeze Blue''',
        'price': 14000,
        'category': 'IQOS ILUMA',
        'image': 'iqos_iluma_i_standart_breeze_blue.jpg'
    },
    {
        'name': 'IQOS Iluma i Standart Vivid Terracotta',
        'description': '''<b>IQOS Iluma i Standart</b> в цвете Vivid Terracotta — тёплый терракотовый оттенок. Сбалансированная модель с технологией SMARTCORE. Универсальный дизайн.

<b>Характеристики:</b>
• <b>Размеры:</b> 113 × 24 × 14 мм
• <b>Вес:</b> 50 г
• <b>Время зарядки:</b> 90 минут
• <b>Сеансов:</b> до 25
• <b>Цвет:</b> Vivid Terracotta''',
        'price': 14000,
        'category': 'IQOS ILUMA',
        'image': 'iqos_iluma_i_standart_vivid_terracotta.jpg'
    },
    {
        'name': 'Iqos Iluma i Standart Seletti',
        'description': '''<b>IQOS Iluma i Standart Seletti</b> — лимитированная версия в коллаборации с итальянским брендом Seletti. Уникальный художественный дизайн. Для ценителей эксклюзива.

<b>Характеристики:</b>
• <b>Размеры:</b> 113 × 24 × 14 мм
• <b>Вес:</b> 50 г
• <b>Время зарядки:</b> 90 минут
• <b>Сеансов:</b> до 25
• <b>Особенность:</b> эксклюзивный дизайн от Seletti''',
        'price': 30000,
        'category': 'IQOS ILUMA',
        'image': 'iqos_iluma_i_standart_seletti.jpg'
    },
    
    # IQOS Iluma i Prime (4 шт + лимитированная)
    {
        'name': 'IQOS Iluma i Prime Midnight Black',
        'description': '''<b>IQOS Iluma i Prime</b> в цвете Midnight Black — премиальное устройство с увеличенным корпусом и батареей. Технология SMARTCORE без лезвия. Классический чёрный для делового стиля.

<b>Характеристики:</b>
• <b>Размеры:</b> 145 × 30 × 20 мм
• <b>Вес:</b> 60 г
• <b>Время зарядки:</b> 90 минут
• <b>Сеансов:</b> до 25
• <b>Цвет:</b> Midnight Black''',
        'price': 17000,
        'category': 'IQOS ILUMA',
        'image': 'iqos_iluma_i_prime_midnight_black.jpg'
    },
    {
        'name': 'IQOS Iluma i Prime Breeze Blue',
        'description': '''<b>IQOS Iluma i Prime</b> в цвете Breeze Blue — премиальная модель в небесно-голубом. Увеличенный корпус, до 25 сеансов. Стиль и функциональность.

<b>Характеристики:</b>
• <b>Размеры:</b> 145 × 30 × 20 мм
• <b>Вес:</b> 60 г
• <b>Время зарядки:</b> 90 минут
• <b>Сеансов:</b> до 25
• <b>Цвет:</b> Breeze Blue''',
        'price': 17000,
        'category': 'IQOS ILUMA',
        'image': 'iqos_iluma_i_prime_breeze_blue.jpg'
    },
    {
        'name': 'IQOS Iluma i Prime Garnet Red',
        'description': '''<b>IQOS Iluma i Prime</b> в цвете Garnet Red — премиальное устройство в гранатово-красном. Выразительный цвет для смелого образа. Технология SMARTCORE.

<b>Характеристики:</b>
• <b>Размеры:</b> 145 × 30 × 20 мм
• <b>Вес:</b> 60 г
• <b>Время зарядки:</b> 90 минут
• <b>Сеансов:</b> до 25
• <b>Цвет:</b> Garnet Red''',
        'price': 17000,
        'category': 'IQOS ILUMA',
        'image': 'iqos_iluma_i_prime_garnet_red.jpg'
    },
    {
        'name': 'IQOS Iluma i Prime Aspen Green',
        'description': '''<b>IQOS Iluma i Prime</b> в цвете Aspen Green — премиальная модель в зелёном цвете осины. Увеличенная батарея, до 25 сеансов. Элегантный и сдержанный дизайн.

<b>Характеристики:</b>
• <b>Размеры:</b> 145 × 30 × 20 мм
• <b>Вес:</b> 60 г
• <b>Время зарядки:</b> 90 минут
• <b>Сеансов:</b> до 25
• <b>Цвет:</b> Aspen Green''',
        'price': 17000,
        'category': 'IQOS ILUMA',
        'image': 'iqos_iluma_i_prime_aspen_green.jpg'
    },
    {
        'name': 'IQOS ILUMA I PRIME SELETTI LIMITED EDITION',
        'description': '''<b>IQOS ILUMA I PRIME SELETTI LIMITED</b> — эксклюзивная коллаборация с итальянским брендом Seletti. Лимитированная премиальная модель с уникальным дизайном. Для настоящих коллекционеров.

<b>Характеристики:</b>
• <b>Размеры:</b> 145 × 30 × 20 мм
• <b>Вес:</b> 60 г
• <b>Время зарядки:</b> 90 минут
• <b>Сеансов:</b> до 25
• <b>Особенность:</b> уникальный дизайн от Seletti''',
        'price': 44990,
        'category': 'IQOS ILUMA',
        'image': 'iqos_iluma_i_prime_seletti_limited.jpg'
    },
    
    # lil SOLID DUAL (4 шт)
    {
        'name': 'lil SOLID DUAL Чёрный Титан',
        'description': '''<b>lil SOLID DUAL</b> в цвете Чёрный Титан — компактное устройство с кейсом для зарядки. Совместимо со стиками HEETS и FIT. Классический тёмный цвет, до 30 сеансов от полного кейса.

<b>Характеристики:</b>
• <b>Аккумулятор:</b> 300 мАч + 2900 мАч (кейс)
• <b>Время нагрева:</b> 10 секунд
• <b>Сеансов:</b> до 30
• <b>Совместимость:</b> HEETS и FIT
• <b>Цвет:</b> Чёрный Титан''',
        'price': 5500,
        'category': 'LIL',
        'image': 'lil_solid_dual_black_titan.jpg'
    },
    {
        'name': 'lil SOLID DUAL Зелёный Кобальт',
        'description': '''<b>lil SOLID DUAL</b> в цвете Зелёный Кобальт — устройство с зарядным кейсом. Работает со стиками HEETS и FIT. Зелёно-синий оттенок для яркого образа. До 30 сеансов.

<b>Характеристики:</b>
• <b>Аккумулятор:</b> 300 мАч + 2900 мАч (кейс)
• <b>Время нагрева:</b> 10 секунд
• <b>Сеансов:</b> до 30
• <b>Совместимость:</b> HEETS и FIT
• <b>Цвет:</b> Зелёный Кобальт''',
        'price': 5500,
        'category': 'LIL',
        'image': 'lil_solid_dual_green_cobalt.jpg'
    },
    {
        'name': 'lil SOLID DUAL Белый Хром',
        'description': '''<b>lil SOLID DUAL</b> в цвете Белый Хром — компактное устройство с кейсом. Светлый хромированный корпус. Совместимость с HEETS и FIT. Практичный и стильный выбор.

<b>Характеристики:</b>
• <b>Аккумулятор:</b> 300 мАч + 2900 мАч (кейс)
• <b>Время нагрева:</b> 10 секунд
• <b>Сеансов:</b> до 30
• <b>Совместимость:</b> HEETS и FIT
• <b>Цвет:</b> Белый Хром''',
        'price': 5500,
        'category': 'LIL',
        'image': 'lil_solid_dual_white_chrome.jpg'
    },
    {
        'name': 'lil SOLID DUAL Красная Медь',
        'description': '''<b>lil SOLID DUAL</b> в цвете Красная Медь — устройство с зарядным кейсом в медном оттенке. Совместимо с HEETS и FIT. Выразительный цвет, до 30 сеансов от кейса.

<b>Характеристики:</b>
• <b>Аккумулятор:</b> 300 мАч + 2900 мАч (кейс)
• <b>Время нагрева:</b> 10 секунд
• <b>Сеансов:</b> до 30
• <b>Совместимость:</b> HEETS и FIT
• <b>Цвет:</b> Красная Медь''',
        'price': 5500,
        'category': 'LIL',
        'image': 'lil_solid_dual_red_copper.jpg'
    },
    
    # lil SOLID 3.0 (4 шт)
    {
        'name': 'lil SOLID 3.0 Чёрный',
        'description': '''<b>lil SOLID 3.0</b> в цвете Чёрный — компактное устройство с двумя режимами интенсивности. Съёмный нагреватель, до 3 стиков подряд. Классический чёрный цвет.

<b>Характеристики:</b>
• <b>Режимы:</b> 2 режима интенсивности
• <b>Нагреватель:</b> съемный
• <b>Сеансов:</b> до 3 стиков подряд
• <b>Цвет:</b> Чёрный''',
        'price': 3500,
        'category': 'LIL',
        'image': 'lil_solid_30_black.jpg'
    },
    {
        'name': 'lil SOLID 3.0 Зелёный',
        'description': '''<b>lil SOLID 3.0</b> в цвете Зелёный — устройство с двумя режимами нагрева. Съёмный нагреватель для удобства. Зелёный корпус, до 3 стиков подряд.

<b>Характеристики:</b>
• <b>Режимы:</b> 2 режима интенсивности
• <b>Нагреватель:</b> съемный
• <b>Сеансов:</b> до 3 стиков подряд
• <b>Цвет:</b> Зелёный''',
        'price': 3500,
        'category': 'LIL',
        'image': 'lil_solid_30_green.jpg'
    },
    {
        'name': 'lil SOLID 3.0 Золотой',
        'description': '''<b>lil SOLID 3.0</b> в цвете Золотой — компактный девайс с премиальным золотым оттенком. Два режима интенсивности, съёмный нагреватель. Стильный выбор.

<b>Характеристики:</b>
• <b>Режимы:</b> 2 режима интенсивности
• <b>Нагреватель:</b> съемный
• <b>Сеансов:</b> до 3 стиков подряд
• <b>Цвет:</b> Золотой''',
        'price': 3500,
        'category': 'LIL',
        'image': 'lil_solid_30_gold.jpg'
    },
    {
        'name': 'lil SOLID 3.0 Синий',
        'description': '''<b>lil SOLID 3.0</b> в цвете Синий — устройство с двумя режимами нагрева. Съёмный нагреватель, до 3 стиков подряд. Синий корпус для яркого образа.

<b>Характеристики:</b>
• <b>Режимы:</b> 2 режима интенсивности
• <b>Нагреватель:</b> съемный
• <b>Сеансов:</b> до 3 стиков подряд
• <b>Цвет:</b> Синий''',
        'price': 3500,
        'category': 'LIL',
        'image': 'lil_solid_30_blue.jpg'
    }
]

# ===================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====================

def slugify(name):
    """Генерирует slug из названия"""
    import re
    s = name.lower()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    return s.strip('-')[:100] if s else 'product'

# ===================== МАППИНГ ИЗОБРАЖЕНИЙ (из папок Devices/ и Sticks/) =====================

IMAGE_MAP = {
    'Terea Purple Wave KZ': 'Sticks/Terea Purple Wave KZ/cr13289_h208450_pmi_switzerland_terea_3_quarter_right_single_mauve_wave_angle-1-600x600-1.png',
    'Terea Silver KZ': 'Sticks/Terea Silver KZ/cr13289_h208450_pmi_switzerland_terea_3_quarter_right_single_silver_angle-1-1-600x600-1.png',
    'Terea Amber KZ': 'Sticks/Terea Amber KZ/cr13289_h208450_pmi_switzerland_terea_3_quarter_right_single_amber_angle-1-600x600-1.png',
    'Terea Zing Wave KZ': 'Sticks/Terea Zing Wave KZ/terea-green-zing-photoroom-1-1.png',
    'Terea Turquoise KZ': 'Sticks/Terea Turquoise KZ/cr13289_h208450_pmi_switzerland_terea_3_quarter_right_single_turquoise_angle-1-600x600-1.png',
    'Terea Summer Wave KZ': 'Sticks/Terea Summer Wave KZ/terea-summer-breeze-1.png',
    'Terea Yellow KZ': 'Sticks/Terea Yellow KZ/cr13289_h208450_pmi_switzerland_terea_3_quarter_right_single_yellow_angle-1.png',
    'Terea Starling Pearl': 'Sticks/Terea Starling Pearl/terea-starling-pearl-1-768x768.webp',
    'Terea Sun Pearl KZ': 'Sticks/Terea Sun Pearl KZ/terea-sun-pearl-rok-1-1-1024x970-1-768x728.webp',
    'Terea Twilight Pearl KZ': 'Sticks/Terea Twilight Pearl KZ/terea-twilight-768x768.webp',
    'Terea Blue KZ': 'Sticks/Terea Blue KZ/cr13289_h208450_pmi_switzerland_terea_3_quarter_right_single_blue_angle-1-1.png',
    'Terea Tidal Pearl KZ': 'Sticks/Terea Tidal Pearl KZ/terea-tidal-pearl-768x768.webp',
    'Terea Provience Pearl KZ': 'Sticks/Terea Provience Pearl KZ/terea-provence-pearl-768x768.webp',
    'IQOS Iluma i One Breeze Blue': 'Devices/IQOS Iluma i One Breeze Blue/pdp_iluma_i_one_breeze_blue-768x769.webp',
    'IQOS Iluma i One Vivid Terracotta': 'Devices/IQOS Iluma i One Vivid Terracotta/iluma_i_one_vivid_terracotta_-768x769.webp',
    'IQOS Iluma i One Midnight Black': 'Devices/IQOS Iluma i One Midnight Black/iluma_i_one_midnight_black_-768x769.webp',
    'IQOS Iluma i One Digital Violet': 'Devices/IQOS Iluma i One Digital Violet/iluma_i_one_digital_violet-768x769.webp',
    'IQOS Iluma i One Leaf Green': 'Devices/IQOS Iluma i One Leaf Green/iluma_i_one_leaf_green-768x769.webp',
    'IQOS Iluma i One Anniversary Model Limited edition': 'Devices/IQOS Iluma i One Anniversary Model Limited edition/10YA-LEP_ONE_02-600x600-1.jpg',
    'IQOS Iluma i One Seletti Limited edition': 'Devices/IQOS Iluma i One Seletti Limited edition/iluma-i-one-seletti-limited-edition.webp',
    'IQOS Iluma i Standart Midnight Black': 'Devices/IQOS Iluma i Standart Midnight Black/iqos_iluma_i_midnight_black.webp',
    'IQOS Iluma i Standart Digital violet': 'Devices/IQOS Iluma i Standart Digital violet/iqos_iluma_i_digital_violet.webp',
    'IQOS Iluma i Standard Leaf Green': 'Devices/IQOS Iluma i Standard Leaf Green/iqos-iluma-i-leaf-green-2.webp',
    'IQOS Iluma i Standart Breeze Blue': 'Devices/IQOS Iluma i Standart Breeze Blue/iqos_iluma_i_breeze_blue.webp',
    'IQOS Iluma i Standart Vivid Terracotta': 'Devices/IQOS Iluma i Standart Vivid Terracotta/iqos_iluma_i_vivid_terracotta.webp',
    'Iqos Iluma i Standart Seletti': 'Devices/Iqos Iluma i Standart Seletti/iqos_iluma_seletti.webp',
    'IQOS Iluma i Prime Midnight Black': 'Devices/IQOS Iluma i Prime Midnight Black/iqos_4.1_iluma_core_prime_i_midnight_black_without_terea_@1.5x.png',
    'IQOS Iluma i Prime Breeze Blue': 'Devices/IQOS Iluma i Prime Breeze Blue/iqos_4.1_iluma_core_prime_i_breeze_blue_without_terea_@1.5x.png',
    'IQOS Iluma i Prime Garnet Red': 'Devices/IQOS Iluma i Prime Garnet Red/iqos_4.1_iluma_core_prime_i_garnet_red_without_terea_@1.5x-n.png',
    'IQOS Iluma i Prime Aspen Green': 'Devices/IQOS Iluma i Prime Aspen Green/iqos-iluma-i-prime-aspen-green-photoroom-1-768x645.png',
    'IQOS ILUMA I PRIME SELETTI LIMITED EDITION': 'Devices/IQOS ILUMA I PRIME SELETTI LIMITED EDITION/iqos-iluma-i-prime-seletti-.webp',
    'lil SOLID DUAL Чёрный Титан': 'Devices/lil SOLID DUAL Чёрный Титан/9c489a07101e290c762e07d9760629c8.png',
    'lil SOLID DUAL Зелёный Кобальт': 'Devices/lil SOLID DUAL Зелёный Кобальт/311x172_1x_1x.webp',
    'lil SOLID DUAL Белый Хром': 'Devices/lil SOLID DUAL Белый Хром/35d65367-91c0-4cb6-8d32-67221e0264f6.800x600.png',
    'lil SOLID DUAL Красная Медь': 'Devices/lil SOLID DUAL Красная Медь/76ddcd14-430b-4c70-86c7-8af308d1a336.800x600.png',
    'lil SOLID 3.0 Чёрный': 'Devices/lil SOLID 3.0 Чёрный/64bd6e61-7833-4c03-acd3-34cb9b0a7b88.800x600.png',
    'lil SOLID 3.0 Зелёный': 'Devices/lil SOLID 3.0 Зелёный/mxw_20486_auto.jpg',
    'lil SOLID 3.0 Золотой': 'Devices/lil SOLID 3.0 Золотой/097866ca-2885-43cb-b9f8-b7ba8b3fd92c.800x600.png',
    'lil SOLID 3.0 Синий': 'Devices/lil SOLID 3.0 Синий/c3f72f9d-e2e3-4767-9394-499341bc2dd3.800x600.png',
}

# ===================== ФУНКЦИЯ ОБНОВЛЕНИЯ =====================

def full_update():
    print("="*70)
    print("ПОЛНОЕ ОБНОВЛЕНИЕ БАЗЫ ДАННЫХ (35 ТОВАРОВ)")
    print("="*70)
    
    # Схема БД — через Flask/SQLAlchemy (совместимо с models.py)
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from app import app, db
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shop.db')
    with app.app_context():
        try:
            from alembic_runner import run_alembic
            run_alembic()
        except Exception as e:
            print(f"  [INFO] Alembic: {e}, используем db.create_all()")
            db.create_all()
    print("  [OK] Схема БД актуальна")
    
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    # Очищаем product и category (сохраняем схему, product первым из-за FK)
    cursor.execute("DELETE FROM product")
    cursor.execute("DELETE FROM category")
    conn.commit()
    
    # Добавляем категории
    categories = [
        ('IQOS ILUMA', 'iqos-iluma', 'Устройства IQOS ILUMA', 'iqos-iluma.jpg'),
        ('Стики TEREA', 'terea-sticks', 'Стики для IQOS ILUMA', 'terea-sticks.jpg'),
        ('LIL', 'lil', 'Устройства LIL', 'lil.jpg')
    ]
    
    for name, slug, desc, img in categories:
        cursor.execute('''
            INSERT INTO category (name, slug, description, image, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, slug, desc, img, datetime.now()))
    
    print("  [OK] Категории добавлены")
    
    # Получаем ID категорий
    cursor.execute("SELECT id, slug FROM category")
    cat_ids = {slug: id for id, slug in cursor.fetchall()}
    
    # Добавляем все стики (image из IMAGE_MAP или из stick)
    for i, stick in enumerate(STICKS):
        slug = slugify(stick['name']) + f'-{i}'  # уникальность
        images_json = json.dumps(stick.get('images', [])) if stick.get('images') else None
        img = IMAGE_MAP.get(stick['name'], stick['image'])
        cursor.execute('''
            INSERT INTO product (name, slug, price, description, image, images, category_id, views, in_stock, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        ''', (stick['name'], slug, stick['price'], stick['description'], 
              img, images_json, cat_ids['terea-sticks'], 0, datetime.now()))
    
    # Добавляем все устройства (image из IMAGE_MAP или из device)
    for i, device in enumerate(DEVICES):
        cat_slug = 'iqos-iluma' if 'IQOS' in device['name'] or 'Iqos' in device['name'] else 'lil'
        slug = slugify(device['name']) + f'-{i}'
        images_json = json.dumps(device.get('images', [])) if device.get('images') else None
        img = IMAGE_MAP.get(device['name'], device['image'])
        cursor.execute('''
            INSERT INTO product (name, slug, price, description, image, images, category_id, views, in_stock, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        ''', (device['name'], slug, device['price'], device['description'], 
              img, images_json, cat_ids[cat_slug], 0, datetime.now()))
    
    conn.commit()
    conn.close()
    
    total = len(STICKS) + len(DEVICES)
    print(f"\n[OK] ОБНОВЛЕНИЕ ЗАВЕРШЕНО!")
    print(f"   • Стики: {len(STICKS)} шт.")
    print(f"   • Устройства: {len(DEVICES)} шт.")
    print(f"   • ВСЕГО: {total} шт.")

# ===================== СОЗДАНИЕ ЗАГЛУШЕК =====================

def create_thumbnails():
    """Создает изображения-заглушки для всех товаров"""
    print("\n" + "="*70)
    print("СОЗДАНИЕ ИЗОБРАЖЕНИЙ-ЗАГЛУШЕК")
    print("="*70)
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        print("  [OK] Библиотека Pillow найдена")
    except ImportError:
        print("  [ERR] Библиотека Pillow не найдена. Устанавливаю...")
        os.system("python -m pip install Pillow")
        from PIL import Image, ImageDraw, ImageFont
        print("  [OK] Библиотека Pillow установлена")
    
    # Создаем папку
    os.makedirs('static/images/products', exist_ok=True)
    print("  [OK] Папка static/images/products создана")
    
    colors = [
        (52, 152, 219), (46, 204, 113), (155, 89, 182), (231, 76, 60),
        (241, 196, 15), (230, 126, 34), (52, 73, 94), (26, 188, 156),
        (243, 156, 18), (192, 57, 43), (41, 128, 185), (39, 174, 96),
        (142, 68, 173), (22, 160, 133), (211, 84, 0), (44, 62, 80)
    ]
    
    all_products = STICKS + DEVICES
    print(f"\n  Создание {len(all_products)} изображений:")
    
    for i, product in enumerate(all_products):
        color = colors[i % len(colors)]
        filepath = f"static/images/products/{product['image']}"
        
        # Создаем изображение
        img = Image.new('RGB', (400, 400), color=color)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.load_default()
            name = product['name']
            if len(name) > 30:
                name = name[:27] + '...'
            
            draw.text((50, 150), name, fill=(255, 255, 255), font=font)
            draw.text((50, 200), f"{product['price']} ₽", fill=(255, 255, 255), font=font)
            draw.text((50, 250), f"Кат: {product['category']}", fill=(255, 255, 255), font=font)
        except:
            pass
        
        img.save(filepath, 'JPEG', quality=90)
        print(f"    [{i+1}/{len(all_products)}] {product['image']}")
    
    print(f"\n  [OK] Создано {len(all_products)} изображений-заглушек")

# ===================== ЗАПУСК =====================

if __name__ == "__main__":
    # Обновляем БД
    full_update()
    
    # Собираем галереи (доп. фото) из папок товаров
    try:
        from update_product_galleries import update_galleries
        update_galleries()
    except Exception as e:
        print(f"  [INFO] Галереи: {e}")
    
    # Заглушки не создаём — используются реальные фото из папок Devices/ и Sticks/
    # create_thumbnails()
    
    # Проверяем результат
    print("\n" + "="*70)
    print("ПРОВЕРКА РЕЗУЛЬТАТА")
    print("="*70)
    
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM product")
    total = cursor.fetchone()[0]
    print(f"  Всего товаров в базе: {total}")
    
    cursor.execute("""
        SELECT c.name, COUNT(*) 
        FROM product p
        JOIN category c ON p.category_id = c.id
        GROUP BY c.name
    """)
    stats = cursor.fetchall()
    for cat_name, count in stats:
        print(f"  • {cat_name}: {count} шт.")
    
    conn.close()
    
    print("\n" + "="*70)
    print("[OK] ГОТОВО!")
    print("")
    print("ВАЖНО: Если сервер уже запущен - ОБЯЗАТЕЛЬНО перезапустите его!")
    print("   Иначе изменения не отобразятся в интерфейсе.")
    print("")
    print("   py app.py   (или py shop.py — то же приложение)")
    print("="*70)