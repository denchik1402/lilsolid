# -*- coding: utf-8 -*-
"""Единый источник правды по статусам заказов (сайт + Telegram)."""
from __future__ import annotations

STATUS_NEW = 'new'
STATUS_PROCESSING = 'processing'
STATUS_COMPLETED = 'completed'
STATUS_CANCELLED = 'cancelled'

VALID_STATUSES = (STATUS_NEW, STATUS_PROCESSING, STATUS_COMPLETED, STATUS_CANCELLED)

STATUS_LABELS_RU = {
    STATUS_NEW: 'Новый',
    STATUS_PROCESSING: 'В работе',
    STATUS_COMPLETED: 'Получен',  # клиент получил заказ (после доставки)
    STATUS_CANCELLED: 'Отменён',
}

STATUS_BADGE = {
    STATUS_NEW: 'info',
    STATUS_PROCESSING: 'primary',
    STATUS_COMPLETED: 'success',
    STATUS_CANCELLED: 'danger',
}

# Допустимые переходы (from -> to)
_ALLOWED = {
    STATUS_NEW: {STATUS_PROCESSING, STATUS_CANCELLED},
    STATUS_PROCESSING: {STATUS_COMPLETED, STATUS_CANCELLED, STATUS_PROCESSING},
    STATUS_COMPLETED: {STATUS_PROCESSING},  # редкий откат админом
    STATUS_CANCELLED: {STATUS_NEW, STATUS_PROCESSING},
}


def normalize_status(raw) -> str:
    s = (raw or STATUS_NEW).strip().lower()
    aliases = {
        'done': STATUS_COMPLETED,
        'delivered': STATUS_COMPLETED,
        'complete': STATUS_COMPLETED,
        'finished': STATUS_COMPLETED,
        'refused': STATUS_CANCELLED,
        'canceled': STATUS_CANCELLED,
        'cancel': STATUS_CANCELLED,
        'in_work': STATUS_PROCESSING,
        'in-work': STATUS_PROCESSING,
        'working': STATUS_PROCESSING,
        'taken': STATUS_PROCESSING,
    }
    s = aliases.get(s, s)
    return s if s in VALID_STATUSES else STATUS_NEW


def status_label(raw) -> str:
    return STATUS_LABELS_RU.get(normalize_status(raw), str(raw or '—'))


def status_badge(raw) -> str:
    return STATUS_BADGE.get(normalize_status(raw), 'secondary')


def can_transition(current, new) -> bool:
    cur = normalize_status(current)
    nxt = normalize_status(new)
    if cur == nxt:
        return True
    return nxt in _ALLOWED.get(cur, set())


def apply_order_status(order, new_status: str, *, force: bool = False) -> bool:
    """Ставит статус на модели Order. Возвращает True если изменился."""
    nxt = normalize_status(new_status)
    cur = normalize_status(getattr(order, 'status', None))
    if cur == nxt:
        return False
    if not force and not can_transition(cur, nxt):
        return False
    order.status = nxt
    if nxt == STATUS_NEW:
        order.courier_telegram_id = None
    if nxt == STATUS_CANCELLED:
        # курьер снимается при отмене
        pass
    return True


def sync_taken_state(order_number: str, *, telegram_id: int | None, display_name: str, outcome: str) -> None:
    """Синхронизирует BotSetting order_taken_* с исходом (in_work / delivered / refused)."""
    try:
        from order_notify import (
            ORDER_STATUS_DELIVERED,
            ORDER_STATUS_IN_WORK,
            ORDER_STATUS_REFUSED,
            set_order_outcome,
            set_order_taken,
        )
    except ImportError:
        return
    if outcome == STATUS_PROCESSING or outcome == 'in_work':
        if telegram_id:
            set_order_taken(order_number, int(telegram_id), display_name or 'Сотрудник')
        return
    if outcome == STATUS_COMPLETED:
        set_order_outcome(
            order_number,
            ORDER_STATUS_DELIVERED,
            int(telegram_id or 0),
            display_name or 'Сотрудник',
        )
        return
    if outcome == STATUS_CANCELLED:
        set_order_outcome(
            order_number,
            ORDER_STATUS_REFUSED,
            int(telegram_id or 0),
            display_name or 'Сотрудник',
        )


def heal_order_status_from_taken(order) -> bool:
    """
    Если в TG заказ «в работе», а в БД ещё new — поднимаем до processing.
    Не трогаем completed/cancelled.
    """
    try:
        from order_notify import ORDER_STATUS_DELIVERED, ORDER_STATUS_IN_WORK, ORDER_STATUS_REFUSED, get_order_taken
    except ImportError:
        return False
    num = getattr(order, 'order_number', None)
    if not num:
        return False
    taken = get_order_taken(num)
    if not taken:
        return False
    tstatus = taken.get('status') or ORDER_STATUS_IN_WORK
    cur = normalize_status(order.status)
    changed = False
    if tstatus == ORDER_STATUS_IN_WORK and cur == STATUS_NEW:
        order.status = STATUS_PROCESSING
        tid = taken.get('telegram_id')
        if tid and not order.courier_telegram_id:
            try:
                order.courier_telegram_id = int(tid)
            except (TypeError, ValueError):
                pass
        changed = True
    elif tstatus == ORDER_STATUS_DELIVERED and cur in (STATUS_NEW, STATUS_PROCESSING):
        order.status = STATUS_COMPLETED
        changed = True
    elif tstatus == ORDER_STATUS_REFUSED and cur in (STATUS_NEW, STATUS_PROCESSING):
        order.status = STATUS_CANCELLED
        changed = True
    return changed
