# Запуск магазина и бота

## Запуск сайта

```bash
cd c:\Users\Dubko\Desktop\111\my_shop
py app.py
```

Или: `py shop.py` — запускает то же приложение (app.py).

Сайт откроется на http://127.0.0.1:5000

**Админка:**
- http://127.0.0.1:5000/admin — форма ввода ключа
- http://127.0.0.1:5000/admin/products?key=Dik — управление товарами (ключ из config.py)

---

## 2. Запуск Telegram-бота

**В отдельном терминале** (сайт должен быть запущен):

```bash
cd c:\Users\Dubko\Desktop\111\my_shop
python TG/telegram_bot.py
```

Или на Windows: `TG\run_bot.bat`

Перед запуском:
1. При первом запуске `py app.py` создаётся `config.py` из `config.example.py`
2. Отредактируйте `config.py` — укажите `TELEGRAM_BOT_TOKEN` (получить у @BotFather) и `TELEGRAM_BOT_USERNAME` (например: `iluma_prime_bot`)
3. Напишите боту `/start` в личку — уведомления пойдут вам в личку (или в группу, если написали там)

**Куда подставить новый токен бота:**
- **config.py** — строка `TELEGRAM_BOT_TOKEN = 'ваш_токен_от_BotFather'`
- **config.production.py** (на сервере) — то же поле при деплое
- Или переменная окружения `TELEGRAM_BOT_TOKEN` (если не хотите хранить в файле)

---

## 3. Одновременный запуск (два окна)

**Терминал 1 — сайт:**
```
py app.py
```

**Терминал 2 — бот:**
```
py TG/telegram_bot.py
```

Оба процесса должны работать одновременно.

---

## 4. Тесты (pytest)

```bash
py -m pip install pytest
py -m pytest tests/
```
