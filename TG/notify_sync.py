# -*- coding: utf-8 -*-
"""Синхронизация chat_id уведомлений с my_shop (lilstore.ru)."""
from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request


def derive_sync_secret(bot_token: str) -> str:
    if not bot_token:
        return ''
    return hashlib.sha256(f'notify-sync:{bot_token}'.encode()).hexdigest()


def _notify_sync_url() -> str:
    try:
        import config
        url = getattr(config, 'NOTIFY_SYNC_URL', None)
        if url:
            return url.rstrip('/')
    except ImportError:
        pass
    return 'https://lilstore.ru/api/internal/notification-chat-id'


def fetch_remote_notification_chat_id(bot_token: str) -> str | None:
    if not bot_token:
        return None
    req = urllib.request.Request(
        _notify_sync_url(),
        headers={
            'X-Notify-Sync': derive_sync_secret(bot_token),
            'User-Agent': 'LilStore-NotifySync/1.0',
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode())
            chat_id = data.get('chat_id')
            return str(chat_id) if chat_id else None
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError, OSError):
        return None


def sync_notification_chat_to_local_db() -> bool:
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token and os.path.exists('config.py'):
        try:
            import config
            token = getattr(config, 'TELEGRAM_BOT_TOKEN', None)
        except ImportError:
            token = None
    chat_id = fetch_remote_notification_chat_id(token or '')
    if not chat_id:
        return False
    from app import app
    from extensions import db
    from models import BotSetting
    with app.app_context():
        row = BotSetting.query.filter_by(key='notification_chat_id').first()
        if row:
            row.value = chat_id
        else:
            db.session.add(BotSetting(key='notification_chat_id', value=chat_id))
        db.session.commit()
    return True
