#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch repair_db.py on lilsolid: use apply_store_sync instead of full_update."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / 'repair_db.py'

OLD = """        if cat_n == 0 or prod_n == 0:
            _run('init_db.py')
            _run('full_update.py', timeout=180)
            _run('fix_product_images.py')
            _run('update_product_galleries.py', timeout=120)"""

NEW = """        if cat_n == 0 or prod_n == 0:
            _run('init_db.py')
            _run('scripts/apply_store_sync.py', timeout=300)
            _run('fix_product_images.py')
            _run('update_product_galleries.py', timeout=120)"""

OLD2 = """            _run('init_db.py')
            _run('full_update.py', timeout=180)
            _run('fix_product_images.py')
            _run('update_product_galleries.py', timeout=120)
            if smoke_main() != 0:"""

NEW2 = """            _run('init_db.py')
            _run('scripts/apply_store_sync.py', timeout=300)
            _run('fix_product_images.py')
            _run('update_product_galleries.py', timeout=120)
            if smoke_main() != 0:"""


def main() -> int:
    if not TARGET.exists():
        print(f'missing {TARGET}')
        return 1
    text = TARGET.read_text(encoding='utf-8')
    if OLD in text:
        text = text.replace(OLD, NEW)
    if OLD2 in text:
        text = text.replace(OLD2, NEW2)
    if 'full_update.py' in text and 'apply_store_sync.py' not in text:
        text = text.replace("'full_update.py'", "'scripts/apply_store_sync.py'")
        text = text.replace('timeout=180', 'timeout=300')
    TARGET.write_text(text, encoding='utf-8')
    print('repair_db patched for lilsolid sync')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
