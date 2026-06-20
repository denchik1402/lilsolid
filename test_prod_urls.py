#!/usr/bin/env python3
import os
import sys

ROOT = os.environ.get('APP_DIR', os.getcwd())
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from app import app

with app.test_client() as c:
    for p in ('/', '/catalog', '/delivery', '/health'):
        r = c.get(p, base_url='https://lilsolid.ru')
        print(p, r.status_code, len(r.data))
        if r.status_code >= 500:
            print((r.get_data(as_text=True) or '')[:500])
