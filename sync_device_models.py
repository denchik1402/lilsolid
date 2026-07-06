#!/usr/bin/env python3
"""Синхронизация справочника моделей и привязка model у товаров."""
from __future__ import annotations

from datetime import datetime

from device_models_utils import (
    CANONICAL_DEVICE_MODELS,
    LEGACY_MODEL_NAMES,
    detect_device_model,
    is_stick_product_name,
    normalize_legacy_model,
)
from homepage_carousel import pick_hit_product_ids
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
        if is_stick_product_name(product.name or ''):
            if product.model:
                product.model = None
                updated += 1
            continue
        if (product.model or '') == 'IQOS ILUMA STANDART':
            product.model = None
            updated += 1
            continue
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


def cleanup_legacy_device_models(db, DeviceModel, Product):
    """Удаляет пустые устаревшие модели (IQOS ILUMA STANDART без устройств)."""
    removed = 0
    for dm in DeviceModel.query.filter(DeviceModel.name == 'IQOS ILUMA STANDART').all():
        count = Product.query.filter(db.func.lower(Product.model) == dm.name.lower()).count()
        if count == 0:
            db.session.delete(dm)
            removed += 1
    db.session.commit()
    return removed


def rebalance_hit_flags(db, Product):
    """Хиты: ILUMA + LIL + TEREA, не только стики."""
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
        removed = cleanup_legacy_device_models(db, DeviceModel, Product)
        hit_changed, hit_total = 0, 0
        if rebalance_hits:
            hit_changed, hit_total = rebalance_hit_flags(db, Product)
        cache.delete('index_data')
        print(
            f'Models synced; products updated: {model_updates}; '
            f'legacy models removed: {removed}; '
            f'hits rebalanced: {hit_changed} (target {hit_total})'
        )


if __name__ == '__main__':
    run(rebalance_hits=True)
