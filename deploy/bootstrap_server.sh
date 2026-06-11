#!/usr/bin/env bash
# Первичная настройка сервера FirstByte для lilsolid.ru
# Запуск на сервере под root:
#   export GITHUB_REPO="https://github.com/ВАШ_ЛОГИН/lilsolid.git"
#   bash bootstrap_server.sh

set -euo pipefail

APP_USER="lilstore"
APP_DIR="/home/${APP_USER}/lilsolid"
DOMAIN="lilsolid.ru"
SERVICE="lilsolid"
GITHUB_REPO="${GITHUB_REPO:-}"

echo "=== Bootstrap: ${DOMAIN} ==="

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Запустите от root: sudo bash bootstrap_server.sh"
  exit 1
fi

if ! id "$APP_USER" &>/dev/null; then
  useradd -m -s /bin/bash "$APP_USER"
  echo "Создан пользователь $APP_USER"
fi

apt-get update
apt-get install -y git python3 python3-pip python3-venv nginx certbot python3-certbot-nginx curl

mkdir -p "$APP_DIR"
chown "$APP_USER:$APP_USER" "$APP_DIR"

if [[ -n "$GITHUB_REPO" ]] && [[ ! -d "$APP_DIR/.git" ]]; then
  sudo -u "$APP_USER" git clone "$GITHUB_REPO" "$APP_DIR"
elif [[ ! -f "$APP_DIR/app.py" ]]; then
  echo ""
  echo "Клонируйте репозиторий вручную:"
  echo "  sudo -u $APP_USER git clone $GITHUB_REPO $APP_DIR"
fi

if [[ -f "$APP_DIR/requirements.txt" ]]; then
  sudo -u "$APP_USER" bash -c "cd $APP_DIR && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
fi

if [[ ! -f "$APP_DIR/config.py" ]] && [[ -f "$APP_DIR/config.example.py" ]]; then
  cp "$APP_DIR/config.example.py" "$APP_DIR/config.py"
  chown "$APP_USER:$APP_USER" "$APP_DIR/config.py"
  echo "Создан config.py — отредактируйте: nano $APP_DIR/config.py"
fi

cp "$APP_DIR/deploy/${SERVICE}.service" "/etc/systemd/system/${SERVICE}.service"
cp "$APP_DIR/deploy/nginx-lilsolid-http.conf" /etc/nginx/sites-available/lilsolid
ln -sf /etc/nginx/sites-available/lilsolid /etc/nginx/sites-enabled/lilsolid
rm -f /etc/nginx/sites-enabled/default

systemctl daemon-reload
systemctl enable "$SERVICE" nginx

if [[ -f "$APP_DIR/app.py" ]]; then
  sudo -u "$APP_USER" bash -c "cd $APP_DIR && source venv/bin/activate && python3 repair_schema.py" || true
  sudo -u "$APP_USER" bash -c "cd $APP_DIR && source venv/bin/activate && python3 full_update.py" 2>/dev/null || true
fi

systemctl start "$SERVICE" || true
nginx -t && systemctl reload nginx

echo ""
echo "=== Дальше ==="
echo "1. DNS Selectel: A @ и A www -> IP этого сервера"
echo "2. config.py: SITE_URL=https://${DOMAIN}, TELEGRAM_BOT_TOKEN, ADMIN_SECRET, TELEGRAM_RUN_POLLING=False"
echo "3. SSL: certbot --nginx -d ${DOMAIN} -d www.${DOMAIN}"
echo "4. После SSL: cp $APP_DIR/deploy/nginx-lilsolid.conf /etc/nginx/sites-available/lilsolid && nginx -t && systemctl reload nginx"
echo "5. GitHub Secrets: SSH_HOST=<IP>, SSH_USER=root, SSH_PRIVATE_KEY=<deploy key>"
echo "6. git push в main — CI/CD задеплоит автоматически"
