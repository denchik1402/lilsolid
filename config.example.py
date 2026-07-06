# -*- coding: utf-8 -*-
# Киберпанк-версия. Скопируйте в config.py и заполните.

# Тот же токен, что у my_shop (уведомления о заказах). Polling — только на my_shop.
TELEGRAM_BOT_TOKEN = ''
TELEGRAM_BOT_USERNAME = 'iluma_prime_bot'
TELEGRAM_RUN_POLLING = False
# ID чата для уведомлений — тот же, что в my_shop config.py (группа менеджеров)
TELEGRAM_CHAT_ID = ''
TELEGRAM_ADMIN_IDS = ''
TELEGRAM_DEFAULT_ADMIN = 'denchik1402'

# Секретный ключ администратора (полный доступ, в т.ч. удаление заказов): /admin
ADMIN_SECRET = ''

# Отдельный ключ роли «Босс» — тот же URL /admin, все права кроме удаления заказов
BOSS_SECRET = ''

SECRET_KEY = ''

# URL киберпанк-сайта
SITE_URL = 'https://lilsolid.ru'

# Контакты на сайте (телефон, адрес для Яндекса/Google и страницы «Контакты»)
SITE_PHONE = '+7 (993) 596-82-25'
SITE_ADDRESS = 'Москва, Ленинградское шоссе, 16А'
SITE_CITY = 'Москва'

# Бренд на сайте (отображается в title, footer, SEO)
SITE_BRAND_NAME = 'LIL SOLID'

# Мессенджеры (необязательно; если не используете — не задавайте)
# SITE_WHATSAPP_URL = ''
# SITE_MAX_URL = ''

# Доставка на карточке товара и в FAQ
DELIVERY_MOSCOW_PRICE = 0
DELIVERY_MOSCOW_NOTE = 'в день заказа'
DELIVERY_RF_NOTE = 'стоимость доставки сообщит менеджер при подтверждении заказа'
DELIVERY_RF_DAYS = 'от 1–2 дней'

# Яндекс.Метрика — ОТДЕЛЬНЫЙ счётчик только для https://lilsolid.ru
# Создайте в https://metrika.yandex.ru → «Добавить счётчик» → домен lilsolid.ru
YANDEX_METRIKA_ID = ''

ILUMA_XLSX_PATH = ''
