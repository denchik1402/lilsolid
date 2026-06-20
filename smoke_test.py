#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smoke test key pages; exit 1 if any 500."""
import sys

from app import app


def main() -> int:
    failed = []
    with app.test_client() as client:
        for path in ('/', '/catalog', '/delivery', '/health'):
            resp = client.get(path)
            print(f'{path} -> {resp.status_code}')
            if resp.status_code >= 500:
                failed.append(path)
                body = (resp.get_data(as_text=True) or '')[:800]
                print(body)
    if failed:
        print('FAILED:', ', '.join(failed))
        return 1
    print('OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
