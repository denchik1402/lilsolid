# Полная инструкция: развёртка LIL STORE в продакшен с CI/CD

Пошаговое руководство для человека без опыта. Следуйте шагам по порядку.

**Ваш сервер:** IP `104.128.141.177`, пользователь `root`

---

## Содержание

1. [Регистрация на GitHub и создание репозитория](#часть-1-регистрация-на-github)
2. [Первый push кода в GitHub](#часть-2-первый-push-кода)
3. [Настройка сервера](#часть-3-настройка-сервера)
4. [Настройка CI/CD (автодеплой)](#часть-4-cicd-автодеплой)
5. [Домен и SSL (опционально)](#часть-5-домен-и-ssl)
6. [Продвижение в поиске (SEO)](#часть-6-продвижение-в-поиске)

---

## Часть 1: Регистрация на GitHub

### 1.1. Создайте аккаунт

1. Откройте браузер и перейдите на **https://github.com**
2. Нажмите **Sign up** (Регистрация)
3. Введите email, придумайте пароль, имя пользователя (например `yourname`)
4. Подтвердите email (проверьте почту, перейдите по ссылке)

### 1.2. Создайте репозиторий

1. Войдите в GitHub
2. Нажмите зелёную кнопку **New** (или **+** → **New repository**)
3. Заполните:
   - **Repository name:** `my_shop` (или `lilstore`)
   - **Description:** LIL STORE — магазин IQOS
   - **Private** или **Public** — на ваш выбор (для CI/CD подойдёт Private)
4. **НЕ** ставьте галочки «Add README», «Add .gitignore» — репозиторий должен быть пустым
5. Нажмите **Create repository**

---

## Часть 2: Первый push кода

### 2.1. Установите Git на ПК

**Windows:**
1. Скачайте Git: https://git-scm.com/download/win
2. Установите (всё по умолчанию)
3. Откройте **PowerShell** или **Командную строку**

**Проверка:** введите `git --version` — должна показаться версия.

### 2.2. Настройте Git (один раз)

```powershell
git config --global user.name "Ваше Имя"
git config --global user.email "ваш@email.com"
```

Подставьте свои данные (email должен совпадать с GitHub).

### 2.3. Инициализируйте репозиторий и загрузите код

Откройте PowerShell, перейдите в папку проекта:

```powershell
cd c:\Users\Dubko\Desktop\111\my_shop
```

Выполните по очереди:

```powershell
# 1. Инициализация Git (если ещё не сделано)
git init

# 2. Добавить все файлы (config.py и shop.db не попадут — они в .gitignore)
git add .

# 3. Первый коммит
git commit -m "Первый коммит: LIL STORE"

# 4. Переименовать ветку в main (если нужно)
git branch -M main

# 5. Подключить удалённый репозиторий (замените YOUR_USERNAME и YOUR_REPO на свои)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# 6. Загрузить код
git push -u origin main
```

**Пример:** если ваш логин `ivanov`, репозиторий `my_shop`:
```
git remote add origin https://github.com/ivanov/my_shop.git
```

При `git push` GitHub попросит авторизацию:
- **Рекомендуется:** Personal Access Token (токен)
- Создайте токен: GitHub → Settings → Developer settings → Personal access tokens → Generate new token
- Права: отметьте `repo`
- Скопируйте токен и вставьте вместо пароля при `git push`

---

## Часть 3: Настройка сервера

### 3.1. Подключитесь к серверу по SSH

**Windows (PowerShell):**
```powershell
ssh root@104.128.141.177
```

При первом подключении спросят «Are you sure you want to continue connecting?» — введите `yes`.

Введите пароль от root (если есть) или используйте SSH-ключ.

### 3.2. Установите необходимое ПО

Скопируйте и выполните на сервере (по одной команде или блоком):

```bash
apt update && apt upgrade -y
apt install -y git python3 python3-pip python3-venv nginx
```

### 3.3. Создайте пользователя для приложения

```bash
adduser lilstore
```

Задайте пароль (можно простой — доступ будет по ключу). Остальные поля можно оставить пустыми (Enter).

```bash
usermod -aG sudo lilstore
mkdir -p /home/lilstore/my_shop
chown lilstore:lilstore /home/lilstore/my_shop
```

### 3.4. Установите SSH-ключ для GitHub (для git clone)

**На вашем ПК** сгенерируйте ключ (если ещё нет):

```powershell
ssh-keygen -t ed25519 -C "your@email.com" -f "$env:USERPROFILE\.ssh\id_ed25519"
```

Нажмите Enter на вопросы (пароль можно оставить пустым).

Скопируйте **публичный** ключ:
```powershell
cat $env:USERPROFILE\.ssh\id_ed25519.pub
```

**Добавьте ключ на GitHub:**
1. GitHub → Settings → SSH and GPG keys → New SSH key
2. Title: `My PC` (любое)
3. Key: вставьте содержимое `id_ed25519.pub`
4. Add SSH key

**Добавьте ключ на сервер:**
1. На ПК скопируйте содержимое `id_ed25519.pub`
2. На сервере:
```bash
mkdir -p /home/lilstore/.ssh
nano /home/lilstore/.ssh/authorized_keys
```
3. Вставьте ключ, сохраните (Ctrl+O, Enter, Ctrl+X)
4. `chown -R lilstore:lilstore /home/lilstore/.ssh`
5. `chmod 700 /home/lilstore/.ssh`
6. `chmod 600 /home/lilstore/.ssh/authorized_keys`

### 3.5. Клонируйте репозиторий на сервер

**Важно:** 
- Если репозиторий **Public** — клонируйте без проблем
- Если **Private** — создайте Deploy Key: GitHub → репозиторий → Settings → Deploy keys → Add deploy key. Вставьте публичный ключ с сервера (см. ниже)

Переключитесь на пользователя lilstore:

```bash
su - lilstore
cd /home/lilstore/my_shop
```

Клонируйте (подставьте свой репозиторий):

```bash
# Если репозиторий публичный:
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git .

# Если Private — сначала создайте ключ на сервере:
# ssh-keygen -t ed25519 -C "server" -f ~/.ssh/deploy_key -N ""
# cat ~/.ssh/deploy_key.pub   — скопируйте и добавьте в Deploy keys на GitHub
# git clone git@github.com:YOUR_USERNAME/YOUR_REPO.git .
```

Точка в конце (` .`) — клонировать в текущую папку.

### 3.6. Создайте config.py на сервере

```bash
cp config.example.py config.py
nano config.py
```

Заполните (обязательно измените):

```python
TELEGRAM_BOT_TOKEN = 'ваш_токен_от_BotFather'
TELEGRAM_BOT_USERNAME = 'iluma_prime_bot'
TELEGRAM_ADMIN_IDS = '390144231'
ADMIN_SECRET = 'придумайте_надёжный_секрет'
SECRET_KEY = 'сгенерируйте_ниже'
TELEGRAM_DEFAULT_ADMIN = 'denchik1402'
ILUMA_XLSX_PATH = ''   # можно пусто на сервере
SITE_URL = 'http://104.128.141.177'   # или https://ваш-домен.ru
```

**Сгенерировать SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_hex(24))"
```
Скопируйте вывод в `SECRET_KEY = '...'`

Сохраните: Ctrl+O, Enter, Ctrl+X.

### 3.7. Установите зависимости и запустите

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 init_db.py
```

Проверьте запуск:
```bash
gunicorn --bind 127.0.0.1:8000 app:app
```

В другом окне или с ПК: откройте `http://104.128.141.177:8000` — должен открыться сайт. Остановите gunicorn (Ctrl+C).

### 3.8. Настройте Nginx

**Если у вас пока нет домена** (работаем по IP):

```bash
exit
sudo cp /home/lilstore/my_shop/deploy/nginx-ip-only.conf /etc/nginx/sites-available/lilstore
sudo ln -sf /etc/nginx/sites-available/lilstore /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

### 3.9. Настройте автозапуск (systemd)

```bash
sudo cp /home/lilstore/my_shop/deploy/lilstore.service /etc/systemd/system/
sudo cp /home/lilstore/my_shop/deploy/lilstore-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable lilstore lilstore-bot
sudo systemctl start lilstore lilstore-bot
```

Проверьте:
```bash
sudo systemctl status lilstore
sudo systemctl status lilstore-bot
```

### 3.10. Откройте порты (firewall)

```bash
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
sudo ufw --force enable
```

Откройте в браузере: **http://104.128.141.177** — должен открыться сайт.

---

## Часть 4: CI/CD (автодеплой при push)

При каждом `git push` в ветку `main` сайт будет автоматически обновляться на сервере.

### 4.1. Создайте SSH-ключ для деплоя

**На вашем ПК:**

```powershell
ssh-keygen -t ed25519 -C "deploy" -f "$env:USERPROFILE\.ssh\deploy_key" -N '""'
```

Пароль оставьте пустым (Enter два раза).

Скопируйте **приватный** ключ:
```powershell
Get-Content $env:USERPROFILE\.ssh\deploy_key
```
Скопируйте всё, включая `-----BEGIN...` и `-----END...`.

Скопируйте **публичный** ключ:
```powershell
Get-Content $env:USERPROFILE\.ssh\deploy_key.pub
```

### 4.2. Добавьте публичный ключ на сервер

На сервере (под root или lilstore):

```bash
mkdir -p /home/lilstore/.ssh
echo "ВСТАВЬТЕ_СЮДА_ПУБЛИЧНЫЙ_КЛЮЧ" >> /home/lilstore/.ssh/authorized_keys
chown -R lilstore:lilstore /home/lilstore/.ssh
chmod 700 /home/lilstore/.ssh
chmod 600 /home/lilstore/.ssh/authorized_keys
```

Замените `ВСТАВЬТЕ_СЮДА_ПУБЛИЧНЫЙ_КЛЮЧ` на содержимое `deploy_key.pub`.

### 4.3. Добавьте секреты в GitHub

1. Откройте репозиторий на GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Нажмите **New repository secret**
4. Добавьте три секрета:

| Name | Value |
|------|-------|
| `SSH_PRIVATE_KEY` | Весь приватный ключ (deploy_key) — включая BEGIN и END |
| `SSH_HOST` | `104.128.141.177` |
| `SSH_USER` | `root` (рекомендуется — деплой без sudo) или `lilstore` (нужен visudo) |

### 4.4. Разрешите sudo для перезапуска сервисов и смены прав

На сервере:

```bash
sudo visudo
```

В конец файла добавьте (замените `lilstore` если другой пользователь):

```
lilstore ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart lilstore lilstore-bot
lilstore ALL=(ALL) NOPASSWD: /usr/bin/chown
lilstore ALL=(ALL) NOPASSWD: /usr/bin/find
```

Сохраните (Ctrl+O, Enter, Ctrl+X).

### 4.5. Добавьте workflow в репозиторий

На вашем ПК в папке проекта создайте файл:

**Путь:** `c:\Users\Dubko\Desktop\111\my_shop\.github\workflows\deploy.yml`

Файл уже создан: `.github/workflows/deploy.yml`. Он автоматически:
- подключается к серверу по SSH
- выполняет `git pull`
- обновляет зависимости
- применяет миграции БД
- перезапускает сайт и бота

Закоммитьте и запушьте:

```powershell
cd c:\Users\Dubko\Desktop\111\my_shop
git add .github/
git commit -m "Добавлен CI/CD: автодеплой при push"
git push
```

### 4.6. Проверка

1. Откройте репозиторий на GitHub → вкладка **Actions**
2. Должен запуститься workflow «Deploy to Production»
3. Зелёная галочка — деплой прошёл успешно
4. При любом `git push` в `main` деплой будет запускаться автоматически

---

## Часть 5: Домен и SSL

Если у вас есть домен (например lilstore.ru):

### 5.1. Привяжите домен к серверу

В панели управления доменом добавьте A-записи:

| Тип | Имя | Значение | TTL |
|-----|-----|----------|-----|
| A | @ | 104.128.141.177 | 300 |
| A | www | 104.128.141.177 | 300 |

### 5.2. Установите Certbot и получите SSL

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot certonly --nginx -d ваш-домен.ru -d www.ваш-домен.ru --email your@email.com --agree-tos --non-interactive
```

### 5.3. Обновите Nginx

Используйте конфиг `deploy/nginx-lilstore.conf` (замените lilstore.ru на ваш домен) и перезагрузите nginx.

### 5.4. Обновите config.py

```python
SITE_URL = 'https://ваш-домен.ru'
```

---

## Часть 6: Продвижение в поиске (SEO)

### 6.1. Google Search Console

1. Перейдите на https://search.google.com/search-console
2. Войдите через Google-аккаунт
3. **Добавить ресурс** → **URL-префикс** → введите `http://104.128.141.177` (или ваш домен)
4. Подтверждение: выберите **HTML-тег** — скопируйте meta-тег
5. Добавьте его в `templates/base.html` в блок `<head>` (можно попросить разработчика)
6. После подтверждения: **Файлы Sitemap** → добавьте `http://ваш-сайт/sitemap.xml`

### 6.2. Яндекс.Вебмастер

1. Перейдите на https://webmaster.yandex.ru
2. Войдите через Яндекс
3. **Добавить сайт** → введите URL
4. Подтвердите права (HTML-тег или файл)
5. **Индексирование** → **Файлы Sitemap** → добавьте `https://ваш-сайт/sitemap.xml`

### 6.3. Sitemap на вашем сайте

Сайт уже отдаёт sitemap по адресу `/sitemap.xml`. Убедитесь, что он открывается.

---

## Шпаргалка: частые команды

**Перезапуск сервисов:**
```bash
sudo systemctl restart lilstore lilstore-bot
```

**Логи:**
```bash
sudo journalctl -u lilstore -f
sudo journalctl -u lilstore-bot -f
```

**Обновление вручную (если CI/CD не сработал):**
```bash
# 1. Права для Git (lilstore должен владеть проектом)
sudo chown -R lilstore:lilstore /home/lilstore/my_shop

# 2. Обновление кода
su - lilstore
cd /home/lilstore/my_shop
git fetch origin main
git reset --hard origin/main
source venv/bin/activate
pip install -r requirements.txt --quiet
python3 update_product_galleries.py
exit

# 3. Права для Nginx (www-data должен читать статику)
sudo chown -R www-data:www-data /home/lilstore/my_shop/static
sudo find /home/lilstore/my_shop/static -type d -exec chmod 755 {} \;
sudo find /home/lilstore/my_shop/static -type f -exec chmod 644 {} \;

# 4. Папки загрузок — приложение (lilstore) должно записывать
sudo mkdir -p /home/lilstore/my_shop/static/images/banners
sudo mkdir -p /home/lilstore/my_shop/static/images/products
sudo chown -R lilstore:lilstore /home/lilstore/my_shop/static/images/banners
sudo chown -R lilstore:lilstore /home/lilstore/my_shop/static/images/products

# 5. Перезапуск
sudo systemctl restart lilstore lilstore-bot
```

**Права доступа (памятка):**

| Операция | Владелец | Команда |
|----------|----------|---------|
| Git (pull, reset) | `lilstore` | `sudo chown -R lilstore:lilstore /home/lilstore/my_shop` |
| Работа сайта (Nginx читает статику) | `www-data` | `sudo chown -R www-data:www-data /home/lilstore/my_shop/static` |
| Загрузка баннеров и фото товаров | `lilstore` | `sudo chown -R lilstore:lilstore /home/lilstore/my_shop/static/images/banners /home/lilstore/my_shop/static/images/products` |
| После git pull | → `www-data` + `banners` → `lilstore` | См. шаги 3–4 в ручном деплое |

**Перенос баннеров на прод:**

1. Локально: `py export_banners.py` → создаётся `banners_export.json`
2. Скопировать `banners_export.json` на сервер (или он уже в репо после `git pull`)
3. На сервере: `cd /home/lilstore/my_shop && source venv/bin/activate && python3 import_banners.py`
4. `sudo systemctl restart lilstore`

Скрипт добавляет только новые баннеры (по имени файла). Существующие на проде не трогаются.

---

## Частые проблемы

| Проблема | Решение |
|---------|---------|
| Сайт не открывается | `sudo systemctl status lilstore` — проверьте, что сервис запущен |
| 502 Bad Gateway | Gunicorn упал. Смотрите логи: `sudo journalctl -u lilstore -n 50` |
| Бот не отвечает | Проверьте `TELEGRAM_BOT_TOKEN` в config.py, логи: `sudo journalctl -u lilstore-bot -n 50` |
| CI/CD падает | Проверьте секреты в GitHub, права sudo для lilstore |
| config.py перезаписывается | config.py в .gitignore — на сервере не делайте `git checkout config.py` |
| Permission denied при git reset | `git` требует владельца `lilstore`. Перед git: `sudo chown -R lilstore:lilstore /home/lilstore/my_shop`. После git: `sudo chown -R www-data:www-data /home/lilstore/my_shop/static` |
| 500 при входе в админку | Проверьте логи: `sudo journalctl -u lilstore -n 100 --no-pager`. Убедитесь, что в config.py заданы `ADMIN_SECRET`, `SECRET_KEY`, `SITE_URL` (https://...). Для HTTPS нужен `SESSION_COOKIE_SECURE`. |
| CI/CD: sudo password required | В GitHub Secrets задайте `SSH_USER=root`. Deploy-ключ добавьте в `/root/.ssh/authorized_keys`. Root SSH: `PermitRootLogin prohibit-password` в `/etc/ssh/sshd_config`, затем `sudo systemctl reload ssh` (или `sshd`). |
| 500 при сохранении баннеров/фото товаров | Папки `static/images/banners` и `static/images/products` — владелец `lilstore`: `sudo chown -R lilstore:lilstore /home/lilstore/my_shop/static/images/banners /home/lilstore/my_shop/static/images/products` |
