# -*- coding: utf-8 -*-
"""Внутренний API: заказы за календарный день (МСК) для health-check хаба."""
from __future__ import annotations

from datetime import datetime, timedelta
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

MSK = ZoneInfo('Europe/Moscow')


def site_label_from_config() -> str:
    import os
    url = os.environ.get('SITE_URL', '')
    if not url:
        try:
            import config
            url = getattr(config, 'SITE_URL', '') or ''
        except ImportError:
            url = ''
    parsed = urlparse(url if '://' in (url or '') else f'https://{url or ""}')
    host = (parsed.netloc or '').lower()
    if host.startswith('www.'):
        host = host[4:]
    return host or 'unknown'


def msk_day_bounds(day_offset: int = 1):
    """Границы календарного дня МСК в naive UTC (как Order.created_at)."""
    now_msk = datetime.now(MSK)
    day_start_msk = (now_msk - timedelta(days=day_offset)).replace(
        hour=0, minute=0, second=0, microsecond=0,
    )
    day_end_msk = day_start_msk + timedelta(days=1)
    start_utc = day_start_msk.astimezone(ZoneInfo('UTC')).replace(tzinfo=None)
    end_utc = day_end_msk.astimezone(ZoneInfo('UTC')).replace(tzinfo=None)
    return day_start_msk.strftime('%d.%m.%Y'), start_utc, end_utc


def list_orders_for_previous_msk_day():
    """Список {number, created_at} за вчера (МСК)."""
    from models import Order

    day_label, start_utc, end_utc = msk_day_bounds(1)
    orders = (
        Order.query
        .filter(Order.created_at >= start_utc, Order.created_at < end_utc)
        .order_by(Order.created_at.asc())
        .all()
    )
    items = []
    for o in orders:
        items.append({
            'number': str(o.order_number or o.id),
            'created_at': o.created_at.isoformat(sep=' ', timespec='seconds') if o.created_at else '',
        })
    return {
        'site': site_label_from_config(),
        'day_label': day_label,
        'orders': items,
        'total': len(items),
    }


def register_yesterday_orders_api(app):
    """Регистрирует GET /api/internal/yesterday-orders (X-Notify-Sync)."""
    from flask import jsonify, request

    @app.route('/api/internal/yesterday-orders')
    def internal_yesterday_orders():
        from notify_sync import derive_sync_secret
        import os

        token = os.environ.get('TELEGRAM_BOT_TOKEN')
        try:
            import config
            token = token or getattr(config, 'TELEGRAM_BOT_TOKEN', None)
        except ImportError:
            pass
        if not token:
            return jsonify({'error': 'bot not configured'}), 503
        if request.headers.get('X-Notify-Sync') != derive_sync_secret(token):
            return jsonify({'error': 'forbidden'}), 403
        try:
            payload = list_orders_for_previous_msk_day()
        except Exception as e:
            return jsonify({'error': str(e)[:120]}), 500
        return jsonify(payload)
