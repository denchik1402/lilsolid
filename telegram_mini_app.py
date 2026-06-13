# -*- coding: utf-8 -*-
"""API Telegram Mini App для satellite-магазинов (вызывается из app.py)."""
from __future__ import annotations

import re

from flask import jsonify, request, session


def register(app, csrf, db, Product, Category, Order, OrderItem, PromoCode, get_cart_products, logger):
    """Регистрирует /api/telegram-app/* на iqos-store / lilsolid."""

    def _site_base_url():
        try:
            import config
            base = getattr(config, 'SITE_URL', None) or ''
            if base and base.startswith('http') and '127.0.0.1' not in base and 'localhost' not in base:
                return base.rstrip('/')
        except ImportError:
            pass
        return request.url_root.rstrip('/')

    def _abs_product_image(filename):
        if not filename:
            return None
        if str(filename).startswith('http'):
            return filename
        path = str(filename).lstrip('/')
        if not path.startswith('products/') and not path.startswith('static/'):
            path = f'products/{path}'
        if path.startswith('static/'):
            return f"{_site_base_url()}/{path}"
        return f"{_site_base_url()}/static/images/{path}"

    def _fmt_rub(value):
        if value is None:
            return None
        return "{:,.0f}".format(float(value)).replace(",", " ")

    def _parse_for_categories():
        raw = (request.args.get('for_categories') or '').strip()
        if not raw:
            return None
        return [s.strip() for s in raw.split(',') if s.strip()]

    def _category_ids_for_slugs(slugs):
        if not slugs:
            return None
        ids = []
        for slug in slugs:
            cat = Category.query.filter_by(slug=slug).first()
            if cat:
                ids.append(cat.id)
        return ids or None

    def _product_in_scope(product, allowed_ids):
        return not allowed_ids or product.category_id in allowed_ids

    def _telegram_product_payload(product, *, detailed=False):
        img = product.all_images[0] if product.all_images else product.image
        payload = {
            'id': product.id,
            'name': product.name,
            'slug': product.get_url_slug(),
            'price': float(product.price),
            'price_fmt': _fmt_rub(product.price),
            'old_price': float(product.old_price) if product.old_price else None,
            'old_price_fmt': _fmt_rub(product.old_price) if product.old_price else None,
            'image_url': _abs_product_image(img),
            'in_stock': bool(product.in_stock),
            'is_hit': bool(product.is_hit),
            'category_id': product.category_id,
        }
        if detailed:
            intro = product.get_intro_text()
            if intro:
                payload['description'] = re.sub(r'<[^>]+>', '', intro)[:600]
            payload['characteristics'] = [{'key': k, 'value': v} for k, v in product.get_characteristics()[:8]]
        return payload

    def _cart_items_count():
        cart = session.get('cart') or {}
        return sum(int(v) for v in cart.values())

    def _cart_payload():
        cart_items, total = get_cart_products(session.get('cart', {}))
        items = []
        for item in cart_items:
            p = item['product']
            img = p.all_images[0] if p.all_images else p.image
            items.append({
                'product_id': p.id,
                'name': p.name,
                'quantity': item['quantity'],
                'price': float(p.price),
                'price_fmt': _fmt_rub(p.price),
                'subtotal': float(item['subtotal']),
                'subtotal_fmt': _fmt_rub(item['subtotal']),
                'image_url': _abs_product_image(img),
                'in_stock': bool(p.in_stock),
            })
        return {
            'items': items,
            'total': float(total),
            'total_fmt': _fmt_rub(total),
            'cart_count': _cart_items_count(),
        }

    def _place_checkout_order(form_data, idempotency_key):
        from sqlalchemy.exc import IntegrityError
        from checkout_idempotency import find_existing_order

        existing = find_existing_order(Order, idempotency_key)
        if existing:
            return existing, None

        _, server_subtotal = get_cart_products(session.get('cart', {}))
        if server_subtotal <= 0:
            return None, 'empty_cart'

        promo_code = (form_data.get('promo_code') or '').strip().upper()
        server_discount, server_total = 0, server_subtotal
        if promo_code:
            promo = PromoCode.query.filter_by(code=promo_code).first()
            if promo and promo.is_valid():
                server_discount, server_total = promo.apply_discount(server_subtotal)
                if server_discount > 0:
                    promo.used_count += 1

        order = Order(
            customer_name=(form_data.get('name') or '').strip()[:100],
            customer_phone=(form_data.get('phone') or '').strip()[:20],
            customer_email=(form_data.get('email') or '').strip()[:100],
            delivery_address=(form_data.get('address') or '').strip()[:500],
            delivery_method=(form_data.get('delivery') or 'delivery')[:50],
            payment_method=(form_data.get('payment') or 'courier')[:50],
            comment=(form_data.get('comment') or '')[:500],
            total_amount=server_total,
            promo_code=promo_code if server_discount > 0 else None,
            discount_amount=server_discount,
            idempotency_key=idempotency_key,
        )
        db.session.add(order)
        db.session.flush()

        for product_id, quantity in session.get('cart', {}).items():
            try:
                pid = int(product_id)
            except (TypeError, ValueError):
                continue
            product = db.session.get(Product, pid)
            if product and quantity > 0:
                db.session.add(OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=min(int(quantity), 99),
                    price=product.price,
                ))

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            existing = find_existing_order(Order, idempotency_key)
            if existing:
                return existing, None
            raise

        try:
            from telegram_notify import send_order_to_telegram
            ok, err = send_order_to_telegram(order)
            if not ok:
                logger.warning('[Telegram] Заказ %s: %s', order.order_number, err)
        except Exception as e:
            logger.warning('[Telegram] %s', e)

        return order, None

    @app.route('/api/telegram-app/bootstrap')
    def telegram_app_bootstrap():
        allowed_slugs = _parse_for_categories()
        allowed_ids = _category_ids_for_slugs(allowed_slugs)
        categories = Category.query.order_by(Category.name).all()
        cat_payload = []
        for cat in categories:
            if allowed_ids and cat.id not in allowed_ids:
                continue
            count = Product.query.filter_by(category_id=cat.id, in_stock=True).count()
            if count == 0:
                continue
            cat_payload.append({
                'id': cat.id,
                'slug': cat.slug or str(cat.id),
                'name': cat.name,
                'product_count': count,
            })
        hits_q = Product.query.filter_by(is_hit=True, in_stock=True)
        if allowed_ids:
            hits_q = hits_q.filter(Product.category_id.in_(allowed_ids))
        hits = hits_q.order_by(Product.views.desc()).limit(8).all()
        if not hits:
            fallback_q = Product.query.filter_by(in_stock=True)
            if allowed_ids:
                fallback_q = fallback_q.filter(Product.category_id.in_(allowed_ids))
            hits = fallback_q.order_by(Product.views.desc()).limit(8).all()
        return jsonify({
            'categories': cat_payload,
            'portals': [],
            'hits': [_telegram_product_payload(p) for p in hits],
            'cart_count': _cart_items_count(),
        })

    @app.route('/api/telegram-app/products')
    def telegram_app_products():
        allowed_slugs = _parse_for_categories()
        allowed_ids = _category_ids_for_slugs(allowed_slugs)
        category_slug = (request.args.get('category') or '').strip()
        page = max(1, request.args.get('page', 1, type=int))
        per_page = min(24, max(6, request.args.get('per_page', 12, type=int)))
        q = Product.query.filter_by(in_stock=True)
        if category_slug:
            cat = Category.query.filter_by(slug=category_slug).first()
            if not cat and category_slug.isdigit():
                cat = Category.query.get(int(category_slug))
            if cat and (not allowed_ids or cat.id in allowed_ids):
                q = q.filter_by(category_id=cat.id)
            elif allowed_ids:
                q = q.filter(Product.id == -1)
        elif allowed_ids:
            q = q.filter(Product.category_id.in_(allowed_ids))
        q = q.order_by(Product.is_hit.desc(), Product.name)
        pagination = q.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'products': [_telegram_product_payload(p) for p in pagination.items],
            'page': pagination.page,
            'pages': pagination.pages,
            'total': pagination.total,
            'has_next': pagination.has_next,
        })

    @app.route('/api/telegram-app/product/<int:product_id>')
    def telegram_app_product_detail(product_id):
        product = Product.query.get_or_404(product_id)
        allowed_ids = _category_ids_for_slugs(_parse_for_categories())
        if not _product_in_scope(product, allowed_ids):
            return jsonify({'error': 'Товар не найден'}), 404
        return jsonify(_telegram_product_payload(product, detailed=True))

    @app.route('/api/telegram-app/cart')
    def telegram_app_cart():
        return jsonify(_cart_payload())

    @csrf.exempt
    @app.route('/api/telegram-app/checkout', methods=['GET', 'POST'])
    def telegram_app_checkout_api():
        from checkout_idempotency import ensure_checkout_idempotency_key, get_submitted_idempotency_key, finalize_checkout_session

        if request.method == 'GET':
            _, total = get_cart_products(session.get('cart', {}))
            payload = _cart_payload()
            payload['idempotency_key'] = ensure_checkout_idempotency_key(session)
            payload['total'] = float(total)
            payload['total_fmt'] = _fmt_rub(total)
            return jsonify(payload)

        data = request.get_json(silent=True) or {}
        idempotency_key = get_submitted_idempotency_key(data) or ensure_checkout_idempotency_key(session)
        order, err = _place_checkout_order(data, idempotency_key)
        if err == 'empty_cart':
            return jsonify({'success': False, 'error': 'Корзина пуста'}), 400
        if not order:
            return jsonify({'success': False, 'error': 'Не удалось оформить заказ'}), 500
        finalize_checkout_session(session, order.id)
        return jsonify({
            'success': True,
            'order_id': order.id,
            'order_number': order.order_number,
        })
