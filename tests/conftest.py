# -*- coding: utf-8 -*-
"""Pytest fixtures для LIL STORE."""
import os
import pytest


@pytest.fixture
def app():
    """Flask app с тестовой БД."""
    os.environ.setdefault('SECRET_KEY', 'test-secret-key')
    from app import app
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app


@pytest.fixture
def client(app):
    """Тестовый клиент."""
    return app.test_client()


@pytest.fixture
def app_ctx(app):
    """Контекст приложения и создание таблиц."""
    with app.app_context():
        from extensions import db
        db.create_all()
        yield
