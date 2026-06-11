# -*- coding: utf-8 -*-
"""Общие расширения (db) — разрывает циклический импорт app <-> models"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
