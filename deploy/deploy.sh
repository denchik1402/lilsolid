#!/bin/bash
# Скрипт деплоя LIL STORE на Ubuntu 24.04
# Запускать от root: sudo bash deploy/deploy.sh

set -e

APP_USER="lilstore"
APP_DIR="/home/${APP_USER}/my_shop"
DOMAIN="lilstore.ru"

echo "=== LIL STORE: Деплой на Ubuntu 24.04 ==="

# 1. Создать пользователя
if ! id "$APP_USER" &>/dev/null; then
    useradd -m -s /bin/bash "$APP_USER"
    echo "Создан пользователь $APP_USER"
else
    echo "Пользователь $APP_USER уже существует"
fi

# 2. Установить зависимости системы
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx

# 3. Создать директорию приложения
mkdir -p "$APP_DIR"
chown "$APP_USER:$APP_USER" "$APP_DIR"

echo ""
echo "=== ВАЖНО: Дальнейшие шаги выполните вручную ==="
echo ""
echo "1. Скопируйте проект на сервер (с вашего ПК):"
echo "   scp -r my_shop/* ${APP_USER}@ВАШ_СЕРВЕР:${APP_DIR}/"
echo ""
echo "2. На сервере создайте config.py в ${APP_DIR}/"
echo "   Укажите SITE_URL='https://${DOMAIN}'"
echo ""
echo "3. Следуйте инструкции в DEPLOY.md"
echo ""
