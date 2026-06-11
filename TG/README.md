# Telegram-бот LIL STORE

Файлы Telegram-бота вынесены в папку `TG` для возможности раздельного деплоя: бот на одном устройстве, сайт на другом.

## Содержимое

- `telegram_bot.py` — основной файл бота
- `telegram_notify.py` — отправка уведомлений о заказах и отзывах (используется и сайтом)
- `bot_utils.py` — утилиты (прибыль, маршруты Яндекс.Карт)
- `run_bot.bat` — запуск на Windows
- `TELEGRAM_SETUP.md` — настройка
- `deploy/lilstore-bot.service` — systemd-юнит для Linux

## Запуск

**Из корня проекта (my_shop):**

```bash
python TG/telegram_bot.py
```

Windows: `TG\run_bot.bat`

## Раздельный деплой

Для запуска бота на отдельном устройстве скопируйте папку `TG` и файлы: `app.py`, `models.py`, `extensions.py`, `config.py`, `shop.db`, `static/images/products`. Подробнее — в `TELEGRAM_SETUP.md`.
