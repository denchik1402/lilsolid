#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Исправить IndentationError после patch_checkout_async на iqos/lilsolid."""
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

if BROKEN not in text:
    if FIXED.split('\n')[1] in text:
        print(f'{path}: already fixed')
        sys.exit(0)
    print(f'{path}: broken block not found')
    sys.exit(1)

text = text.replace(BROKEN, FIXED, 1)
path.write_text(text, encoding='utf-8')

import py_compile
py_compile.compile(str(path), doraise=True)
print(f'{path}: fixed and verified')
