# -*- coding: utf-8 -*-
"""
Отправка уведомлений о заказах в Telegram.
Рассылка: admin, boss, courier (личка) + групповой чат (если настроен /set_notify).
"""

import os
import logging
import threading
from html import escape
from urllib.parse import urlparse

from staff_notify import send_telegram_messages, get_group_chat_id, get_bot_token
from order_notify import order_take_button_markup, register_order_notify_messages

_logger = logging.getLogger(__name__)


def get_config():
    """Получает token и chat_id (группа — для обратной совместимости)."""
    token = get_bot_token()
    chat_id = get_group_chat_id()
    return token, chat_id


def _site_order_label() -> str:
    """Домен витрины: lilstore.ru / iqos-store.ru / lilsolid.ru / iluma-iqos.ru."""
    url = os.environ.get('SITE_URL', '')
    if not url and os.path.exists('config.py'):
        try:
            import config
            url = getattr(config, 'SITE_URL', None) or ''
        except ImportError:
            pass
    if not url:
        try:
            from flask import has_request_context, request
            if has_request_context():
                url = request.url_root.rstrip('/')
        except Exception:
            pass
    parsed = urlparse(url if '://' in (url or '') else f'https://{url or ""}')
    host = (parsed.netloc or '').lower()
    if host.startswith('www.'):
        host = host[4:]
    if 'iqos-store' in host:
        return 'iqos-store.ru'
    if 'lilsolid' in host:
        return 'lilsolid.ru'
    if 'iluma-iqos' in host or host.startswith('iluma'):
        return 'iluma-iqos.ru'
    if 'lilstore' in host:
        return 'lilstore.ru'
    return host or 'lilstore.ru'


def format_order_message(order):
    """Форматирует заказ для Telegram (HTML-safe)."""
    from delivery_options import format_delivery_line

    lines = [
        f"🛒 <b>НОВЫЙ ЗАКАЗ</b> · {_site_order_label()}",
        "",
        f"📋 Номер: <code>{escape(str(order.order_number or ''))}</code>",
        f"👤 Клиент: {escape(str(order.customer_name or '—'))}",
        f"📞 Телефон: {escape(str(order.customer_phone or '—'))}",
        f"✉️ Email: {escape(str(order.customer_email or '—'))}",
        "",
        "📦 <b>Товары:</b>",
    ]

    goods_sum = 0.0
    for item in order.items:
        product_name = item.product.name if item.product else f"Товар #{item.product_id}"
        line_sum = (item.price or 0) * (item.quantity or 0)
        goods_sum += line_sum
        lines.append(
            f"  • {escape(str(product_name))} × {int(item.quantity or 0)} — "
            f"{line_sum:,.0f} ₽".replace(",", " ")
        )

    total_str = f"{(order.total_amount or 0):,.0f}".replace(",", " ")
    lines.extend([
        "",
        f"💰 Товары: {goods_sum:,.0f} ₽".replace(",", " "),
        f"🚚 Доставка: {escape(format_delivery_line(order.delivery_method))}",
        f"💰 <b>Итого: {total_str} ₽</b>",
        "",
        f"📍 Адрес доставки: {escape(str(order.delivery_address or '—'))}",
        "💳 Оплата: При получении",
    ])

    if order.comment:
        lines.extend(["", f"💬 Комментарий: {escape(str(order.comment))}"])

    return "\n".join(lines)


def send_order_to_telegram(order):
    """Отправляет уведомление о заказе всем staff с кнопкой «Взять в работу!»."""
    text = format_order_message(order)
    markup = order_take_button_markup(order.order_number)
    ok, err, placements = send_telegram_messages(
        text, reply_markup=markup, return_placements=True,
    )
    if not ok:
        _logger.warning('[Telegram] с кнопкой не ушло (%s), повтор без markup', err)
        ok, err, placements = send_telegram_messages(
            text, reply_markup=None, return_placements=True,
        )
    if ok and placements:
        try:
            register_order_notify_messages(order.order_number, placements)
        except Exception as reg_err:
            _logger.warning('[Telegram] register placements: %s', reg_err)
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
                    _logger.warning('[Telegram] order_id=%s не найден', order_id)
                    return
                ok, err = send_order_to_telegram(order)
                if not ok:
                    _logger.error('[Telegram] Заказ %s НЕ отправлен: %s', order.order_number, err)
                else:
                    _logger.info('[Telegram] Заказ %s отправлен', order.order_number)
        except Exception as exc:
            _logger.exception('[Telegram] async order_id=%s: %s', order_id, exc)

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
        f"📦 Товар: {escape(str(product_name))}\n"
        f"👤 Автор: {escape(str(review.customer_name or ''))}\n"
        f"⭐ Оценка: {stars}\n\n"
        f"📝 Текст:\n{escape(str(review.text or ''))}"
    )


def send_review_pending_to_telegram(review):
    """Отправляет уведомление об отзыве всем staff с кнопками одобрения/отклонения"""
    text = format_review_pending_message(review)
    reply_markup = {
        "inline_keyboard": [[
            {"text": "✅ Одобрить", "callback_data": f"review_approve_{review.id}"},
            {"text": "❌ Отклонить", "callback_data": f"review_reject_{review.id}"}
        ]]
    }
    return send_telegram_messages(text, reply_markup=reply_markup)
