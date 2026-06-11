#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Однократная загрузка себестоимости из iluma.xlsx в Product.cost.
Запуск: python load_costs_from_xlsx.py
После этого xlsx не используется — прибыль считается из Product.cost на сайте.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def _get_iluma_path():
    try:
        import config
        return getattr(config, 'ILUMA_XLSX_PATH', None)
    except ImportError:
        pass
    return r'c:\Users\Dubko\Desktop\iluma.xlsx'


def load_costs():
    """Возвращает {product_name: cost} из xlsx"""
    result = {}
    path = _get_iluma_path()
    if not os.path.exists(path):
        print(f"Файл не найден: {path}")
        return result
    try:
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb.active
        headers = []
        for row_idx, row in enumerate(ws.iter_rows(values_only=True)):
            if row_idx == 0:
                headers = [str(c).lower() if c else '' for c in row]
                continue
            if not any(row):
                continue
            name_col = cost_col = None
            for i, h in enumerate(headers):
                if h and ('назва' in h or 'name' in h or 'товар' in h):
                    name_col = i
                elif h and ('себесто' in h or 'cost' in h):
                    cost_col = i
            if name_col is None:
                name_col = 0
            if cost_col is None and len(row) > 2:
                cost_col = 2
            elif cost_col is None:
                cost_col = 1
            name = row[name_col] if name_col is not None and len(row) > name_col else None
            cost_val = row[cost_col] if cost_col is not None and len(row) > cost_col else None
            if name and cost_val is not None:
                try:
                    result[str(name).strip()] = float(cost_val)
                except (ValueError, TypeError):
                    pass
        wb.close()
    except ImportError:
        print("Установите: pip install openpyxl")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка чтения xlsx: {e}")
    return result


def main():
    from app import app, db
    from models import Product

    costs = load_costs()
    if not costs:
        print("Нет данных для загрузки.")
        return

    updated = 0
    with app.app_context():
        for p in Product.query.all():
            cost = costs.get(p.name)
            if cost is not None:
                p.cost = cost
                updated += 1
                print(f"  {p.name[:40]}: себестоимость {cost} ₽")

        db.session.commit()
    print(f"\nОбновлено {updated} товаров. Себестоимость сохранена в Product.cost.")


if __name__ == "__main__":
    main()
