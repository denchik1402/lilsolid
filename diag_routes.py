#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Print tracebacks for routes returning 500 (deploy diagnostics)."""
import traceback

from app import app


def main() -> int:
    failed = 0
    with app.app_context():
        with app.test_client() as client:
            for path in ('/', '/catalog', '/delivery', '/health'):
                try:
                    resp = client.get(path, follow_redirects=False)
                    print(f'{path} -> {resp.status_code}')
                    if resp.status_code >= 500:
                        failed += 1
                        print((resp.get_data(as_text=True) or '')[:2000])
                except Exception:
                    failed += 1
                    print(f'{path} EXCEPTION:')
                    traceback.print_exc()
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
