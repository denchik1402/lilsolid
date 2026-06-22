"""Утилиты для оптимизированных изображений (WebP + responsive variants)."""
import os
import re

IMAGE_EXTENSIONS = frozenset({'.jpg', '.jpeg', '.png', '.gif', '.webp'})
PRODUCT_WIDTHS = (400, 800)
BANNER_WIDTHS = (400, 800, 1200)
CATEGORY_WIDTHS = (400, 800)
VARIANT_SUFFIX_RE = re.compile(r'_(\d+)w$')


def image_stem(filename):
    """Имя файла без расширения и суффикса _400w / _800w / _1200w."""
    base, _ = os.path.splitext(os.path.basename(filename))
    return VARIANT_SUFFIX_RE.sub('', base)


def is_variant_filename(filename):
    base, ext = os.path.splitext(filename)
    if ext.lower() not in IMAGE_EXTENSIONS:
        return False
    return bool(VARIANT_SUFFIX_RE.search(base))


def image_base_path(rel_filename):
    """Относительный путь без расширения: Devices/foo/bar (без _400w)."""
    dirpart = os.path.dirname(rel_filename).replace('\\', '/')
    stem = image_stem(rel_filename)
    return f'{dirpart}/{stem}' if dirpart else stem


def variant_rel_path(rel_filename, width):
    return f'{image_base_path(rel_filename)}_{width}w.webp'


def _variant_path(static_folder, folder, rel_filename, width):
    return os.path.join(static_folder, 'images', folder, variant_rel_path(rel_filename, width))


def has_image_variants(static_folder, folder, rel_filename):
    if not rel_filename:
        return False
    return os.path.isfile(_variant_path(static_folder, folder, rel_filename, 400))


def build_optimized_image(static_folder, folder, rel_filename, url_for_static):
    """Данные для шаблона: src, srcset, has_variants."""
    prefix = f'images/{folder}/'
    original_url = url_for_static(prefix + rel_filename)
    if not has_image_variants(static_folder, folder, rel_filename):
        return {
            'has_variants': False,
            'original_url': original_url,
            'src': original_url,
            'src_800': original_url,
            'srcset_webp': '',
            'srcset_fallback': '',
        }

    base = image_base_path(rel_filename)
    w400 = url_for_static(prefix + variant_rel_path(rel_filename, 400))
    w800 = url_for_static(prefix + variant_rel_path(rel_filename, 800))
    srcset_webp = f'{w400} 400w, {w800} 800w'
    srcset_fallback = srcset_webp

    w1200_path = _variant_path(static_folder, folder, rel_filename, 1200)
    if os.path.isfile(w1200_path):
        w1200 = url_for_static(prefix + variant_rel_path(rel_filename, 1200))
        srcset_webp = f'{w400} 400w, {w800} 800w, {w1200} 1200w'

    return {
        'has_variants': True,
        'original_url': original_url,
        'src': w400,
        'src_800': w800,
        'srcset_webp': srcset_webp,
        'srcset_fallback': srcset_fallback,
    }
