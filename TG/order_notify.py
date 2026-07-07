# -*- coding: utf-8 -*-
"""Кнопки под уведомлениями о заказах: взять в работу → доставлен / отказ."""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

ORDER_STATUS_IN_WORK = 'in_work'
ORDER_STATUS_DELIVERED = 'delivered'
ORDER_STATUS_REFUSED = 'refused'


def _is_main_shop() -> bool:
    try:
        import config
        url = (getattr(config, 'SITE_URL', None) or '').lower()
        if 'iqos-store' in url or 'lilsolid' in url:
            return False
        return 'lilstore' in url
    except ImportError:
        return False


def _register_api_url() -> str:
    try:
        import config
        base = getattr(config, 'NOTIFY_SYNC_URL', None) or getattr(config, 'STAFF_SYNC_URL', None)
        if base:
            base = base.rstrip('/')
            for suffix in ('/staff-telegram-ids', '/notification-chat-id'):
                if base.endswith(suffix):
                    return base.replace(suffix, '/order-notify-messages')
            return f'{base}/order-notify-messages'
    except ImportError:
        pass
    return 'https://lilstore.ru/api/internal/order-notify-messages'


def order_take_button_markup(order_number: str, taken_by: str | None = None) -> dict:
    """Разметка inline-кнопок по текущему состоянию заказа в уведомлении."""
    taken = get_order_taken(order_number)
    if taken:
        return _markup_for_taken(order_number, taken)
    if taken_by:
        return {
            'inline_keyboard': [[
                {'text': f'В работе у {taken_by}', 'callback_data': 'noop'},
            ]]
        }
    return {
        'inline_keyboard': [[
            {'text': '✋ Взять в работу!', 'callback_data': f'order_work_{order_number}'},
        ]]
    }


def _markup_for_taken(order_number: str, taken: dict) -> dict:
    name = taken.get('display_name') or 'Сотрудник'
    status = taken.get('status') or ORDER_STATUS_IN_WORK
    if status == ORDER_STATUS_DELIVERED:
        return {
            'inline_keyboard': [[
                {'text': f'✅ Доставил {name}', 'callback_data': 'noop'},
            ]]
        }
    if status == ORDER_STATUS_REFUSED:
        return {
            'inline_keyboard': [[
                {'text': f'❌ Клиент отказался ({name})', 'callback_data': 'noop'},
            ]]
        }
    return {
        'inline_keyboard': [[
            {'text': '✔️Доставлен', 'callback_data': f'order_deliver_{order_number}'},
            {'text': '❌Отказ', 'callback_data': f'order_refuse_{order_number}'},
        ]]
    }


def register_order_notify_messages(order_number: str, placements: list[tuple[int | str, int]]) -> bool:
    """Сохранить chat_id + message_id для последующего обновления кнопки."""
    if not order_number or not placements:
        return False
    payload = [[int(c), int(m)] for c, m in placements]
    if _is_main_shop():
        return _register_local(order_number, payload)
    return _register_remote(order_number, payload)


def _register_local(order_number: str, placements: list[list[int]]) -> bool:
    try:
        from app import app
        from extensions import db
        from models import BotSetting
        key = f'order_notify_msgs_{order_number}'
        with app.app_context():
            row = BotSetting.query.filter_by(key=key).first()
            val = json.dumps(placements, ensure_ascii=False)
            if row:
                row.value = val
            else:
                db.session.add(BotSetting(key=key, value=val))
            db.session.commit()
        return True
    except Exception:
        return False


def _register_remote(order_number: str, placements: list[list[int]]) -> bool:
    try:
        from notify_sync import derive_sync_secret
        from staff_notify import get_bot_token
    except ImportError:
        return False
    token = get_bot_token() or ''
    if not token:
        return False
    body = json.dumps({'order_number': order_number, 'placements': placements}).encode()
    req = urllib.request.Request(
        _register_api_url(),
        data=body,
        method='POST',
        headers={
            'Content-Type': 'application/json',
            'X-Notify-Sync': derive_sync_secret(token),
            'User-Agent': 'LilStore-OrderNotify/1.0',
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return 200 <= resp.status < 300
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return False


def get_order_notify_messages(order_number: str) -> list[tuple[int, int]]:
    try:
        from app import app
        from models import BotSetting
        key = f'order_notify_msgs_{order_number}'
        with app.app_context():
            row = BotSetting.query.filter_by(key=key).first()
            if not row or not row.value:
                return []
            data = json.loads(row.value)
            return [(int(c), int(m)) for c, m in data]
    except Exception:
        return []


def get_order_taken(order_number: str) -> dict | None:
    try:
        from app import app
        from models import BotSetting
        key = f'order_taken_{order_number}'
        with app.app_context():
            row = BotSetting.query.filter_by(key=key).first()
            if not row or not row.value:
                return None
            data = json.loads(row.value)
            if 'status' not in data:
                data['status'] = ORDER_STATUS_IN_WORK
            return data
    except Exception:
        return None


def set_order_taken(order_number: str, telegram_id: int, display_name: str) -> None:
    _save_order_taken(order_number, {
        'telegram_id': int(telegram_id),
        'display_name': display_name,
        'status': ORDER_STATUS_IN_WORK,
    })


def set_order_outcome(order_number: str, outcome: str, telegram_id: int, display_name: str) -> None:
    if outcome not in (ORDER_STATUS_DELIVERED, ORDER_STATUS_REFUSED):
        raise ValueError(f'invalid outcome: {outcome}')
    _save_order_taken(order_number, {
        'telegram_id': int(telegram_id),
        'display_name': display_name,
        'status': outcome,
    })


def _save_order_taken(order_number: str, payload: dict) -> None:
    from app import app
    from extensions import db
    from models import BotSetting
    key = f'order_taken_{order_number}'
    val = json.dumps(payload, ensure_ascii=False)
    with app.app_context():
        row = BotSetting.query.filter_by(key=key).first()
        if row:
            row.value = val
        else:
            db.session.add(BotSetting(key=key, value=val))
        db.session.commit()
