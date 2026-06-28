#!/usr/bin/env python3
"""Синхронизация справочника моделей и привязка model у товаров."""
from __future__ import annotations

from datetime import datetime

from device_models_utils import (
    CANONICAL_DEVICE_MODELS,
    LEGACY_MODEL_NAMES,
    detect_device_model,
    normalize_legacy_model,
)
from seo_utils import device_model_slug


def sync_device_model_catalog(db, DeviceModel, Product):
    """Создаёт/обновляет записи device_model, переименовывает legacy."""
    now = datetime.utcnow()

    for old_name, new_name in LEGACY_MODEL_NAMES.items():
        row = DeviceModel.query.filter(DeviceModel.name == old_name).first()
        if row:
            row.name = new_name
        Product.query.filter(Product.model == old_name).update({'model': new_name})
        Product.query.filter(Product.model == old_name.lower()).update({'model': new_name})

    for name, sort_order in CANONICAL_DEVICE_MODELS:
        row = DeviceModel.query.filter(db.func.lower(DeviceModel.name) == name.lower()).first()
        if not row:
            row = DeviceModel(name=name, sort_order=sort_order, created_at=now)
            db.session.add(row)
        else:
            row.name = name
            row.sort_order = sort_order
        slug = device_model_slug(name)
        if slug and not row.slug:
            row.slug = slug

    db.session.commit()


def assign_product_models(db, Product):
    """Проставляет Product.model по названию."""
    updated = 0
    for product in Product.query.all():
        detected = detect_device_model(product.name, product.description or '')
        if detected and product.model != detected:
            product.model = detected
            updated += 1
        elif product.model:
            normalized = normalize_legacy_model(product.model)
            if normalized and product.model != normalized:
                product.model = normalized
                updated += 1
    db.session.commit()
    return updated


def rebalance_hit_flags(db, Product):
    """Хиты: ILUMA + LIL + TEREA, не только стики."""
    from homepage_carousel import pick_hit_product_ids
    products = Product.query.filter(Product.in_stock == True).all()
    if not products:
        products = Product.query.all()
    target_ids = set(pick_hit_product_ids(products))
    changed = 0
    for product in Product.query.all():
        should_hit = product.id in target_ids
        if product.is_hit != should_hit:
            product.is_hit = should_hit
            changed += 1
    db.session.commit()
    return changed, len(target_ids)


def run(rebalance_hits: bool = False):
    from app import app, cache
    from models import DeviceModel, Product
    from extensions import db

    with app.app_context():
        sync_device_model_catalog(db, DeviceModel, Product)
        model_updates = assign_product_models(db, Product)
        hit_changed, hit_total = 0, 0
        if rebalance_hits:
            hit_changed, hit_total = rebalance_hit_flags(db, Product)
        cache.delete('index_data')
        print(
            f'Models synced; products updated: {model_updates}; '
            f'hits rebalanced: {hit_changed} (target {hit_total})'
        )


if __name__ == '__main__':
    run(rebalance_hits=False)
