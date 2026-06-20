#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Расширить repair_schema — колонки banner/product и home_block."""
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding='utf-8')

marker = "if _add_column_if_missing('review', 'status'"
if 'banner' in text and 'impressions' in text:
    print(f'{path}: banner columns already in repair_schema')
    sys.exit(0)

insert = """        for col, ddl in (
            ('impressions', 'impressions INTEGER DEFAULT 0'),
            ('clicks', 'clicks INTEGER DEFAULT 0'),
            ('ab_test_group', 'ab_test_group VARCHAR(50)'),
            ('badge_type', 'badge_type VARCHAR(20)'),
            ('product_id', 'product_id INTEGER'),
        ):
            if _add_column_if_missing('banner', col, ddl):
                changed += 1

        if _add_column_if_missing('product', 'is_hit', 'is_hit BOOLEAN DEFAULT 0'):
            changed += 1

        if 'home_block' not in tables:
            db.create_all()
            print('[repair] created home_block table')
            changed += 1

"""

if marker not in text:
    print(f'{path}: marker not found')
    sys.exit(1)

text = text.replace(marker, insert + marker, 1)
path.write_text(text, encoding='utf-8')
print(f'{path}: extended repair_schema')
