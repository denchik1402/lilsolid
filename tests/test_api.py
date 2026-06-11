# -*- coding: utf-8 -*-
"""Тесты API."""
import pytest


def test_cart_count(client, app_ctx):
    """API cart-count — 200, JSON с count."""
    r = client.get('/api/cart-count')
    assert r.status_code == 200
    data = r.get_json()
    assert 'count' in data
    assert isinstance(data['count'], (int, float))


def test_search_suggestions_empty(client, app_ctx):
    """API search-suggestions с коротким запросом — пустой список."""
    r = client.get('/api/search-suggestions?q=a')
    assert r.status_code == 200
    data = r.get_json()
    assert data.get('suggestions') == []


def test_search_suggestions(client, app_ctx):
    """API search-suggestions — 200, структура suggestions."""
    r = client.get('/api/search-suggestions?q=IQOS')
    assert r.status_code == 200
    data = r.get_json()
    assert 'suggestions' in data
    assert isinstance(data['suggestions'], list)


def test_products_by_ids_empty(client, app_ctx):
    """API products-by-ids без ids — пустой список."""
    r = client.get('/api/products-by-ids')
    assert r.status_code == 200
    data = r.get_json()
    assert 'products' in data
    assert data['products'] == []
