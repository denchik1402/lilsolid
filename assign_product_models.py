#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Присвоение моделей устройствам по названию (см. device_models_utils)."""

from device_models_utils import detect_device_model, normalize_legacy_model


def detect_model(name, description=''):
    return detect_device_model(name, description)


def run():
    from app import app
    from models import Product
    from extensions import db

    with app.app_context():
        products = Product.query.all()
        updated = 0
        no_model = []
        for p in products:
            model = detect_device_model(p.name, p.description or '')
            if not model and p.model:
                model = normalize_legacy_model(p.model)
            if model:
                if p.model != model:
                    p.model = model
                    updated += 1
                    print(f"  {p.name[:55]} -> {model}")
            else:
                no_model.append(p.name)
        db.session.commit()
        print(f"\nОбновлено: {updated} из {len(products)} товаров")
        if no_model:
            print(f"\nБез модели (не распознаны):")
            for n in no_model[:15]:
                print(f"  - {n}")
            if len(no_model) > 15:
                print(f"  ... и ещё {len(no_model) - 15}")


if __name__ == '__main__':
    run()
