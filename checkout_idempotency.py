# -*- coding: utf-8 -*-
"""Ключ идемпотентности для /checkout — защита от двойного нажатия «Оформить»."""
import uuid

SESSION_CHECKOUT_KEY = 'checkout_idempotency_key'


def ensure_checkout_idempotency_key(session) -> str:
    key = (session.get(SESSION_CHECKOUT_KEY) or '').strip()
    if not key or len(key) > 64:
        key = str(uuid.uuid4())
        session[SESSION_CHECKOUT_KEY] = key
        session.modified = True
    return key


def clear_checkout_idempotency_key(session) -> None:
    session.pop(SESSION_CHECKOUT_KEY, None)
    session.modified = True


def get_submitted_idempotency_key(form) -> str:
    return (form.get('idempotency_key') or '').strip()[:64]


def find_existing_order(Order, idempotency_key: str):
    if not idempotency_key:
        return None
    return Order.query.filter_by(idempotency_key=idempotency_key).first()


def one_click_idempotency_key(session, product_id: int) -> str:
    """Стабильный ключ для повторных кликов «1 клик» по одному товару в сессии."""
    base = ensure_checkout_idempotency_key(session)
    return f'{base}-oc-{int(product_id)}'[:64]


def finalize_checkout_session(session, order_id: int) -> None:
    session['cart'] = {}
    session['last_order_id'] = order_id
    clear_checkout_idempotency_key(session)
    session.modified = True
