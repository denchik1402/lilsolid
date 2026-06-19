# -*- coding: utf-8 -*-
"""Рассылка уведомлений staff-ролям (admin, boss, courier) в личку бота."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

STAFF_ROLES = ('admin', 'boss', 'courier')


def get_bot_token():
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token and os.path.exists('config.py'):
        try:
            import config
            token = getattr(config, 'TELEGRAM_BOT_TOKEN', None)
        except ImportError:
            token = None
    return token


def get_staff_telegram_ids(roles=STAFF_ROLES) -> list[int]:
    """Telegram ID всех пользователей с ролями staff из локальной БД."""
    try:
        from app import app
        from models import TelegramUser
        with app.app_context():
            users = TelegramUser.query.filter(TelegramUser.role.in_(tuple(roles))).all()
            ids = []
            seen = set()
            for u in users:
                tid = int(u.telegram_id)
                if tid and tid not in seen:
                    seen.add(tid)
                    ids.append(tid)
            return ids
    except Exception:
        return []


def _staff_sync_url() -> str:
    try:
        import config
        url = getattr(config, 'STAFF_SYNC_URL', None) or getattr(config, 'NOTIFY_SYNC_URL', None)
        if url:
            base = url.rstrip('/')
            if base.endswith('/notification-chat-id'):
                return base.replace('/notification-chat-id', '/staff-telegram-ids')
            return f'{base}/staff-telegram-ids'
    except ImportError:
        pass
    return 'https://lilstore.ru/api/internal/staff-telegram-ids'


def fetch_remote_staff_telegram_ids(bot_token: str, roles=STAFF_ROLES) -> list[int]:
    """Staff IDs с основного сервера (iqos-store / lilsolid)."""
    if not bot_token:
        return []
    try:
        from notify_sync import derive_sync_secret
    except ImportError:
        import hashlib
        def derive_sync_secret(t):
            return hashlib.sha256(f'notify-sync:{t}'.encode()).hexdigest()
    req = urllib.request.Request(
        _staff_sync_url(),
        headers={
            'X-Notify-Sync': derive_sync_secret(bot_token),
            'User-Agent': 'LilStore-StaffSync/1.0',
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode())
            ids = []
            for raw in data.get('telegram_ids') or []:
                try:
                    ids.append(int(raw))
                except (TypeError, ValueError):
                    pass
            return ids
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError, OSError):
        return []


def get_group_chat_id():
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    try:
        import config
        chat_id = chat_id or getattr(config, 'TELEGRAM_CHAT_ID', None)
    except ImportError:
        pass
    try:
        from app import app
        from models import BotSetting
        with app.app_context():
            s = BotSetting.query.filter_by(key='notification_chat_id').first()
            if s and s.value:
                chat_id = s.value
    except Exception:
        pass
    return chat_id


def collect_notification_chat_ids(roles=STAFF_ROLES, include_group=True) -> list[int | str]:
    """Уникальные chat_id: staff в личку + опционально группа."""
    targets: list[int | str] = []
    seen = set()

    staff_ids = get_staff_telegram_ids(roles)
    if not staff_ids:
        token = get_bot_token() or ''
        staff_ids = fetch_remote_staff_telegram_ids(token, roles)

    for tid in staff_ids:
        key = str(tid)
        if key not in seen:
            seen.add(key)
            targets.append(tid)

    if include_group:
        gid = get_group_chat_id()
        if gid and str(gid) not in seen:
            seen.add(str(gid))
            targets.append(gid)

    return targets


def send_telegram_messages(text: str, *, reply_markup: dict | None = None,
                           roles=STAFF_ROLES, include_group=True) -> tuple[bool, str | None]:
    """
    Отправляет сообщение всем staff и в групповой чат (если есть).
    Возвращает (успех хотя бы одной отправки, описание ошибки).
    """
    token = get_bot_token()
    if not token:
        return False, 'Telegram не настроен (TELEGRAM_BOT_TOKEN)'

    chat_ids = collect_notification_chat_ids(roles=roles, include_group=include_group)
    if not chat_ids:
        return False, 'Нет получателей: назначьте роли admin/boss/courier и напишите боту /start'

    url = f'https://api.telegram.org/bot{token}/sendMessage'
    errors = []
    sent = 0
    for chat_id in chat_ids:
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True,
        }
        if reply_markup is not None:
            payload['reply_markup'] = json.dumps(reply_markup)
        data = urllib.parse.urlencode(payload).encode()
        try:
            req = urllib.request.Request(url, data=data, method='POST')
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
                if result.get('ok'):
                    sent += 1
                else:
                    errors.append(str(result.get('description', chat_id)))
        except Exception as exc:
            errors.append(str(exc))

    if sent:
        return True, None
    return False, '; '.join(errors[:3]) if errors else 'Не удалось отправить'
