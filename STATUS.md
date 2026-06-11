# Статус реализации

## ✅ Реализовано

### Безопасность и инфраструктура
- **Поиск** — параметризованные запросы, `_escape_like()` для защиты от SQL-инъекций
- **SECRET_KEY** — из env или config.py (не в коде)
- **Страницы 404 и 500** — `templates/errors/404.html`, `500.html`
- **PWA** — manifest.json, Service Worker (sw.js), theme-color
- **Тесты** — pytest в `tests/test_routes.py`, `tests/test_api.py`

### Админка
- Редактирование meta (description, keywords) для товаров
- Массовые операции (категория, цена, скидка, наличие, удаление)
- Экспорт заказов (Excel, CSV)
- Редактирование meta и описаний категорий

### SEO
- ЧПУ для товаров (`/product/slug`)
- lastmod в sitemap (updated_at)
- Уникальные meta для категорий + админка
- Product Schema: oldPrice, image[]
- Preconnect к CDN
- Canonical, rel prev/next для каталога
- noindex для корзины, оформления, избранного, отслеживания
- Alt-тексты для баннеров и блоков
- FAQPage Schema, Twitter Card
- defer для скриптов
- Описания категорий в админке
- «Популярные запросы» на странице поиска

---

## ⏳ В работе / осталось

- **Поле alt в админке** — для изображений товаров
- **WebP, srcset** — оптимизация изображений
- **Nginx** — gzip, Cache-Control (пример в deploy/)
- **Ручные действия** — Search Console, Вебмастер, PageSpeed
