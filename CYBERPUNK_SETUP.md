# lilsolid.ru — локальная разработка

> Деплой на сервер: **[DEPLOY_LILSOLID.md](DEPLOY_LILSOLID.md)** и **[../DEPLOY_TWO_SITES.md](../DEPLOY_TWO_SITES.md)**

Киберпанк UI. На проде: домен **lilsolid.ru**, служба **`lilsolid`**, папка `/home/lilstore/lilsolid`.

## 1. Конфигурация

```bash
cp config.example.py config.py
# Отредактируйте config.py: SITE_URL, ADMIN_SECRET, SECRET_KEY
# TELEGRAM_BOT_TOKEN — тот же, что и у основного сайта
```

## 2. Инициализация БД и наполнение

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Linux: source venv/bin/activate

pip install -r requirements.txt
python init_db.py          # создание схемы БД (Alembic/models)
python full_update.py      # наполнение товарами (перезаписывает product, category)
python update_product_galleries.py
```

## 3. Импорт баннеров (опционально)

```bash
python import_banners.py   # если есть banners_export.json
```

## 4. Запуск локально

```bash
# Порт 5001, чтобы не конфликтовать с основным сайтом
python -c "from app import app; app.run(port=5001)"
```

## 5. Деплой

- Служба systemd: **`lilsolid`**
- Nginx: **`nginx-lilsolid.conf`** → домен **lilsolid.ru**
- CI/CD: **`lilsolid/.github/workflows/deploy.yml`**

См. `deploy/` и **DEPLOY_LILSOLID.md**.
