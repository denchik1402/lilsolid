# Деплой lilsolid.ru

> **Полная пошаговая инструкция:** [`../DEPLOY_TWO_SITES.md`](../DEPLOY_TWO_SITES.md)  
> **Первичная настройка сервера:** `deploy/bootstrap_server.sh`

## Параметры

| | |
|--|--|
| Домен | **lilsolid.ru** |
| IP сервера FirstByte | **104.128.137.162** |
| Папка на сервере | `/home/lilstore/lilsolid` |
| Служба systemd | **`lilsolid`** (`systemctl restart lilsolid`) |
| Nginx | `/etc/nginx/sites-available/lilsolid` |
| GitHub | https://github.com/denchik1402/lilsolid |
| Telegram polling | **выключен** (`TELEGRAM_RUN_POLLING = False`) |

## Быстрый старт на сервере

```bash
ssh root@104.128.137.162

useradd -m -s /bin/bash lilstore 2>/dev/null || true
apt-get update && apt-get install -y git python3 python3-venv nginx certbot python3-certbot-nginx curl

sudo -u lilstore git clone https://github.com/denchik1402/lilsolid.git /home/lilstore/lilsolid
cd /home/lilstore/lilsolid
cp config.example.py config.py
nano config.py   # SITE_URL=https://lilsolid.ru, TELEGRAM_RUN_POLLING=False

bash deploy/bootstrap_server.sh

certbot --nginx -d lilsolid.ru -d www.lilsolid.ru
cp deploy/nginx-lilsolid.conf /etc/nginx/sites-available/lilsolid
nginx -t && systemctl reload nginx
systemctl status lilsolid
```

## Файлы deploy/

| Файл | Назначение |
|------|------------|
| `lilsolid.service` | systemd — gunicorn на порту 8000 |
| `nginx-lilsolid-http.conf` | HTTP до SSL |
| `nginx-lilsolid.conf` | HTTPS после certbot |
| `healthcheck.sh` | проверка сайта (опционально, cron) |
| `bootstrap_server.sh` | первичная установка |

## Telegram

**Не запускайте** `lilstore-bot.service` на этом сервере.

- Интерактивный бот — только на **my_shop** (`lilstore-bot.service`).
- На lilsolid достаточно `TELEGRAM_BOT_TOKEN` в `config.py` — уведомления о заказах через HTTP API.

## CI/CD

`.github/workflows/deploy.yml` — при push в `main` обновляет `/home/lilstore/lilsolid` и перезапускает **`lilsolid`**.

GitHub Secrets: `SSH_HOST=104.128.137.162`, `SSH_USER=root`, `SSH_PRIVATE_KEY`.

---

*Файл `DEPLOY_CYBER.md` оставлен для совместимости — актуальное имя проекта: **lilsolid**.*
