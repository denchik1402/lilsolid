#!/usr/bin/env bash
# Healthcheck для lilsolid.ru (без Telegram-бота)

set -u

SITE_URL="https://lilsolid.ru"
SITE_ENDPOINTS=("/" "/sitemap.xml" "/robots.txt" "/favicon.svg")
LOCAL_ENDPOINT="http://127.0.0.1:8000/health"
LOG_TAG="lilsolid-healthcheck"
APP_DIR="/home/lilstore/lilsolid"
SERVICE="lilsolid"

ok=1
reasons=()

check_url() {
  local url="$1"
  local code
  code="$(curl -L -sS -o /dev/null -w "%{http_code}" --max-time 10 "$url" || echo "000")"
  if [[ "$code" != "200" ]]; then
    ok=0
    reasons+=("$url:$code")
  fi
}

for path in "${SITE_ENDPOINTS[@]}"; do
  check_url "${SITE_URL}${path}"
done
check_url "${LOCAL_ENDPOINT}"

if [[ "$ok" -eq 1 ]]; then
  logger -t "$LOG_TAG" "OK"
  exit 0
fi

logger -t "$LOG_TAG" "FAIL: ${reasons[*]} -> restart ${SERVICE}"
systemctl restart "${SERVICE}" nginx || true
sleep 4

ok=1
reasons=()
for path in "${SITE_ENDPOINTS[@]}"; do
  check_url "${SITE_URL}${path}"
done
check_url "${LOCAL_ENDPOINT}"

if [[ "$ok" -eq 1 ]]; then
  logger -t "$LOG_TAG" "RECOVERED"
  exit 0
fi

logger -t "$LOG_TAG" "CRITICAL: ${reasons[*]}"
exit 1
