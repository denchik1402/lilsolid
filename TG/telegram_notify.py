# -*- coding: utf-8 -*-
"""
Отправка уведомлений о заказах в Telegram.
Чат для уведомлений: куда добавлен бот (сохраняется автоматически или через /set_notify).
TELEGRAM_CHAT_ID в config — запасной вариант.
"""

import os
import urllib.request
import urllib.parse
import json
import logging
import threading

from staff_notify import send_telegram_messages
from order_notify import order_take_button_markup, register_order_notify_messages

_logger = logging.getLogger(__name__)


def get_config():
    """Token и chat_id для уведомлений (config.py или BotSetting на этом сайте)."""
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if os.path.exists('config.py'):
        try:
            import config
            token = token or getattr(config, 'TELEGRAM_BOT_TOKEN', None)
            chat_id = chat_id or getattr(config, 'TELEGRAM_CHAT_ID', None) or None
        except ImportError:
            pass
    try:
        from flask import has_request_context
        from models import BotSetting
        if has_request_context():
            s = BotSetting.query.filter_by(key='notification_chat_id').first()
            if s and s.value:
                chat_id = s.value
        else:
            from app import app
            with app.app_context():
                s = BotSetting.query.filter_by(key='notification_chat_id').first()
                if s and s.value:
                    chat_id = s.value
    except Exception:
        pass
    if not chat_id and token:
        try:
            from notify_sync import sync_notification_chat_to_local_db
            if sync_notification_chat_to_local_db():
                from flask import has_request_context
                from models import BotSetting
                if has_request_context():
                    s = BotSetting.query.filter_by(key='notification_chat_id').first()
                    if s and s.value:
                        chat_id = s.value
                else:
                    from app import app
                    with app.app_context():
                        s = BotSetting.query.filter_by(key='notification_chat_id').first()
                        if s and s.value:
                            chat_id = s.value
        except Exception:
            pass
    return token, chat_id


def _site_order_label():
    try:
        import config
        url = (getattr(config, 'SITE_URL', None) or '').lower()
    except ImportError:
        url = ''
    if 'iqos-store' in url:
        return 'АЙКОС СТОР · iqos-store.ru'
    if 'lilsolid' in url:
        return 'LIL SOLID · lilsolid.ru'
    if 'lilstore' in url:
        return 'LIL STORE · lilstore.ru'
    return url.replace('https://', '').replace('http://', '') or 'Сайт'


def format_order_message(order):
    """Форматирует заказ для красивого отображения в Telegram"""
    lines = [
        f"🛒 <b>НОВЫЙ ЗАКАЗ</b> — {_site_order_label()}",
        "",
        f"📋 Номер: <code>{order.order_number}</code>",
        f"👤 Клиент: {order.customer_name}",
        f"📞 Телефон: {order.customer_phone}",
        f"✉️ Email: {order.customer_email or '—'}",
        "",
        "📦 <b>Товары:</b>",
    ]
    
    for item in order.items:
        product_name = item.product.name if item.product else f"Товар #{item.product_id}"
        lines.append(f"  • {product_name} × {item.quantity} — {item.price * item.quantity:,.0f} ₽".replace(",", " "))
    
    total_str = f"{order.total_amount:,.0f}".replace(",", " ")
    lines.extend([
        "",
        f"💰 <b>Итого: {total_str} ₽</b>",
        "",
        f"📍 Адрес доставки: {order.delivery_address or '—'}",
        f"🚚 Способ получения: Москва 0–2 дня; регионы — уточняет менеджер",
        f"💳 Оплата: При получении",
    ])
    
    if order.comment:
        lines.extend(["", f"💬 Комментарий: {order.comment}"])
    
    return "\n".join(lines)


def send_order_to_telegram(order):
    """Отправляет уведомление о заказе всем staff с кнопкой «Взять в работу!»."""
    text = format_order_message(order)
    markup = order_take_button_markup(order.order_number)
    ok, err, placements = send_telegram_messages(
        text, reply_markup=markup, return_placements=True,
    )
    if ok and placements:
        register_order_notify_messages(order.order_number, placements)
    return ok, err





def send_order_to_telegram_async(order_id: int) -> None:
    """Отправка в Telegram в фоне — checkout не ждёт (избегаем 504 nginx)."""
    def _worker():
        try:
            from app import app
            from models import Order
            with app.app_context():
                order = Order.query.get(order_id)
                if not order:
                    return
                ok, err = send_order_to_telegram(order)
                if not ok:
                    _logger.warning('[Telegram] Заказ %s: %s', order.order_number, err)
        except Exception as exc:
            _logger.warning('[Telegram] async order_id=%s: %s', order_id, exc)

    threading.Thread(
        target=_worker,
        daemon=True,
        name=f'tg-order-{order_id}',
    ).start()

def format_review_pending_message(review):
    """Форматирует отзыв на модерации для Telegram"""
    product_name = "Товар"
    try:
        if review.product:
            product_name = review.product.name
    except Exception:
        pass
    stars = "★" * review.rating + "☆" * (5 - review.rating)
    return (
        f"💬 <b>НОВЫЙ ОТЗЫВ НА МОДЕРАЦИИ</b>\n\n"
        f"📦 Товар: {product_name}\n"
        f"👤 Автор: {review.customer_name}\n"
        f"⭐ Оценка: {stars}\n\n"
        f"📝 Текст:\n{review.text}"
    )


def send_review_pending_to_telegram(review):
    """Отправляет уведомление об отзыве всем staff."""
    text = format_review_pending_message(review)
    reply_markup = {
        "inline_keyboard": [[
            {"text": "✅ Одобрить", "callback_data": f"review_approve_{review.id}"},
            {"text": "❌ Отклонить", "callback_data": f"review_reject_{review.id}"}
        ]]
    }
    return send_telegram_messages(text, reply_markup=reply_markup)
