"""Helpers for idempotent SQLite migrations on partially migrated DBs."""
from sqlalchemy import inspect


def column_exists(conn, table: str, column: str) -> bool:
    return column in {c['name'] for c in inspect(conn).get_columns(table)}


def table_exists(conn, table: str) -> bool:
    return inspect(conn).has_table(table)
