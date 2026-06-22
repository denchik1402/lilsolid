from extensions import db
from datetime import datetime
import re
import json

class Category(db.Model):
    """Категория товаров"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(200))
    meta_description = db.Column(db.String(300))  # SEO: meta description для страницы категории
    meta_keywords = db.Column(db.String(300))     # SEO: meta keywords
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # для lastmod в sitemap
    
    products = db.relationship('Product', backref='category', lazy=True)


class DeviceModel(db.Model):
    """Справочник моделей устройств (фильтр каталога, выбор в карточке товара)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    image_alt = db.Column(db.String(200))
    meta_description = db.Column(db.String(300))
    meta_keywords = db.Column(db.String(300))
    seo_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BlogPost(db.Model):
    """Статья блога / гайд для SEO"""
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    excerpt = db.Column(db.String(400))
    content = db.Column(db.Text, nullable=False)
    meta_description = db.Column(db.String(300))
    meta_keywords = db.Column(db.String(300))
    cover_icon = db.Column(db.String(50), default='fa-book-open')
    cover_image = db.Column(db.String(300))
    reading_minutes = db.Column(db.Integer, default=5)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BotSetting(db.Model):
    """Настройки бота (ключ-значение), в т.ч. chat_id для уведомлений"""
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text)


class TelegramUser(db.Model):
    """Пользователь Telegram с ролью (user, courier, boss, admin)"""
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False)
    username = db.Column(db.String(100))  # @username без @
    first_name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user')  # user, courier, boss, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Product(db.Model):
    """Товар"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True)
    price = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float)  # себестоимость для расчёта прибыли (из iluma.xlsx)
    old_price = db.Column(db.Float)
    description = db.Column(db.Text)
    characteristics = db.Column(db.Text)  # JSON строка с характеристиками
    image = db.Column(db.String(200))
    image_alt = db.Column(db.String(200))  # alt-текст для изображения (SEO)
    images = db.Column(db.Text)  # JSON строка с дополнительными изображениями
    in_stock = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)
    model = db.Column(db.String(50))  # One, Standart, Prime, i One, i Standart, i Prime
    color = db.Column(db.String(50))  # Black, Blue, Green и т.д.
    is_exclusive = db.Column(db.Boolean, default=False)
    is_hit = db.Column(db.Boolean, default=False)
    meta_description = db.Column(db.String(300))  # SEO: meta description для страницы товара
    meta_keywords = db.Column(db.String(300))     # SEO: meta keywords
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # для lastmod в sitemap
    
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    reviews = db.relationship('Review', backref='product', lazy=True, cascade='all, delete-orphan')

    def get_characteristics(self):
        """Извлекает характеристики из description в виде списка (ключ, значение)"""
        if not self.description:
            return []
        # Форматы: <b>Key:</b> value или • <b>Key</b>: value (двоеточие может быть внутри или снаружи тега)
        pattern = r'[•]?\s*<b>([^<]+)</b>\s*:?\s*([^<\n]+)'
        matches = re.findall(pattern, self.description)
        result = []
        for k, v in matches:
            k = k.strip().rstrip(':').strip()
            if k and k.lower() != 'характеристики':
                result.append((k, v.strip()))
        return result

    def get_intro_text(self):
        """Извлекает вступительный текст до блока характеристик (с сохранением HTML)"""
        if not self.description:
            return ''
        # Берём текст до первого <b>Key:</b> или <b>Характеристики</b> или •
        match = re.search(r'^(.+?)(?=<b>[^<]+</b>\s*:|<b>Характеристики</b>|^\s*[•])', self.description, re.DOTALL | re.MULTILINE | re.IGNORECASE)
        intro = match.group(1).strip() if match else ''
        if not intro:
            # Fallback: первая строка/абзац до двойного переноса
            parts = re.split(r'\n\s*\n', self.description, 1)
            intro = parts[0].strip() if parts else ''
        return intro

    @property
    def all_images(self):
        """Список изображений для галереи: без дубликатов и без _400w/_800w вариантов."""
        from image_utils import image_base_path, is_variant_filename

        result = []
        seen = set()

        def add_path(path):
            if not path or not isinstance(path, str):
                return
            path = path.strip()
            if not path or is_variant_filename(path):
                return
            key = image_base_path(path)
            if key in seen:
                return
            seen.add(key)
            result.append(path)

        if self.image:
            add_path(self.image)
        if self.images:
            try:
                extra = json.loads(self.images)
                if isinstance(extra, list):
                    for item in extra:
                        add_path(item)
                elif isinstance(extra, str):
                    add_path(extra)
            except (json.JSONDecodeError, TypeError):
                pass
        return result

    def get_url_slug(self):
        """Slug для ЧПУ URL. Генерирует из name, если slug пуст."""
        if self.slug:
            return self.slug
        s = re.sub(r'[^\w\s-]', '', self.name.lower())
        s = re.sub(r'[-\s]+', '-', s).strip('-')[:180]
        return s or str(self.id)

class Review(db.Model):
    """Отзыв (status: pending=на модерации, approved=опубликован, rejected=отклонён)"""
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    text = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

class Order(db.Model):
    """Заказ"""
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_email = db.Column(db.String(100))
    delivery_address = db.Column(db.Text)
    delivery_method = db.Column(db.String(50))
    payment_method = db.Column(db.String(50))
    comment = db.Column(db.Text)
    status = db.Column(db.String(50), default='new')  # new, processing, completed, cancelled
    courier_telegram_id = db.Column(db.BigInteger)  # ID курьера в Telegram, взявшего заказ
    total_amount = db.Column(db.Float, nullable=False)
    promo_code = db.Column(db.String(50))  # применённый промокод
    discount_amount = db.Column(db.Float, default=0)  # сумма скидки
    idempotency_key = db.Column(db.String(64), unique=True, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generate_order_number()
    
    def generate_order_number(self):
        """Генерация номера заказа"""
        import random
        import string
        self.order_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

class OrderItem(db.Model):
    """Позиция заказа"""
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    product = db.relationship('Product')


class PromoCode(db.Model):
    """Промокод (управление только админом)"""
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)  # например SALE10
    discount_type = db.Column(db.String(20), nullable=False)  # percent | fixed
    discount_value = db.Column(db.Float, nullable=False)  # 10 для 10% или 500 для 500₽
    min_order = db.Column(db.Float, default=0)  # мин. сумма заказа
    max_uses = db.Column(db.Integer, default=None)  # None = без лимита
    used_count = db.Column(db.Integer, default=0)
    valid_from = db.Column(db.DateTime, default=None)
    valid_until = db.Column(db.DateTime, default=None)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_valid(self):
        from datetime import datetime as dt
        if not self.is_active:
            return False
        if self.max_uses is not None and self.used_count >= self.max_uses:
            return False
        now = dt.utcnow()
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        return True

    def apply_discount(self, subtotal):
        """Возвращает (скидка, итого)"""
        if subtotal < self.min_order:
            return 0, subtotal
        if self.discount_type == 'percent':
            discount = subtotal * (self.discount_value / 100)
        else:
            discount = min(self.discount_value, subtotal)
        return discount, max(0, subtotal - discount)


class Banner(db.Model):
    """Баннер главной карусели (фото, текст, кнопка)"""
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(300))  # цена или подзаголовок
    button_text = db.Column(db.String(50), default='Купить сейчас')
    button_url = db.Column(db.String(500))  # /product/123 или /catalog
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))  # если задан — кнопка ведёт на товар
    badge_type = db.Column(db.String(20))  # telegram, promo, bonus, hit — бейдж на баннере
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # A/B-тестирование и статистика
    impressions = db.Column(db.Integer, default=0)  # показы
    clicks = db.Column(db.Integer, default=0)  # клики
    ab_test_group = db.Column(db.String(50))  # A/B: баннеры с одинаковой группой — варианты (A vs B)

    product = db.relationship('Product')

    @property
    def ctr(self):
        """CTR в процентах"""
        imp = self.impressions or 0
        if imp <= 0:
            return 0
        return round(100 * (self.clicks or 0) / imp, 2)


class HomeBlock(db.Model):
    """Блок секции «Премиальные устройства» (3 блока: фото, заголовок, текст, кнопка)"""
    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.Integer, nullable=False)  # 1=левый большой, 2=правый верх, 3=правый низ
    image = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    button_text = db.Column(db.String(50))
    button_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)