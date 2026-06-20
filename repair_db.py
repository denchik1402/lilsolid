#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SQLite integrity check, recovery, schema repair, seed if empty."""
from __future__ import annotations

import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'shop.db'


def _integrity(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, 'file missing'
    if path.stat().st_size == 0:
        return False, 'file empty'
    try:
        conn = sqlite3.connect(str(path), timeout=10)
        row = conn.execute('PRAGMA quick_check').fetchone()
        conn.close()
        if row and row[0] == 'ok':
            return True, 'ok'
        return False, str(row[0] if row else 'quick_check failed')
    except sqlite3.DatabaseError as exc:
        return False, str(exc)


def _recover_file(path: Path) -> bool:
    ts = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    backup = ROOT / f'shop.db.corrupt.{ts}'
    if path.exists():
        shutil.move(path, backup)
        print(f'[repair_db] backup: {backup.name}')
    recovered = ROOT / 'shop.db.recovered'
    if recovered.exists():
        recovered.unlink(missing_ok=True)
    if backup.exists():
        rc = os.system(f'sqlite3 "{backup}" ".recover" | sqlite3 "{recovered}"')
        if rc == 0 and recovered.exists() and recovered.stat().st_size > 0:
            ok, msg = _integrity(recovered)
            if ok:
                shutil.move(recovered, path)
                print('[repair_db] recovered via sqlite3 .recover')
                return True
            print(f'[repair_db] recovered file still bad: {msg}')
    return False


def _run(name: str, timeout: int | None = None) -> None:
    script = ROOT / name
    if script.exists():
        print(f'[repair_db] running {name}')
        subprocess.run([sys.executable, str(script)], cwd=str(ROOT), check=False, timeout=timeout)


def main() -> int:
    ok, msg = _integrity(DB)
    print(f'[repair_db] start integrity: {msg}')
    if not ok:
        if DB.exists() and not _recover_file(DB):
            DB.unlink(missing_ok=True)
            print('[repair_db] removed bad shop.db')

    if not DB.exists():
        print('[repair_db] creating empty shop.db')
        sqlite3.connect(str(DB)).close()

    sys.path.insert(0, str(ROOT))

    try:
        from repair_schema import repair
        repair()
    except Exception as exc:
        print(f'[repair_db] repair_schema warning: {exc}')

    try:
        from app import app, db
        from models import Category, Product
    except Exception as exc:
        print(f'[repair_db] cannot import app: {exc}')
        _run('init_db.py')
        return 1

    with app.app_context():
        try:
            cat_n = Category.query.count()
            prod_n = Product.query.count()
        except Exception as exc:
            print(f'[repair_db] ORM query failed: {exc}')
            db.session.rollback()
            try:
                db.create_all()
            except Exception as exc2:
                print(f'[repair_db] create_all failed: {exc2}')
            cat_n, prod_n = 0, 0

        print(f'[repair_db] categories={cat_n} products={prod_n}')
        if cat_n == 0 or prod_n == 0:
            _run('init_db.py')
            _run('full_update.py', timeout=180)
            try:
                cat_n = Category.query.count()
                prod_n = Product.query.count()
                print(f'[repair_db] after seed categories={cat_n} products={prod_n}')
            except Exception as exc:
                print(f'[repair_db] post-seed query failed: {exc}')
                return 1

    ok, msg = _integrity(DB)
    print(f'[repair_db] final integrity: {msg}')

    # Smoke test — if pages still 500, rebuild DB from scratch once
    try:
        from smoke_test import main as smoke_main
        if smoke_main() != 0:
            print('[repair_db] smoke test failed, rebuilding shop.db')
            if DB.exists():
                ts = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
                shutil.move(DB, ROOT / f'shop.db.failed_smoke.{ts}')
            sqlite3.connect(str(DB)).close()
            from repair_schema import repair
            repair()
            _run('init_db.py')
            _run('full_update.py', timeout=180)
            if smoke_main() != 0:
                print('[repair_db] smoke test still failing after rebuild')
                return 1
    except Exception as exc:
        print(f'[repair_db] smoke test warning: {exc}')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
