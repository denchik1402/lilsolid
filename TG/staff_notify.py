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


def get_config_admin_ids() -> list[int]:
    """TELEGRAM_ADMIN_IDS из config/env — всегда в получателях заказов."""
    raw = os.environ.get('TELEGRAM_ADMIN_IDS', '')
    try:
        import config
        raw = raw or getattr(config, 'TELEGRAM_ADMIN_IDS', '') or ''
    except ImportError:
        pass
    ids: list[int] = []
    for x in str(raw).replace(',', ' ').split():
        try:
            ids.append(int(x.strip()))
        except ValueError:
            pass
    return ids


def get_staff_telegram_ids(roles=STAFF_ROLES) -> list[int]:
    """Telegram ID staff из локальной БД + TELEGRAM_ADMIN_IDS (если роль admin запрошена)."""
    ids: list[int] = []
    seen: set[int] = set()
    try:
        from app import app
        from models import TelegramUser
        with app.app_context():
            users = TelegramUser.query.filter(TelegramUser.role.in_(tuple(roles))).all()
            for u in users:
                tid = int(u.telegram_id)
                if tid and tid not in seen:
                    seen.add(tid)
                    ids.append(tid)
    except Exception:
        pass
    if 'admin' in roles or 'boss' in roles:
        for tid in get_config_admin_ids():
            if tid not in seen:
                seen.add(tid)
                ids.append(tid)
    return ids


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
    """Staff IDs с основного сервера (iqos-store / lilsolid / iluma)."""
    if not bot_token:
        return []
    try:
        from notify_sync import derive_sync_secret
    except ImportError:
        import hashlib
        def derive_sync_secret(t):
            return hashlib.sha256(f'notify-sync:{t}'.encode()).hexdigest()
    qs = urllib.parse.urlencode({'roles': ','.join(roles)})
    req = urllib.request.Request(
        f'{_staff_sync_url()}?{qs}',
        headers={
            'X-Notify-Sync': derive_sync_secret(bot_token),
            'User-Agent': 'LilStore-StaffSync/1.0',
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
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


def collect_notification_chat_ids(roles=STAFF_ROLES, include_group=True,
                                  include_remote=True) -> list[int | str]:
    """Уникальные chat_id: staff в личку + опционально группа.

    Локальная БД + TELEGRAM_ADMIN_IDS + (опционально) staff с хаба.
    """
    targets: list[int | str] = []
    seen = set()

    staff_ids = list(get_staff_telegram_ids(roles))
    if include_remote:
        token = get_bot_token() or ''
        for tid in fetch_remote_staff_telegram_ids(token, roles):
            if tid not in staff_ids:
                staff_ids.append(tid)

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
                           roles=STAFF_ROLES, include_group=True,
                           include_remote=True,
                           exclude_telegram_ids=None,
                           return_placements: bool = False):
    """
    Отправляет сообщение всем staff и в групповой чат (если есть).
    Возвращает (успех, ошибка) или (успех, ошибка, placements) если return_placements=True.
    """
    token = get_bot_token()
    if not token:
        if return_placements:
            return False, 'Telegram не настроен (TELEGRAM_BOT_TOKEN)', []
        return False, 'Telegram не настроен (TELEGRAM_BOT_TOKEN)'

    exclude = {str(x) for x in (exclude_telegram_ids or [])}
    chat_ids = collect_notification_chat_ids(
        roles=roles, include_group=include_group, include_remote=include_remote,
    )
    chat_ids = [cid for cid in chat_ids if str(cid) not in exclude]
    if not chat_ids:
        if return_placements:
            return False, 'Нет получателей: назначьте роли admin/boss/courier и напишите боту /start', []
        return False, 'Нет получателей: назначьте роли admin/boss/courier и напишите боту /start'

    from telegram_api import telegram_method_url, telegram_request_headers

    url = telegram_method_url(token, 'sendMessage')
    errors = []
    sent = 0
    placements: list[tuple[int | str, int]] = []

    def _post(payload: dict) -> dict:
        data = urllib.parse.urlencode(payload).encode()
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        for k, v in telegram_request_headers().items():
            req.add_header(k, v)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())

    for chat_id in chat_ids:
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True,
        }
        if reply_markup is not None:
            payload['reply_markup'] = json.dumps(reply_markup)
        try:
            result = _post(payload)
            if result.get('ok'):
                sent += 1
                if return_placements:
                    msg_id = result.get('result', {}).get('message_id')
                    if msg_id is not None:
                        placements.append((chat_id, int(msg_id)))
                continue
            desc = str(result.get('description', chat_id))
            # Часто ломает parse_mode HTML из‑за < в названии товара — повтор без HTML
            if 'parse' in desc.lower() or 'entities' in desc.lower():
                payload_plain = {
                    'chat_id': chat_id,
                    'text': text,
                    'disable_web_page_preview': True,
                }
                if reply_markup is not None:
                    payload_plain['reply_markup'] = json.dumps(reply_markup)
                result2 = _post(payload_plain)
                if result2.get('ok'):
                    sent += 1
                    if return_placements:
                        msg_id = result2.get('result', {}).get('message_id')
                        if msg_id is not None:
                            placements.append((chat_id, int(msg_id)))
                    continue
                errors.append(str(result2.get('description', chat_id)))
            else:
                errors.append(desc)
        except Exception as exc:
            errors.append(str(exc))

    err = None if sent else ('; '.join(errors[:3]) if errors else 'Не удалось отправить')
    if return_placements:
        return bool(sent), err, placements
    return bool(sent), err
