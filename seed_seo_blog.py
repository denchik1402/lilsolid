#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SEO-контент: slug моделей, тексты категорий, статьи блога.
Запуск: python seed_seo_blog.py
"""
import sys
from datetime import datetime

from blog_posts_cyber import BLOG_POSTS_CYBER, LEGACY_SHARED_BLOG_SLUGS
from app import app
from extensions import db
from models import BlogPost, Category, DeviceModel
from seo_utils import (
    device_model_slug,
    generate_category_seo,
    generate_device_model_seo,
    normalize_device_model_name,
    CATEGORY_HOME,
)

BLOG_POSTS = BLOG_POSTS_CYBER


def remove_legacy_shared_posts() -> int:
    """Удаляет статьи с общими slug из шаблона my_shop."""
    deleted = 0
    for slug in LEGACY_SHARED_BLOG_SLUGS:
        post = BlogPost.query.filter_by(slug=slug).first()
        if post:
            db.session.delete(post)
            deleted += 1
    return deleted


def seed_device_model_slugs() -> int:
    updated = 0
    for dm in DeviceModel.query.all():
        name = normalize_device_model_name(dm.name)
        slug = device_model_slug(name)
        if dm.slug != slug:
            dm.slug = slug
            updated += 1
    return updated


def seed_category_seo_text() -> int:
    updated = 0
    for category in Category.query.all():
        seo = generate_category_seo(category)
        home = CATEGORY_HOME.get(category.slug or '', {})
        changed = False
        if seo.get('meta_description') and not (category.meta_description or '').strip():
            category.meta_description = seo['meta_description']
            changed = True
        if seo.get('meta_keywords') and not (category.meta_keywords or '').strip():
            category.meta_keywords = seo['meta_keywords']
            changed = True
        if seo.get('seo_text') and not (category.description or '').strip():
            category.description = seo['seo_text']
            changed = True
        if home.get('image') and category.image != home['image']:
            category.image = home['image']
            changed = True
        if changed:
            updated += 1
    return updated


def seed_device_model_seo_text() -> int:
    updated = 0
    for dm in DeviceModel.query.all():
        seo = generate_device_model_seo(dm)
        if seo.get('seo_text') and not (dm.seo_text or '').strip():
            dm.seo_text = seo['seo_text']
            updated += 1
    return updated


def seed_blog_posts() -> tuple[int, int]:
    created = updated = 0
    now = datetime.utcnow()
    for data in BLOG_POSTS:
        existing = BlogPost.query.filter_by(slug=data['slug']).first()
        if existing:
            changed = False
            # Не перезаписываем поля, изменённые в админке — только заполняем пустые
            if not (existing.meta_description or '').strip() and data.get('meta_description'):
                existing.meta_description = data['meta_description']
                changed = True
            if not (existing.meta_keywords or '').strip() and data.get('meta_keywords'):
                existing.meta_keywords = data['meta_keywords']
                changed = True
            if not (existing.cover_image or '').strip() and data.get('cover_image'):
                existing.cover_image = data['cover_image']
                changed = True
            if not (existing.excerpt or '').strip() and data.get('excerpt'):
                existing.excerpt = data['excerpt']
                changed = True
            if changed:
                existing.updated_at = now
                updated += 1
            continue
        post = BlogPost(
            slug=data['slug'],
            title=data['title'],
            excerpt=data['excerpt'],
            content=data['content'].strip(),
            meta_description=data['meta_description'],
            meta_keywords=data['meta_keywords'],
            cover_icon=data.get('cover_icon', 'fa-book-open'),
            cover_image=data.get('cover_image'),
            reading_minutes=data.get('reading_minutes', 5),
            is_published=True,
            created_at=now,
            updated_at=now,
        )
        db.session.add(post)
        created += 1
    return created, updated


def main() -> int:
    with app.app_context():
        slugs = seed_device_model_slugs()
        cats = seed_category_seo_text()
        models = seed_device_model_seo_text()
        legacy_removed = remove_legacy_shared_posts()
        posts_created, posts_updated = seed_blog_posts()
        db.session.commit()
        print(f'Модели: slug обновлено {slugs}, seo_text {models}')
        print(f'Категории: seo_text {cats}')
        print(f'Блог: удалено дублей {legacy_removed}, создано {posts_created}, обновлено {posts_updated}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
