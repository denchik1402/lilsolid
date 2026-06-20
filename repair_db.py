#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка SQLite, восстановление и пересоздание shop.db при необходимости."""
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


def _recover(path: Path) -> bool:
    ts = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    backup = ROOT / f'shop.db.corrupt.{ts}'
    if path.exists():
        shutil.move(path, backup)
        print(f'[repair_db] backup: {backup.name}')
    recovered = ROOT / 'shop.db.recovered'
    if recovered.exists():
        recovered.unlink()
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


def _run_script(name: str, timeout: int | None = None) -> None:
    script = ROOT / name
    if not script.exists():
        return
    print(f'[repair_db] running {name}')
    subprocess.run([sys.executable, str(script)], cwd=str(ROOT), check=False, timeout=timeout)


def main() -> int:
    ok, msg = _integrity(DB)
    print(f'[repair_db] start integrity: {msg}')

    if not ok:
        if DB.exists() and not _recover(DB):
            if DB.exists():
                DB.unlink()
            print('[repair_db] removed bad shop.db')

    from repair_schema import repair
    repair()

    sys.path.insert(0, str(ROOT))
    from app import app, db
    from models import Category, Product

    with app.app_context():
        try:
            cat_n = Category.query.count()
            prod_n = Product.query.count()
        except Exception as exc:
            print(f'[repair_db] ORM query failed: {exc}')
            db.session.rollback()
            db.create_all()
            cat_n, prod_n = 0, 0

        print(f'[repair_db] categories={cat_n} products={prod_n}')
        if cat_n == 0 or prod_n == 0:
            _run_script('init_db.py')
            _run_script('full_update.py', timeout=180)

        try:
            cat_n = Category.query.count()
            prod_n = Product.query.count()
            print(f'[repair_db] after seed categories={cat_n} products={prod_n}')
        except Exception as exc:
            print(f'[repair_db] post-seed query failed: {exc}')
            return 1

    ok, msg = _integrity(DB)
    print(f'[repair_db] final integrity: {msg}')
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
