# -*- coding: utf-8 -*-
"""Единая точка доступа к Telegram Bot API (прямой или через tg-proxy)."""
from __future__ import annotations

import os
from urllib.parse import urlparse

DEFAULT_API_ROOT = 'https://api.telegram.org'


def _from_config(name: str, default: str = '') -> str:
    val = os.environ.get(name, '')
    if val:
        return str(val).strip()
    try:
        import config
        return str(getattr(config, name, default) or default).strip()
    except ImportError:
        return default


def get_telegram_api_root() -> str:
    """
    Корень API без /bot.
    Пример прокси: https://tg-proxy.devfuture.ru
    По умолчанию: https://api.telegram.org
    """
    raw = _from_config('TELEGRAM_API_BASE', '') or DEFAULT_API_ROOT
    raw = raw.rstrip('/')
    # допускаем TELEGRAM_API_BASE=.../bot — нормализуем
    if raw.endswith('/bot'):
        raw = raw[:-4]
    return raw or DEFAULT_API_ROOT


def get_ptb_base_url() -> str:
    """base_url для python-telegram-bot (должен оканчиваться на /bot)."""
    return f'{get_telegram_api_root()}/bot'


def get_ptb_base_file_url() -> str:
    return f'{get_telegram_api_root()}/file/bot'


def get_proxy_secret() -> str:
    return _from_config('TELEGRAM_PROXY_SECRET', '')


def telegram_method_url(token: str, method: str) -> str:
    """Полный URL метода: {root}/bot{token}/{method}."""
    method = (method or '').lstrip('/')
    return f'{get_telegram_api_root()}/bot{token}/{method}'


def telegram_request_headers() -> dict[str, str]:
    """Опциональный секрет для tg-proxy (если задан TELEGRAM_PROXY_SECRET)."""
    headers = {'User-Agent': 'LilStore-Telegram/1.0'}
    secret = get_proxy_secret()
    if secret:
        headers['X-Proxy-Secret'] = secret
        headers['X-Telegram-Proxy-Secret'] = secret
    return headers


def using_custom_api() -> bool:
    root = get_telegram_api_root()
    host = urlparse(root).hostname or ''
    return host not in ('', 'api.telegram.org')
