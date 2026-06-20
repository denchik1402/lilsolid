#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Checkout: Telegram notify in background (fix 504 on iqos/lilsolid)."""
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding='utf-8')

BROKEN = """            try:
                try:
            from telegram_notify import send_order_to_telegram_async
            send_order_to_telegram_async(order.id)
        except Exception as e:
            logger.warning('[Telegram async] order_id=%s: %s', order.id, e)

            finalize_checkout_session(session, order.id)

            return redirect(url_for('order_success', order_id=order.id))"""

FIXED = """            try:
                from telegram_notify import send_order_to_telegram_async
                send_order_to_telegram_async(order.id)
            except Exception as e:
                logger.warning('[Telegram async] order_id=%s: %s', order.id, e)

            finalize_checkout_session(session, order.id)

            return redirect(url_for('order_success', order_id=order.id))"""

if BROKEN in text:
    text = text.replace(BROKEN, FIXED, 1)
    path.write_text(text, encoding='utf-8')
    print(f'{path}: repaired broken indent')
    sys.exit(0)

if 'send_order_to_telegram_async(order.id)' in text and 'send_order_to_telegram(order)' not in text:
    print(f'{path}: already async')
    sys.exit(0)

# Только блок с send_order_to_telegram (4 пробела внутри POST try)
block_re = re.compile(
    r'([ \t]{12})try:\n'
    r'\1    from telegram_notify import send_order_to_telegram\n'
    r'\1    ok, err = send_order_to_telegram\(order\)\n'
    r'(?:\1    .*\n)*?'
    r'\1except Exception as e:\n'
    r'\1    .*\n',
    re.MULTILINE,
)

replacement = (
    r'\1try:\n'
    r'\1    from telegram_notify import send_order_to_telegram_async\n'
    r'\1    send_order_to_telegram_async(order.id)\n'
    r'\1except Exception as e:\n'
    r"\1    logger.warning('[Telegram async] order_id=%s: %s', order.id, e)\n"
)

new_text, n = block_re.subn(replacement, text)
if n == 0:
    print(f'{path}: WARNING no blocks patched')
    sys.exit(1)

path.write_text(new_text, encoding='utf-8')
import py_compile
py_compile.compile(str(path), doraise=True)
print(f'{path}: patched {n} checkout block(s)')
