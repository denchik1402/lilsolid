#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Replace demo catalog with full_update products when test data detected."""
from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

TEST_IMAGE_MARKERS = (
    'iluma-prime-golden', 'iluma-one.jpg', 'terea-rich', 'case-black', 'charger.jpg',
)


def needs_real_catalog() -> bool:
    from app import app
    from models import Product

    with app.app_context():
        count = Product.query.count()
        if count < 15:
            return True
        for p in Product.query.limit(30).all():
            img = (p.image or '').lower()
            if any(m in img for m in TEST_IMAGE_MARKERS):
                return True
    return False


def main() -> int:
    if not needs_real_catalog():
        print('[ensure_catalog] real catalog OK')
        return 0
    print('[ensure_catalog] test/demo catalog detected — running full_update.py')
    rc = subprocess.run([sys.executable, 'full_update.py'], cwd=ROOT).returncode
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
