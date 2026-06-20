#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Защита inject_nav_categories от падения при битой БД."""
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding='utf-8')

old = """@app.context_processor
def inject_nav_categories():
    \"\"\"Категории для выпадающего меню «Каталог» в шапке.\"\"\"
    categories = cache.get('nav_categories')
    if categories is None:
        categories = _get_nav_categories()
        cache.set('nav_categories', categories, timeout=300)
    return {'nav_categories': categories}"""

new = """@app.context_processor
def inject_nav_categories():
    \"\"\"Категории для выпадающего меню «Каталог» в шапке.\"\"\"
    try:
        categories = cache.get('nav_categories')
        if categories is None:
            categories = _get_nav_categories()
            cache.set('nav_categories', categories, timeout=300)
        return {'nav_categories': categories}
    except Exception as exc:
        logger.warning('nav_categories failed: %s', exc)
        try:
            db.session.rollback()
        except Exception:
            pass
        return {'nav_categories': []}"""

if old not in text:
    if 'nav_categories failed' in text:
        print(f'{path}: already patched')
        sys.exit(0)
    print(f'{path}: inject_nav_categories block not found')
    sys.exit(1)

path.write_text(text.replace(old, new, 1), encoding='utf-8')
print(f'{path}: nav categories guarded')
