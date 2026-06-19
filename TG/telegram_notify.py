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

from staff_notify import send_telegram_messages


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
        f"🚚 Способ получения: Доставка 1–2 дня",
        f"💳 Оплата: При получении",
    ])
    
    if order.comment:
        lines.extend(["", f"💬 Комментарий: {order.comment}"])
    
    return "\n".join(lines)


def send_order_to_telegram(order):
    """Отправляет уведомление о заказе всем staff и в группу."""
    text = format_order_message(order)
    return send_telegram_messages(text)



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
