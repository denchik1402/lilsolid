#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram-бот магазина LIL STORE.
Роли: user, courier, boss, admin.
Полное управление через inline-кнопки.
"""
import os
import sys
import re
import logging
from pathlib import Path

# Корень проекта (my_shop) — для app, models, config
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))
# TG — для telegram_notify, bot_utils
sys.path.insert(0, str(Path(__file__).resolve().parent))

def _config_exists():
    return (_PROJECT_ROOT / 'config.py').exists()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
    from telegram.ext import (
        Application, CommandHandler, CallbackQueryHandler, MessageHandler,
        ContextTypes, filters
    )
    from telegram.error import BadRequest, TimedOut
except ImportError:
    print("Установите: pip install python-telegram-bot")
    sys.exit(1)

# Конфигурация
def get_config():
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    admin_ids = os.environ.get('TELEGRAM_ADMIN_IDS', '')
    default_admin = os.environ.get('TELEGRAM_DEFAULT_ADMIN', 'denchik1402')
    if not token and _config_exists():
        try:
            import config
            token = getattr(config, 'TELEGRAM_BOT_TOKEN', None)
            chat_id = getattr(config, 'TELEGRAM_CHAT_ID', None)
            admin_ids = getattr(config, 'TELEGRAM_ADMIN_IDS', admin_ids)
            default_admin = getattr(config, 'TELEGRAM_DEFAULT_ADMIN', default_admin)
        except ImportError:
            pass
    admin_set = set()
    if admin_ids:
        for x in str(admin_ids).replace(',', ' ').split():
            try:
                admin_set.add(int(x.strip()))
            except ValueError:
                pass
    if not admin_set and chat_id:
        try:
            admin_set.add(int(chat_id))
        except ValueError:
            pass
    return token, chat_id, admin_set, default_admin


def get_site_url() -> str:
    """URL сайта для Web App (должен быть HTTPS)."""
    url = os.environ.get('SITE_URL')
    if not url and _config_exists():
        try:
            import config
            url = getattr(config, 'SITE_URL', None) or getattr(config, 'WEBAPP_URL', None)
        except ImportError:
            pass
    return (url or '').rstrip('/')


def get_product_image_url(filename: str) -> str:
    """Полный URL изображения товара (для Telegram нужен публичный URL)."""
    base = get_site_url()
    if not base or base.startswith('http://127.0.0.1') or base.startswith('http://localhost'):
        return None  # Telegram не загрузит с localhost
    return f"{base}/static/images/products/{filename}"


def get_db():
    import app as app_module
    from models import Product, Category, Review, Order, OrderItem, TelegramUser, BotSetting, PromoCode
    return app_module.app, app_module.db, Product, Category, Review, Order, OrderItem, TelegramUser, BotSetting, PromoCode


def get_or_create_user(telegram_id: int, username: str = None, first_name: str = None):
    """Получить или создать пользователя, @denchik1402 = admin по умолчанию"""
    app, db, *models = get_db()
    TelegramUser = models[-3]  # [-3]=TelegramUser, [-2]=BotSetting, [-1]=PromoCode
    _, _, _, default_admin = get_config()
    with app.app_context():
        user = TelegramUser.query.filter_by(telegram_id=telegram_id).first()
        if not user:
            role = 'admin' if (username and username.lower() == default_admin.lower()) else 'user'
            user = TelegramUser(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                role=role
            )
            db.session.add(user)
            db.session.commit()
        elif user.username != username or user.first_name != first_name:
            user.username = username
            user.first_name = first_name
            db.session.commit()
        return user


def get_user_role(telegram_id: int) -> str:
    app, db, *models = get_db()
    TelegramUser = models[-3]  # [-3]=TelegramUser, [-2]=BotSetting, [-1]=PromoCode
    with app.app_context():
        user = TelegramUser.query.filter_by(telegram_id=telegram_id).first()
        return user.role if user else 'user'


def role_can_access(role: str, menu: str) -> bool:
    """menu: user, courier, boss, admin"""
    hierarchy = {'user': 0, 'courier': 1, 'boss': 2, 'admin': 3}
    return hierarchy.get(role, 0) >= hierarchy.get(menu, 0)


# ==================== ГЛАВНОЕ МЕНЮ ====================

def _build_main_menu_keyboard(role: str) -> InlineKeyboardMarkup:
    """Собирает клавиатуру главного меню по роли."""
    keyboard = [
        [
            InlineKeyboardButton("🛒 Каталог", callback_data="menu_catalog"),
            InlineKeyboardButton("🛍 Корзина", callback_data="menu_cart"),
        ],
        [InlineKeyboardButton("💬 Задать вопрос", callback_data="menu_ask_question")],
    ]
    site_url = get_site_url()
    if site_url.startswith('https://'):
        keyboard.append([InlineKeyboardButton("🚀 Запустить приложение", web_app=WebAppInfo(url=site_url))])
    if role_can_access(role, 'courier'):
        keyboard.append([InlineKeyboardButton("🚚 Курьер — Заказы", callback_data="menu_courier_orders")])
        keyboard.append([InlineKeyboardButton("❓ Как отвечать на вопросы", callback_data="menu_support_help")])
    if role_can_access(role, 'boss'):
        keyboard.append([InlineKeyboardButton("👔 Boss — Меню", callback_data="menu_boss")])
    if role_can_access(role, 'admin'):
        keyboard.append([InlineKeyboardButton("⚙️ Admin — Назначения", callback_data="menu_admin")])
        keyboard.append([InlineKeyboardButton("🎟 Промокоды", callback_data="menu_admin_promo")])
    return InlineKeyboardMarkup(keyboard)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start — главное меню по роли"""
    await _maybe_save_notification_chat(update)
    user = update.effective_user
    if not user:
        return
    telegram_id = user.id
    username = (user.username or '').strip()
    first_name = user.first_name or 'друг'

    get_or_create_user(telegram_id, username, first_name)
    role = get_user_role(telegram_id)

    # Сбрасываем состояние оформления заказа
    if context.user_data:
        context.user_data.pop('awaiting_checkout', None)
        context.user_data.pop('checkout_data', None)

    text = (
        f"👋 Привет, {first_name}!\n\n"
        "🛍 Я бот магазина <b>LIL STORE</b>.\n"
        "Выбери раздел ниже:"
    )
    reply_markup = _build_main_menu_keyboard(role)
    msg = update.effective_message
    if msg:
        await msg.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')


# ==================== USER: КАТАЛОГ ====================

def _catalog_nav_keyboard(in_products_view: bool = False) -> list:
    """Корзина и оформление — над кнопкой «Назад»."""
    rows = [[
        InlineKeyboardButton("🛍 Корзина", callback_data="menu_cart"),
        InlineKeyboardButton("📦 Оформить заказ", callback_data="menu_checkout"),
    ]]
    back_cb = "menu_catalog" if in_products_view else "menu_main"
    rows.append([InlineKeyboardButton("◀️ Назад", callback_data=back_cb)])
    return rows


async def show_product_detail(query, context, product_id: int):
    """Показывает товар с фото и описанием."""
    app, db, Product, Category, Review, Order, OrderItem, TelegramUser, *_ = get_db()
    with app.app_context():
        p = Product.query.get(product_id)
        if not p:
            await _safe_edit_message(query, "Товар не найден.")
            return
        intro = (p.get_intro_text() or "")[:500]
        if intro:
            import re
            intro = re.sub(r'<[^>]+>', '', intro)  # убрать HTML для Telegram
        caption = f"<b>{p.name}</b>\n\n{p.price:,.0f} ₽".replace(",", " ")
        if intro:
            caption += f"\n\n{intro}"
        img = p.all_images[0] if p.all_images else p.image
        url = get_product_image_url(img) if img else None
        chat_id = query.message.chat_id
        photo_source = None
        if img:
            if url:
                photo_source = url
            else:
                local_path = _PROJECT_ROOT / 'static' / 'images' / 'products' / img
                if local_path.exists():
                    photo_source = open(local_path, 'rb')
        try:
            if photo_source:
                await context.bot.send_photo(chat_id=chat_id, photo=photo_source, caption=caption, parse_mode='HTML')
            else:
                await context.bot.send_message(chat_id=chat_id, text=caption, parse_mode='HTML')
        except Exception as e:
            logger.warning("Не удалось отправить фото товара %s: %s", product_id, e)
            await context.bot.send_message(chat_id=chat_id, text=caption, parse_mode='HTML')
        finally:
            if hasattr(photo_source, 'close'):
                photo_source.close()


async def show_catalog(update_or_query, context, is_callback: bool, category_id=None, show_all: bool = False):
    app, db, Product, Category, Review, Order, OrderItem, TelegramUser, *_ = get_db()
    if is_callback:
        obj = update_or_query
        user_id = obj.from_user.id if obj.from_user else 0
        async def send(t, kb=None):
            await _safe_edit_message(obj, t, kb)
    else:
        obj = update_or_query
        user_id = obj.effective_user.id if obj.effective_user else 0
        async def send(t, kb=None):
            await obj.message.reply_text(t, reply_markup=kb, parse_mode='HTML')

    context.user_data['last_catalog_category'] = category_id
    context.user_data['last_catalog_show_all'] = show_all
    cart = get_cart(context, user_id)
    cart_count = sum(cart.values()) if cart else 0

    with app.app_context():
        categories = Category.query.order_by(Category.name).all()

        if category_id is None and not show_all:
            cart_line = f"\n\n🛒 В корзине: {cart_count} шт." if cart_count else ""
            if categories:
                text = f"🛒 <b>Каталог</b>{cart_line}\n\nВыберите категорию:"
                keyboard = [[InlineKeyboardButton(f"📁 {c.name}", callback_data=f"cat_{c.id}")] for c in categories]
                keyboard.append([InlineKeyboardButton("📋 Все товары", callback_data="cat_all")])
            else:
                text = f"🛒 <b>Каталог</b>{cart_line}\n\nКатегории пока не добавлены."
                keyboard = []
            keyboard.extend(_catalog_nav_keyboard(in_products_view=False))
            await send(text, InlineKeyboardMarkup(keyboard))
            return

        if show_all:
            cat = None
            products = Product.query.filter_by(in_stock=True).order_by(Product.name).all()
            header = " — Все товары"
        else:
            cat = Category.query.get(category_id)
            products = (
                Product.query.filter_by(category_id=category_id, in_stock=True).order_by(Product.name).all()
                if cat else []
            )
            header = f" — {cat.name}" if cat else ""

        cart_line = f" | В корзине: {cart_count}" if cart_count else ""
        keyboard = []
        if not products:
            text = f"🛒 <b>Каталог</b>{header}{cart_line}\n\nВ этой категории пока нет товаров."
        else:
            text = f"🛒 <b>Каталог</b>{header}{cart_line}\n\n"
            for p in products[:15]:
                in_cart = cart.get(str(p.id), 0)
                qty_str = f" (×{in_cart})" if in_cart else ""
                text += f"• <b>{p.name}</b> — {p.price:,.0f} ₽{qty_str}\n".replace(",", " ")
                keyboard.append([
                    InlineKeyboardButton(f"➕ {p.name[:25]}", callback_data=f"add_{p.id}"),
                    InlineKeyboardButton("📷", callback_data=f"detail_{p.id}"),
                ])
            if len(products) > 15:
                text += f"\n<i>Показаны первые 15 из {len(products)}</i>"

        keyboard.extend(_catalog_nav_keyboard(in_products_view=True))
        await send(text, InlineKeyboardMarkup(keyboard))


# ==================== USER: КОРЗИНА ====================

def get_cart(context, user_id: int) -> dict:
    if 'carts' not in context.bot_data:
        context.bot_data['carts'] = {}
    return context.bot_data['carts'].setdefault(user_id, {})


async def show_cart(update_or_query, context, is_callback: bool):
    app, db, Product, Category, Review, Order, OrderItem, TelegramUser, *_ = get_db()
    if is_callback:
        obj = update_or_query
        user_id = obj.from_user.id if obj.from_user else 0
        async def send(t, kb=None):
            await _safe_edit_message(obj, t, kb)
    else:
        obj = update_or_query
        user_id = obj.effective_user.id if obj.effective_user else 0
        async def send(t, kb=None):
            await obj.message.reply_text(t, reply_markup=kb, parse_mode='HTML')

    cart = get_cart(context, user_id)
    if not cart:
        text = "🛍 Корзина пуста. Загляни в каталог! 😊"
        keyboard = [[InlineKeyboardButton("🛒 Каталог", callback_data="menu_catalog")], [InlineKeyboardButton("◀️ Назад", callback_data="menu_main")]]
        await send(text, InlineKeyboardMarkup(keyboard))
        return

    with app.app_context():
        total = 0
        lines = ["🛍 <b>Корзина</b>\n"]
        keyboard = []
        for pid, qty in cart.items():
            p = Product.query.get(int(pid))
            if p:
                sub = p.price * qty
                total += sub
                lines.append(f"• {p.name[:40]} × {qty} — {sub:,.0f} ₽".replace(",", " "))
                keyboard.append([
                    InlineKeyboardButton(f"➖ {p.name[:20]}", callback_data=f"cart_minus_{pid}"),
                    InlineKeyboardButton(f"➕", callback_data=f"cart_plus_{pid}")
                ])
        lines.append(f"\n💰 <b>Итого: {total:,.0f} ₽</b>".replace(",", " "))
        keyboard.append([InlineKeyboardButton("📦 Оформить заказ", callback_data="menu_checkout")])
        keyboard.append([InlineKeyboardButton("🗑 Очистить", callback_data="cart_clear")])
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="menu_main")])
        await send("\n".join(lines), InlineKeyboardMarkup(keyboard))


# ==================== USER: ОФОРМЛЕНИЕ ЗАКАЗА ====================

async def start_checkout(update_or_query, context, is_callback: bool):
    app, db, Product, Category, Review, Order, OrderItem, TelegramUser, *_ = get_db()
    if is_callback:
        obj = update_or_query
        user_id = obj.from_user.id if obj.from_user else 0
        send = lambda t: obj.edit_message_text(t, parse_mode='HTML')
    else:
        obj = update_or_query
        user_id = obj.effective_user.id if obj.effective_user else 0
        send = lambda t: obj.message.reply_text(t, parse_mode='HTML')

    cart = get_cart(context, user_id)
    if not cart:
        await send("🛍 Корзина пуста! Добавь товары из каталога.")
        return

    context.user_data['awaiting_checkout'] = True
    text = (
        "📦 <b>Оформление заказа</b>\n\n"
        "Отправь сообщение в формате:\n"
        "<code>Имя: Иванов Иван</code>\n"
        "<code>Телефон: +7 999 123-45-67</code>\n"
        "<code>Адрес: г. Москва, ул. Примерная, д. 1</code>\n"
        "<code>Промокод: PROMO10</code> (опционально)\n\n"
        "Можно одной строкой или с переносами."
    )
    await send(text)


async def handle_checkout_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('awaiting_checkout'):
        return
    text = (update.message.text or '').strip()
    # Парсим имя, телефон, адрес, промокод
    name = re.search(r'[Ии]мя[:\s]+([^\n]+)', text, re.I) or re.search(r'[Nn]ame[:\s]+([^\n]+)', text)
    phone = re.search(r'[Тт]елефон[:\s]+([^\n]+)', text, re.I) or re.search(r'[Pp]hone[:\s]+([^\n]+)', text) or re.search(r'\+?[\d\s\-\(\)]{10,}', text)
    addr = re.search(r'[Аа]дрес[:\s]+([^\n]+)', text, re.I) or re.search(r'[Aa]ddress[:\s]+([^\n]+)', text)
    promo_match = re.search(r'[Пп]ромокод[:\s]+([A-Za-z0-9_-]+)', text, re.I)
    promo_code = (promo_match.group(1).strip().upper() if promo_match else '') or None

    name = (name.group(1).strip() if name else '').strip() or (text.split('\n')[0] if '\n' in text else text[:50])
    phone = (phone.group(1).strip() if phone and phone.lastindex else (phone.group(0) if phone else '')).strip().replace(' ', '')
    addr = (addr.group(1).strip() if addr else '').strip()

    if not name or not phone:
        await update.message.reply_text("❌ Укажи имя и телефон. Попробуй ещё раз.")
        return
    if not addr:
        addr = "Уточнить при доставке"

    user_id = update.effective_user.id
    cart = get_cart(context, user_id)
    if not cart:
        context.user_data.pop('awaiting_checkout', None)
        await update.message.reply_text("🛍 Корзина пуста. Добавь товары и попробуй снова.")
        return

    app, db, Product, Category, Review, Order, OrderItem, TelegramUser, BotSetting, PromoCode = get_db()
    with app.app_context():
        subtotal = 0
        for pid, qty in cart.items():
            p = Product.query.get(int(pid))
            if p:
                subtotal += p.price * qty
        discount, total = 0, subtotal
        applied_promo = None
        if promo_code:
            promo = PromoCode.query.filter_by(code=promo_code).first()
            if promo and promo.is_valid():
                discount, total = promo.apply_discount(subtotal)
                if discount > 0:
                    applied_promo = promo_code
                    promo.used_count += 1
        order = Order(
            customer_name=name,
            customer_phone=phone,
            customer_email='',
            delivery_address=addr,
            delivery_method='Самовывоз',
            payment_method='При получении',
            comment='',
            total_amount=total,
            promo_code=applied_promo,
            discount_amount=discount
        )
        db.session.add(order)
        db.session.flush()
        for pid, qty in cart.items():
            p = Product.query.get(int(pid))
            if p:
                db.session.add(OrderItem(order_id=order.id, product_id=p.id, quantity=qty, price=p.price))
        db.session.commit()

        try:
            from telegram_notify import send_order_to_telegram
            send_order_to_telegram(order)
        except Exception as e:
            logger.info(f"Notify: {e}")

    context.bot_data.setdefault('carts', {})[user_id] = {}
    context.user_data.pop('awaiting_checkout', None)

    msg = (
        f"✅ <b>Заказ оформлен!</b>\n\n"
        f"📋 Номер: <code>{order.order_number}</code>\n"
        f"💰 Сумма: {total:,.0f} ₽"
    )
    if discount > 0:
        msg += f"\n🎟 Скидка: {discount:,.0f} ₽ (промокод {applied_promo})"
    msg += "\n\nСпасибо за покупку! 😊"
    await update.message.reply_text(msg, parse_mode='HTML')


# ==================== COURIER: ЗАКАЗЫ ====================

PAGE_SIZE = 5


async def show_courier_orders(update_or_query, context, is_callback: bool, page=0, show_my_only=None):
    """show_my_only: None = все, 'my' = только мои заказы"""
    app, db, Product, Category, Review, Order, OrderItem, TelegramUser, *_ = get_db()
    if is_callback:
        obj = update_or_query
        user_id = obj.from_user.id if obj.from_user else 0
        async def send(t, kb=None):
            await _safe_edit_message(obj, t, kb)
    else:
        obj = update_or_query
        user_id = obj.effective_user.id if obj.effective_user else 0
        async def send(t, kb=None):
            await obj.message.reply_text(t, reply_markup=kb, parse_mode='HTML')

    role = get_user_role(user_id)
    if not role_can_access(role, 'courier'):
        await send("⛔ Нет доступа. Роль «Курьер» назначает администратор в разделе Admin → Назначения.")
        return

    with app.app_context():
        q = Order.query.filter(Order.status.in_(['new', 'processing']))
        if show_my_only == 'my':
            q = q.filter(Order.courier_telegram_id == user_id)
        orders = q.order_by(Order.created_at.desc()).all()
        total = len(orders)
        start = page * PAGE_SIZE
        page_orders = orders[start:start + PAGE_SIZE]
        em = {"new": "🆕", "processing": "⏳", "completed": "✅", "cancelled": "❌"}
        from bot_utils import format_order_items_brief, format_price

        total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        text = f"🚚 <b>Заказы курьера</b> (стр. {page + 1}/{total_pages})\n"
        text += f"Всего: {total}\n\n"

        if not page_orders:
            text += "Нет заказов." if show_my_only == 'my' else "Нет заказов со статусом «новый» или «в работе»."
        else:
            for idx, o in enumerate(page_orders):
                num = start + idx + 1
                e = em.get(o.status, "•")
                is_mine = o.courier_telegram_id == user_id
                text += f"{e} <b>{num}. Заказ: {o.order_number}</b>" + (" (мой)" if is_mine else "") + "\n"
                text += f"   {o.customer_name} | {o.customer_phone or '—'}\n"
                text += f"   📍 {o.delivery_address or '—'}\n"
                for item_line in format_order_items_brief(o.items):
                    text += f"   📦 {item_line}\n"
                text += f"   💰 Итого: {format_price(o.total_amount)} ₽\n\n"

        raw_route = context.user_data.get('courier_route_orders') or set()
        route_ids = set(str(x) for x in raw_route) if raw_route else set()
        keyboard = []
        for idx, o in enumerate(page_orders):
            num = start + idx + 1
            row = [InlineKeyboardButton(str(num), callback_data="noop")]
            if o.courier_telegram_id != user_id:
                row.append(InlineKeyboardButton("📌 Взять", callback_data=f"courier_take_{o.id}"))
            in_route = str(o.id) in route_ids
            row.append(InlineKeyboardButton("➖ Из маршрута" if in_route else "➕ В маршрут", callback_data=f"courier_route_{'del' if in_route else 'add'}_{o.id}"))
            row.append(InlineKeyboardButton("✅ Выполнен", callback_data=f"complete_{o.id}"))
            row.append(InlineKeyboardButton("❌ Отказался", callback_data=f"courier_cancel_{o.id}"))
            keyboard.append(row)
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton("◀️", callback_data=f"courier_page_{page - 1}_{show_my_only or ''}"))
        if start + PAGE_SIZE < total:
            nav.append(InlineKeyboardButton("▶️", callback_data=f"courier_page_{page + 1}_{show_my_only or ''}"))
        keyboard.append(nav)
        filter_btn = InlineKeyboardButton("📋 Мои", callback_data="courier_page_0_my") if show_my_only != 'my' else InlineKeyboardButton("📋 Все", callback_data="courier_page_0")
        route_count = len(route_ids)
        route_btn = InlineKeyboardButton(f"🗺 Маршрут ({route_count})" if route_count else "🗺 Маршрут", callback_data="courier_route")
        keyboard.append([
            route_btn,
            filter_btn,
            InlineKeyboardButton("🔄 Обновить", callback_data="menu_courier_orders"),
        ])
        keyboard.append([InlineKeyboardButton("◀️ В меню", callback_data="menu_main")])
        await send(text, InlineKeyboardMarkup(keyboard))


# ==================== BOSS: МЕНЮ ====================

async def show_boss_menu(update_or_query, is_callback: bool):
    if is_callback:
        obj = update_or_query
        user_id = obj.from_user.id if obj.from_user else 0
        send = lambda t, kb=None: obj.edit_message_text(t, reply_markup=kb, parse_mode='HTML')
    else:
        obj = update_or_query
        user_id = obj.effective_user.id if obj.effective_user else 0
        send = lambda t, kb=None: obj.message.reply_text(t, reply_markup=kb, parse_mode='HTML')

    role = get_user_role(user_id)
    if not role_can_access(role, 'boss'):
        await send("⛔ Нет доступа.")
        return

    keyboard = [
        [InlineKeyboardButton("🛠 Управление сайтом", callback_data="boss_site")],
        [InlineKeyboardButton("📦 Заказы", callback_data="boss_orders_0")],
        [InlineKeyboardButton("📊 Статистика", callback_data="boss_stats")],
        [InlineKeyboardButton("💰 Прибыль за период", callback_data="boss_profit")],
        [InlineKeyboardButton("💬 Отзывы на модерации", callback_data="boss_reviews")],
        [InlineKeyboardButton("❓ Как отвечать на вопросы", callback_data="menu_support_help")],
        [InlineKeyboardButton("◀️ Назад", callback_data="menu_main")],
    ]
    await send("👔 <b>Boss — Меню</b>\n\nВыбери раздел:", InlineKeyboardMarkup(keyboard))


# ==================== BOSS: УПРАВЛЕНИЕ САЙТОМ ====================

async def show_boss_site(update_or_query, is_callback: bool):
    app, db, Product, Category, Review, Order, OrderItem, TelegramUser, *_ = get_db()
    if is_callback:
        obj = update_or_query
        send = lambda t, kb=None: obj.edit_message_text(t, reply_markup=kb, parse_mode='HTML')
    else:
        obj = update_or_query
        send = lambda t, kb=None: obj.message.reply_text(t, reply_markup=kb, parse_mode='HTML')

    admin_url = ""
    try:
        import config
        key = getattr(config, 'ADMIN_SECRET', '')
        base = getattr(config, 'SITE_URL', None) or os.environ.get('SITE_URL', 'http://127.0.0.1:5000')
        admin_url = f"{base}/admin/products?key={key}" if key else ""
    except Exception:
        pass

    with app.app_context():
        products = Product.query.limit(20).all()
        keyboard = []
        for p in products:
            keyboard.append([InlineKeyboardButton(f"✏️ {p.name[:35]} — {p.price:,.0f} ₽".replace(",", " "), callback_data=f"boss_edit_{p.id}")])
        keyboard.append([InlineKeyboardButton("➕ Добавить товар", callback_data="boss_add_product")])
        if admin_url:
            keyboard.append([InlineKeyboardButton("🌐 Открыть админку на сайте", url=admin_url)])
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="menu_boss")])
        text = "🛠 <b>Управление товарами</b>\n\nВыбери товар или открой админку на сайте для добавления и редактирования:"
        await send(text, InlineKeyboardMarkup(keyboard))


# ==================== BOSS: ЗАКАЗЫ С ПАГИНАЦИЕЙ ====================

async def show_boss_orders(update_or_query, is_callback: bool, page=0):
    app, db, Product, Category, Review, Order, OrderItem, TelegramUser, *_ = get_db()
    if is_callback:
        obj = update_or_query
        user_id = obj.from_user.id if obj.from_user else 0
        send = lambda t, kb=None: obj.edit_message_text(t, reply_markup=kb, parse_mode='HTML')
    else:
        obj = update_or_query
        user_id = obj.effective_user.id if obj.effective_user else 0
        send = lambda t, kb=None: obj.message.reply_text(t, reply_markup=kb, parse_mode='HTML')

    role = get_user_role(user_id)
    if not role_can_access(role, 'boss'):
        await send("⛔ Нет доступа.")
        return

    with app.app_context():
        orders = Order.query.order_by(Order.created_at.desc()).all()
        total = len(orders)
        start = page * PAGE_SIZE
        page_orders = orders[start:start + PAGE_SIZE]
        em = {"new": "🆕", "processing": "⏳", "completed": "✅", "cancelled": "❌"}

        text = f"📦 <b>Заказы</b> (стр. {page + 1}/{(total + PAGE_SIZE - 1) // PAGE_SIZE or 1})\n\n"
        for o in page_orders:
            e = em.get(o.status, "•")
            items_str = ", ".join([f"{i.product.name[:20] if i.product else '?'}×{i.quantity}" for i in o.items[:3]])
            courier_info = ""
            if o.courier_telegram_id:
                cu = TelegramUser.query.filter_by(telegram_id=o.courier_telegram_id).first()
                courier_info = f" | 🚚 {cu.first_name or cu.username or cu.telegram_id}" if cu else f" | 🚚 ID:{o.courier_telegram_id}"
            else:
                courier_info = " | ⚠️ без курьера"
            text += f"{e} <code>{o.order_number}</code> — {o.customer_name} — {o.total_amount:,.0f} ₽{courier_info}\n   {items_str}\n\n".replace(",", " ")

        keyboard = []
        for o in page_orders:
            if o.status not in ('completed', 'cancelled'):
                keyboard.append([
                    InlineKeyboardButton("✅ Выполнен", callback_data=f"boss_complete_{o.id}"),
                    InlineKeyboardButton("❌ Отказался", callback_data=f"boss_cancel_{o.id}")
                ])
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton("◀️", callback_data=f"boss_orders_{page - 1}"))
        nav.append(InlineKeyboardButton(f"{page + 1}/{(total + PAGE_SIZE - 1) // PAGE_SIZE or 1}", callback_data="noop"))
        if start + PAGE_SIZE < total:
            nav.append(InlineKeyboardButton("▶️", callback_data=f"boss_orders_{page + 1}"))
        keyboard.append(nav)
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="menu_boss")])
        await send(text, InlineKeyboardMarkup(keyboard))


# ==================== BOSS: СТАТИСТИКА ====================

async def show_boss_stats(update_or_query, is_callback: bool):
    app, db, Product, Category, Review, Order, OrderItem, TelegramUser, *_ = get_db()
    if is_callback:
        obj = update_or_query
        user_id = obj.from_user.id if obj.from_user else 0
        send = lambda t, kb=None: obj.edit_message_text(t, reply_markup=kb, parse_mode='HTML')
    else:
        obj = update_or_query
        user_id = obj.effective_user.id if obj.effective_user else 0
        send = lambda t, kb=None: obj.message.reply_text(t, reply_markup=kb, parse_mode='HTML')

    role = get_user_role(user_id)
    if not role_can_access(role, 'boss'):
        await send("⛔ Нет доступа.")
        return

    with app.app_context():
        total_orders = Order.query.count()
        new_orders = Order.query.filter_by(status='new').count()
        completed = Order.query.filter_by(status='completed').count()
        total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter(Order.status != 'cancelled').scalar() or 0
        pending_reviews = Review.query.filter_by(status='pending').count()
        products_count = Product.query.count()

        text = (
            "📊 <b>Статистика</b>\n\n"
            f"📦 Заказов всего: {total_orders}\n"
            f"🆕 Новых: {new_orders}\n"
            f"✅ Выполнено: {completed}\n"
            f"💰 Выручка: {total_revenue:,.0f} ₽\n".replace(",", " ") +
            f"💬 На модерации: {pending_reviews}\n"
            f"🛍 Товаров: {products_count}"
        )
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="menu_boss")]]
        await send(text, InlineKeyboardMarkup(keyboard))


# ==================== BOSS: ПРИБЫЛЬ ====================

async def show_boss_profit(update_or_query, is_callback: bool):
    app, db, Product, Category, Review, Order, OrderItem, TelegramUser, *_ = get_db()
    if is_callback:
        obj = update_or_query
        send = lambda t, kb=None: obj.edit_message_text(t, reply_markup=kb, parse_mode='HTML')
    else:
        obj = update_or_query
        send = lambda t, kb=None: obj.message.reply_text(t, reply_markup=kb, parse_mode='HTML')

    with app.app_context():
        from bot_utils import calc_profit_for_orders, format_price
        orders = Order.query.filter(Order.status.in_(['new', 'processing', 'completed'])).all()
        profit, revenue, cost = calc_profit_for_orders(orders)

        text = (
            "💰 <b>Прибыль</b> (по заказам, кроме отменённых)\n\n"
            f"📈 Выручка: {format_price(revenue)} ₽\n"
            f"📉 Себестоимость: {format_price(cost)} ₽\n"
            f"✅ <b>Прибыль: {format_price(profit)} ₽</b>\n\n"
            "💡 Цены и себестоимость — из каталога на сайте."
        )
        keyboard = [
            [InlineKeyboardButton("📅 Выбрать период", callback_data="boss_profit_period")],
            [InlineKeyboardButton("◀️ Назад", callback_data="menu_boss")],
        ]
        await send(text, InlineKeyboardMarkup(keyboard))


# ==================== BOSS: ОТЗЫВЫ ====================

async def show_boss_reviews(update_or_query, is_callback: bool):
    app, db, Product, Category, Review, Order, OrderItem, TelegramUser, *_ = get_db()
    if is_callback:
        obj = update_or_query
        send = lambda t, kb=None: obj.edit_message_text(t, reply_markup=kb, parse_mode='HTML')
    else:
        obj = update_or_query
        send = lambda t, kb=None: obj.message.reply_text(t, reply_markup=kb, parse_mode='HTML')

    with app.app_context():
        pending = Review.query.filter_by(status='pending').order_by(Review.created_at.desc()).all()
        if not pending:
            text = "💬 Нет отзывов на модерации."
            keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="menu_boss")]]
        else:
            text = "💬 <b>Отзывы на модерации</b>\n\n"
            keyboard = []
            for r in pending:
                pname = r.product.name[:25] if r.product else "?"
                text += f"• ID {r.id}: {r.customer_name} — {pname}\n"
                keyboard.append([
                    InlineKeyboardButton("✅", callback_data=f"review_approve_{r.id}"),
                    InlineKeyboardButton("❌", callback_data=f"review_reject_{r.id}")
                ])
            keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="menu_boss")])
        await send(text, InlineKeyboardMarkup(keyboard))


# ==================== ADMIN: ПРОМОКОДЫ ====================

async def show_admin_promo_menu(update_or_query, is_callback: bool):
    """Меню управления промокодами (только admin)"""
    app, db, Product, Category, Review, Order, OrderItem, TelegramUser, BotSetting, PromoCode = get_db()
    if is_callback:
        obj = update_or_query
        user_id = obj.from_user.id if obj.from_user else 0
        send = lambda t, kb=None: obj.edit_message_text(t, reply_markup=kb, parse_mode='HTML')
    else:
        obj = update_or_query
        user_id = obj.effective_user.id if obj.effective_user else 0
        send = lambda t, kb=None: obj.message.reply_text(t, reply_markup=kb, parse_mode='HTML')

    if not role_can_access(get_user_role(user_id), 'admin'):
        await send("⛔ Только для администратора.")
        return

    with app.app_context():
        promos = PromoCode.query.order_by(PromoCode.created_at.desc()).limit(20).all()
        text = "🎟 <b>Промокоды</b>\n\n"
        keyboard = []
        for p in promos:
            st = "✅" if p.is_active else "⏸"
            typ = f"{p.discount_value}%" if p.discount_type == 'percent' else f"{p.discount_value} ₽"
            text += f"{st} <code>{p.code}</code> — {typ} (исп: {p.used_count})\n"
            keyboard.append([
                InlineKeyboardButton(f"✏️ {p.code}", callback_data=f"promo_edit_{p.id}"),
                InlineKeyboardButton("🗑", callback_data=f"promo_del_{p.id}")
            ])
        keyboard.append([InlineKeyboardButton("➕ Создать промокод", callback_data="promo_create")])
        admin_url = ""
        try:
            base = os.environ.get('SITE_URL', '')
            if not base and _config_exists():
                import config
                base = getattr(config, 'SITE_URL', None) or 'http://127.0.0.1:5000'
            admin_url = f"{base.rstrip('/')}/admin?tab=promo" if base else ""
        except Exception:
            pass
        if admin_url:
            keyboard.append([InlineKeyboardButton("🌐 Открыть в админке", url=admin_url)])
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="menu_main")])
        if not promos:
            text += "Промокодов пока нет."
        await send(text, InlineKeyboardMarkup(keyboard))


async def show_promo_create(update_or_query):
    """Создание промокода — инструкция (полное создание в админке)"""
    obj = update_or_query
    send = lambda t, kb=None: obj.edit_message_text(t, reply_markup=kb, parse_mode='HTML')
    admin_url = ""
    try:
        base = os.environ.get('SITE_URL', '')
        if not base and _config_exists():
            import config
            base = getattr(config, 'SITE_URL', None) or 'http://127.0.0.1:5000'
        admin_url = f"{base.rstrip('/')}/admin/promo/add" if base else ""
    except Exception:
        pass
    text = (
        "➕ <b>Создание промокода</b>\n\n"
        "Для полного управления промокодами (код, тип скидки, мин. заказ, срок и т.д.) "
        "используй админку на сайте."
    )
    keyboard = []
    if admin_url:
        keyboard.append([InlineKeyboardButton("🌐 Создать в админке", url=admin_url)])
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="menu_admin_promo")])
    await send(text, InlineKeyboardMarkup(keyboard))


async def show_promo_edit(update_or_query, promo_id: int):
    """Редактирование промокода — ссылка на админку"""
    app, db, Product, Category, Review, Order, OrderItem, TelegramUser, BotSetting, PromoCode = get_db()
    obj = update_or_query
    send = lambda t, kb=None: obj.edit_message_text(t, reply_markup=kb, parse_mode='HTML')
    admin_url = ""
    try:
        base = os.environ.get('SITE_URL', '')
        if not base and _config_exists():
            import config
            base = getattr(config, 'SITE_URL', None) or 'http://127.0.0.1:5000'
        admin_url = f"{base.rstrip('/')}/admin/promo/{promo_id}/edit" if base else ""
    except Exception:
        pass
    with app.app_context():
        p = PromoCode.query.get(promo_id)
        if not p:
            await send("Промокод не найден.")
            return
        text = f"✏️ <b>{p.code}</b>\n\nРедактирование — в админке на сайте."
        keyboard = []
        if admin_url:
            keyboard.append([InlineKeyboardButton("🌐 Редактировать", url=admin_url)])
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="menu_admin_promo")])
        await send(text, InlineKeyboardMarkup(keyboard))


async def promo_delete_confirm(update_or_query, promo_id: int):
    """Удаление промокода"""
    app, db, Product, Category, Review, Order, OrderItem, TelegramUser, BotSetting, PromoCode = get_db()
    obj = update_or_query
    user_id = obj.from_user.id if obj.from_user else 0
    if not role_can_access(get_user_role(user_id), 'admin'):
        await obj.answer("⛔ Только админ", show_alert=True)
        return
    with app.app_context():
        p = PromoCode.query.get(promo_id)
        if p:
            code = p.code
            db.session.delete(p)
            db.session.commit()
            await obj.answer(f"✅ Промокод {code} удалён", show_alert=True)
    await show_admin_promo_menu(update_or_query, True)


# ==================== ADMIN: НАЗНАЧЕНИЯ ====================

async def show_admin_menu(update_or_query, is_callback: bool):
    app, db, Product, Category, Review, Order, OrderItem, TelegramUser, *_ = get_db()
    if is_callback:
        obj = update_or_query
        user_id = obj.from_user.id if obj.from_user else 0
        send = lambda t, kb=None: obj.edit_message_text(t, reply_markup=kb, parse_mode='HTML')
    else:
        obj = update_or_query
        user_id = obj.effective_user.id if obj.effective_user else 0
        send = lambda t, kb=None: obj.message.reply_text(t, reply_markup=kb, parse_mode='HTML')

    if not role_can_access(get_user_role(user_id), 'admin'):
        await send("⛔ Только для администратора.")
        return

    with app.app_context():
        users = TelegramUser.query.order_by(TelegramUser.role.desc(), TelegramUser.username).all()
        text = "⚙️ <b>Admin — Назначение ролей</b>\n\nВыбери пользователя:"
        keyboard = []
        for u in users[:30]:
            role_emoji = {"admin": "👑", "boss": "👔", "courier": "🚚", "user": "👤"}.get(u.role, "•")
            uname = f"@{u.username}" if u.username else str(u.telegram_id)
            keyboard.append([InlineKeyboardButton(f"{role_emoji} {uname} ({u.role})", callback_data=f"admin_user_{u.id}")])
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="menu_main")])
        await send(text, InlineKeyboardMarkup(keyboard))


async def show_admin_user_role(update_or_query, user_db_id: int):
    app, db, Product, Category, Review, Order, OrderItem, TelegramUser, *_ = get_db()
    obj = update_or_query
    send = lambda t, kb=None: obj.edit_message_text(t, reply_markup=kb, parse_mode='HTML')

    with app.app_context():
        u = TelegramUser.query.get(user_db_id)
        if not u:
            await send("Пользователь не найден.")
            return
        text = f"👤 {u.username or u.telegram_id}\nТекущая роль: {u.role}\n\nВыбери новую роль:"
        keyboard = [
            [InlineKeyboardButton("👤 Пользователь", callback_data=f"admin_set_{u.id}_user")],
            [InlineKeyboardButton("🚚 Курьер", callback_data=f"admin_set_{u.id}_courier")],
            [InlineKeyboardButton("👔 Boss", callback_data=f"admin_set_{u.id}_boss")],
            [InlineKeyboardButton("👑 Admin", callback_data=f"admin_set_{u.id}_admin")],
            [InlineKeyboardButton("◀️ Назад", callback_data="menu_admin")],
        ]
        await send(text, InlineKeyboardMarkup(keyboard))


# ==================== ОБРАБОТЧИК CALLBACK ====================

async def _safe_answer_callback(query, text=None, show_alert=False):
    """Отвечает на callback. Возвращает True если успешно, False если запрос истёк или таймаут."""
    try:
        await query.answer(text=text, show_alert=show_alert)
        return True
    except Exception as e:
        err = str(e).lower()
        err_type = type(e).__name__.lower()
        if ("too old" in err or "timeout" in err or "timed out" in err or
            ("query" in err and "invalid" in err) or
            "timedout" in err_type or "connect" in err):
            logger.warning("Callback answer failed (expired/timeout): %s", e)
            return False
        if "not modified" in err:
            return True  # уже отвечено
        raise


async def _safe_edit_message(obj, text, reply_markup=None, parse_mode='HTML'):
    """Безопасное редактирование сообщения. Игнорирует 'Message is not modified'."""
    try:
        await obj.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except BadRequest as e:
        if "not modified" in str(e).lower() or "message is not modified" in str(e).lower():
            logger.debug("Message not modified, skipping: %s", e)
        else:
            raise
    except TimedOut:
        logger.warning("Edit message timed out")
        raise


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data or ""
    if not await _safe_answer_callback(query):
        return
    user_id = query.from_user.id if query.from_user else 0

    # noop
    if data == "noop":
        await query.answer()
        return

    # Главное меню
    if data == "menu_ask_cancel":
        context.user_data.pop('awaiting_question', None)
        # Показываем главное меню
        data = "menu_main"
    if data == "menu_main":
        # Эмулируем start
        context.user_data.pop('awaiting_checkout', None)
        context.user_data.pop('awaiting_question', None)
        role = get_user_role(user_id)
        text = "🛍 <b>LIL STORE</b>\n\nВыбери раздел:"
        keyboard = []
        keyboard.append([InlineKeyboardButton("🛒 Каталог", callback_data="menu_catalog")])
        keyboard.append([InlineKeyboardButton("🛍 Корзина", callback_data="menu_cart")])
        keyboard.append([InlineKeyboardButton("📦 Оформить заказ", callback_data="menu_checkout")])
        keyboard.append([InlineKeyboardButton("💬 Задать вопрос", callback_data="menu_ask_question")])
        site_url = get_site_url()
        if site_url.startswith('https://'):
            keyboard.append([InlineKeyboardButton("🚀 Запустить приложение", web_app=WebAppInfo(url=site_url))])
        if role_can_access(role, 'courier'):
            keyboard.append([InlineKeyboardButton("🚚 Курьер — Заказы", callback_data="menu_courier_orders")])
            keyboard.append([InlineKeyboardButton("❓ Как отвечать на вопросы", callback_data="menu_support_help")])
        if role_can_access(role, 'boss'):
            keyboard.append([InlineKeyboardButton("👔 Boss — Меню", callback_data="menu_boss")])
        if role_can_access(role, 'admin'):
            keyboard.append([InlineKeyboardButton("⚙️ Admin — Назначения", callback_data="menu_admin")])
            keyboard.append([InlineKeyboardButton("🎟 Промокоды", callback_data="menu_admin_promo")])
        await _safe_edit_message(query, text, InlineKeyboardMarkup(keyboard))
        return

    # Задать вопрос (подсказка для пользователя) — включаем режим ожидания вопроса
    if data == "menu_ask_question":
        context.user_data['awaiting_question'] = True
        text = (
            "💬 <b>Задать вопрос</b>\n\n"
            "Напишите ваш вопрос <b>следующим сообщением</b> в этот чат.\n\n"
            "Ответ придёт сюда от поддержки. Курьер, Boss и Admin могут отвечать на вопросы."
        )
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="menu_ask_cancel")]]
        await _safe_edit_message(query, text, InlineKeyboardMarkup(keyboard))
        return

    # Как отвечать на вопросы (только staff: курьер, boss, admin)
    if data == "menu_support_help":
        role = get_user_role(user_id)
        if not role_can_access(role, 'courier'):
            await query.answer("⛔ Только для сотрудников.", show_alert=True)
            return
        notify_chat = _get_notification_chat_id()
        if notify_chat:
            text = (
                "❓ <b>Как отвечать на вопросы</b>\n\n"
                "Вопросы от клиентов приходят в <b>чат уведомлений</b> (где выполнен /set_notify).\n\n"
                "Чтобы ответить:\n"
                "1. Откройте этот чат\n"
                "2. Найдите сообщение с вопросом (❓ Вопрос от...)\n"
                "3. Нажмите <b>Reply</b> (Ответить) на это сообщение\n"
                "4. Напишите ответ — он автоматически уйдёт клиенту"
            )
        else:
            text = (
                "❓ <b>Как отвечать на вопросы</b>\n\n"
                "Сначала настройте чат уведомлений:\n"
                "1. Добавьте бота в группу (или используйте личный чат)\n"
                "2. Выполните команду /set_notify в том чате\n"
                "После этого вопросы будут приходить туда, и вы сможете отвечать через Reply."
            )
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="menu_main")]]
        await _safe_edit_message(query, text, InlineKeyboardMarkup(keyboard))
        return

    # Каталог
    if data == "menu_catalog":
        await show_catalog(query, context, True, None)
        return
    if data.startswith("cat_"):
        cid = data.replace("cat_", "")
        if cid == "all":
            await show_catalog(query, context, True, show_all=True)
        else:
            await show_catalog(query, context, True, category_id=int(cid))
        return

    # Подробнее о товаре (фото + описание)
    if data.startswith("detail_"):
        pid = int(data.replace("detail_", ""))
        await show_product_detail(query, context, pid)
        return

    # Добавить в корзину
    if data.startswith("add_"):
        pid = int(data.replace("add_", ""))
        cart = get_cart(context, user_id)
        cart[str(pid)] = cart.get(str(pid), 0) + 1
        cat_id = context.user_data.get('last_catalog_category')
        show_all = context.user_data.get('last_catalog_show_all', False)
        await show_catalog(query, context, True, category_id=cat_id, show_all=show_all)
        return

    # Корзина
    if data == "menu_cart":
        await show_cart(query, context, True)
        return
    if data == "cart_clear":
        get_cart(context, user_id).clear()
        await show_cart(query, context, True)
        return
    if data.startswith("cart_plus_"):
        pid = data.replace("cart_plus_", "")
        cart = get_cart(context, user_id)
        cart[pid] = cart.get(pid, 0) + 1
        await show_cart(query, context, True)
        return
    if data.startswith("cart_minus_"):
        pid = data.replace("cart_minus_", "")
        cart = get_cart(context, user_id)
        if cart.get(pid, 0) > 1:
            cart[pid] -= 1
        else:
            cart.pop(pid, None)
        await show_cart(query, context, True)
        return

    # Оформление
    if data == "menu_checkout":
        await start_checkout(query, context, True)
        return

    # Курьер
    if data == "menu_courier_orders":
        await show_courier_orders(query, context, True, 0, None)
        return
    if data.startswith("courier_page_"):
        parts = data.replace("courier_page_", "").split("_")
        page = int(parts[0]) if parts and parts[0].isdigit() else 0
        filt = parts[1] if len(parts) > 1 and parts[1] == 'my' else None
        await show_courier_orders(query, context, True, page, filt)
        return
    if data.startswith("courier_take_"):
        oid = int(data.replace("courier_take_", ""))
        app, db, Product, Category, Review, Order, OrderItem, TelegramUser, *_ = get_db()
        with app.app_context():
            order = Order.query.get(oid)
            if order and order.status in ('new', 'processing'):
                order.courier_telegram_id = user_id
                order.status = 'processing'
                db.session.commit()
        route = context.user_data.setdefault('courier_route_orders', set())
        if not isinstance(route, set):
            route = set(str(x) for x in route) if route else set()
        route.add(str(oid))
        context.user_data['courier_route_orders'] = route
        await show_courier_orders(query, context, True, 0, None)
        return
    if data.startswith("courier_route_add_"):
        oid = data.replace("courier_route_add_", "")
        route = context.user_data.setdefault('courier_route_orders', set())
        if not isinstance(route, set):
            route = set(route) if route else set()
        route.add(str(oid))
        context.user_data['courier_route_orders'] = route
        await show_courier_orders(query, context, True, 0, None)
        return
    if data.startswith("courier_route_del_"):
        oid = data.replace("courier_route_del_", "")
        route = context.user_data.get('courier_route_orders') or set()
        if isinstance(route, set):
            route.discard(str(oid))
        else:
            context.user_data['courier_route_orders'] = set()
        await show_courier_orders(query, context, True, 0, None)
        return
    if data.startswith("complete_"):
        app, db, Product, Category, Review, Order, OrderItem, TelegramUser, *_ = get_db()
        oid = int(data.replace("complete_", ""))
        with app.app_context():
            order = Order.query.get(oid)
            if order:
                order.status = 'completed'
                db.session.commit()
        route = context.user_data.get('courier_route_orders') or set()
        if isinstance(route, set):
            route.discard(str(oid))
        context.user_data['courier_route_orders'] = route
        await show_courier_orders(query, context, True, 0, None)
        return
    if data.startswith("courier_cancel_"):
        oid = int(data.replace("courier_cancel_", ""))
        app, db, Product, Category, Review, Order, OrderItem, TelegramUser, *_ = get_db()
        with app.app_context():
            order = Order.query.get(oid)
            if order:
                order.status = 'cancelled'
                order.courier_telegram_id = None
                db.session.commit()
        route = context.user_data.get('courier_route_orders') or set()
        if isinstance(route, set):
            route.discard(str(oid))
        context.user_data['courier_route_orders'] = route
        await show_courier_orders(query, context, True, 0, None)
        return
    if data == "courier_route":
        app, db, Product, Category, Review, Order, OrderItem, TelegramUser, *_ = get_db()
        raw_route = context.user_data.get('courier_route_orders') or set()
        route_ids = set(str(x) for x in raw_route) if raw_route else set()
        with app.app_context():
            if route_ids:
                order_ids = [int(x) for x in route_ids if str(x).isdigit()]
                orders = Order.query.filter(Order.id.in_(order_ids), Order.status.in_(['new', 'processing'])).all()
            else:
                orders = Order.query.filter(Order.courier_telegram_id == user_id, Order.status.in_(['new', 'processing'])).order_by(Order.created_at.desc()).limit(15).all()
            if not orders:
                orders = Order.query.filter(Order.status.in_(['new', 'processing'])).order_by(Order.created_at.desc()).limit(10).all()
            addrs = [o.delivery_address for o in orders if o.delivery_address]
        from bot_utils import build_yandex_route_url
        url = build_yandex_route_url(addrs)
        if url:
            text = "🗺 <b>Маршрут построен</b>\n\n" + (f"По {len(addrs)} адресам." if addrs else "")
            keyboard = [
                [InlineKeyboardButton("🗺 Открыть в Яндекс.Картах", url=url)],
                [InlineKeyboardButton("◀️ Назад к заказам", callback_data="menu_courier_orders")]
            ]
            await _safe_edit_message(query, text, InlineKeyboardMarkup(keyboard))
        else:
            text = "🗺 <b>Маршрут</b>\n\nНет адресов. Нажмите «➕ В маршрут» у нужных заказов, затем снова «Маршрут»."
            keyboard = [[InlineKeyboardButton("◀️ Назад к заказам", callback_data="menu_courier_orders")]]
            await _safe_edit_message(query, text, InlineKeyboardMarkup(keyboard))
        return

    # Boss
    if data == "menu_boss":
        await show_boss_menu(query, True)
        return
    if data == "boss_site":
        await show_boss_site(query, True)
        return
    if data == "boss_add_product":
        admin_url = ""
        try:
            import config
            key = getattr(config, 'ADMIN_SECRET', '')
            base = getattr(config, 'SITE_URL', None) or os.environ.get('SITE_URL', 'http://127.0.0.1:5000')
            admin_url = f"{base}/admin/products?key={key}" if key else ""
        except Exception:
            pass
        text = "➕ <b>Добавление товара</b>\n\nДобавляй товары через админку на сайте."
        keyboard = [[InlineKeyboardButton("🌐 Открыть админку", url=admin_url)]] if admin_url else []
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="boss_site")])
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        return
    if data.startswith("boss_edit_"):
        pid = int(data.replace("boss_edit_", ""))
        app, db, Product, Category, Review, Order, OrderItem, TelegramUser, *_ = get_db()
        with app.app_context():
            p = Product.query.get(pid)
            if p:
                admin_url = ""
                try:
                    import config
                    key = getattr(config, 'ADMIN_SECRET', '')
                    base = getattr(config, 'SITE_URL', None) or os.environ.get('SITE_URL', 'http://127.0.0.1:5000')
                    admin_url = f"{base}/admin?key={key}" if key else base
                except Exception:
                    pass
                text = f"✏️ <b>{p.name}</b>\n\nЦена: {p.price:,.0f} ₽\n\n".replace(",", " ")
                text += f"Для изменения цен и изображений открой админку на сайте." + (f"\n{admin_url}" if admin_url else "")
                keyboard = [[InlineKeyboardButton("◀️ К товарам", callback_data="boss_site")]]
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
            else:
                await query.answer("Товар не найден", show_alert=True)
        return
    if data.startswith("boss_orders_"):
        page = int(data.replace("boss_orders_", "")) if data.replace("boss_orders_", "").isdigit() else 0
        await show_boss_orders(query, True, page)
        return
    if data.startswith("boss_complete_"):
        oid = int(data.replace("boss_complete_", ""))
        app, db, Product, Category, Review, Order, OrderItem, TelegramUser, *_ = get_db()
        with app.app_context():
            order = Order.query.get(oid)
            if order:
                order.status = 'completed'
                db.session.commit()
        await show_boss_orders(query, True, 0)
        return
    if data.startswith("boss_cancel_"):
        oid = int(data.replace("boss_cancel_", ""))
        app, db, Product, Category, Review, Order, OrderItem, TelegramUser, *_ = get_db()
        with app.app_context():
            order = Order.query.get(oid)
            if order:
                order.status = 'cancelled'
                order.courier_telegram_id = None
                db.session.commit()
        await show_boss_orders(query, True, 0)
        return
    if data == "boss_stats":
        await show_boss_stats(query, True)
        return
    if data == "boss_profit":
        await show_boss_profit(query, True)
        return
    if data == "boss_profit_period":
        await query.answer("Выбор периода — в следующей версии. Сейчас показывается общая прибыль.", show_alert=True)
        return
    if data == "boss_reviews":
        await show_boss_reviews(query, True)
        return

    # Модерация отзывов
    if data.startswith("review_approve_"):
        app, db, Product, Category, Review, Order, OrderItem, TelegramUser, *_ = get_db()
        rid = int(data.replace("review_approve_", ""))
        role = get_user_role(user_id)
        if not role_can_access(role, 'boss'):
            await query.answer("Нет доступа", show_alert=True)
            return
        with app.app_context():
            r = Review.query.get(rid)
            if r:
                r.status = 'approved'
                db.session.commit()
                await query.edit_message_text(query.message.text + "\n\n✅ Одобрено!", parse_mode='HTML')
        return
    if data.startswith("review_reject_"):
        app, db, Product, Category, Review, Order, OrderItem, TelegramUser, *_ = get_db()
        rid = int(data.replace("review_reject_", ""))
        role = get_user_role(user_id)
        if not role_can_access(role, 'boss'):
            await query.answer("Нет доступа", show_alert=True)
            return
        with app.app_context():
            r = Review.query.get(rid)
            if r:
                r.status = 'rejected'
                db.session.commit()
                await query.edit_message_text(query.message.text + "\n\n❌ Отклонено", parse_mode='HTML')
        return

    # Admin
    if data == "menu_admin":
        await show_admin_menu(query, True)
        return
    if data == "menu_admin_promo":
        await show_admin_promo_menu(query, True)
        return
    if data == "promo_create":
        await show_promo_create(query)
        return
    if data.startswith("promo_edit_"):
        pid = int(data.replace("promo_edit_", ""))
        await show_promo_edit(query, pid)
        return
    if data.startswith("promo_del_"):
        pid = int(data.replace("promo_del_", ""))
        await promo_delete_confirm(query, pid)
        return
    if data.startswith("admin_user_"):
        uid = int(data.replace("admin_user_", ""))
        await show_admin_user_role(query, uid)
        return
    if data.startswith("admin_set_"):
        parts = data.replace("admin_set_", "").split("_")
        if len(parts) >= 2:
            app, db, Product, Category, Review, Order, OrderItem, TelegramUser, *_ = get_db()
            uid, new_role = int(parts[0]), parts[1]
            if get_user_role(user_id) != 'admin':
                await query.answer("Только админ может назначать роли", show_alert=True)
                return
            with app.app_context():
                u = TelegramUser.query.get(uid)
                if u:
                    u.role = new_role
                    db.session.commit()
                    await query.answer(f"✅ Роль изменена на {new_role}!", show_alert=True)
            await show_admin_menu(query, True)
        return


# ==================== УВЕДОМЛЕНИЯ: ЧАТ КУДА ДОБАВЛЕН БОТ ====================

def _get_notification_chat_id():
    """Получить chat_id для уведомлений из БД или config"""
    _, chat_id, _, _ = get_config()
    if chat_id:
        try:
            return int(chat_id)
        except (ValueError, TypeError):
            pass
    app, db, *rest = get_db()
    BotSetting = rest[-2]  # rest[-1]=PromoCode
    with app.app_context():
        s = BotSetting.query.filter_by(key='notification_chat_id').first()
        if s and s.value:
            return int(s.value)
    return None


def _save_notification_chat(chat_id: int):
    """Сохранить chat_id для уведомлений (в БД)"""
    app, db, *rest = get_db()
    BotSetting = rest[-2]  # rest[-1]=PromoCode
    with app.app_context():
        s = BotSetting.query.filter_by(key='notification_chat_id').first()
        if s:
            s.value = str(chat_id)
        else:
            s = BotSetting(key='notification_chat_id', value=str(chat_id))
            db.session.add(s)
        db.session.commit()


async def cmd_set_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установить этот чат для уведомлений о заказах и отзывах (только Boss/Admin)"""
    user_id = update.effective_user.id if update.effective_user else 0
    role = get_user_role(user_id)
    if not role_can_access(role, 'boss'):
        await update.message.reply_text("⛔ Только Boss или Admin может настроить уведомления.")
        return
    chat_id = update.effective_chat.id if update.effective_chat else 0
    _save_notification_chat(chat_id)
    await update.message.reply_text(
        f"✅ Уведомления о заказах и отзывах будут приходить сюда!\n"
        f"Chat ID: {chat_id}"
    )


async def _maybe_save_notification_chat(update: Update):
    """При первом сообщении (группа или личка) — сохранить chat для уведомлений"""
    chat = update.effective_chat
    if not chat:
        return
    app, db, *rest = get_db()
    BotSetting = rest[-2]  # rest[-1]=PromoCode
    with app.app_context():
        s = BotSetting.query.filter_by(key='notification_chat_id').first()
        if not s or not s.value:
            _save_notification_chat(chat.id)
            logger.info(f"Авто-сохранён chat_id {chat.id} для уведомлений")


# ==================== ОБРАБОТКА ТЕКСТА (CHECKOUT + ВОПРОСЫ) ====================

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текста: checkout, вопросы от user, ответы staff, иначе — меню"""
    await _maybe_save_notification_chat(update)
    user_id = update.effective_user.id if update.effective_user else 0
    role = get_user_role(user_id)

    if context.user_data.get('awaiting_checkout'):
        await handle_checkout_message(update, context)
        return

    # Ответ staff на вопрос пользователя (reply к нашему сообщению)
    if role != 'user' and update.message.reply_to_message:
        threads = context.bot_data.setdefault('support_threads', {})
        key = f"{update.message.chat_id}_{update.message.reply_to_message.message_id}"
        if key in threads:
            target_user_id = threads[key]
            orig_msg = update.message.reply_to_message
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"💬 <b>Ответ от поддержки:</b>\n\n{update.message.text}",
                parse_mode='HTML'
            )
            # Меню клиенту — отдельным сообщением
            client_role = get_user_role(target_user_id)
            await context.bot.send_message(
                chat_id=target_user_id,
                text="Выбери раздел:",
                reply_markup=_build_main_menu_keyboard(client_role),
                parse_mode='HTML'
            )
            # Обновляем исходное сообщение: показываем, что ответили
            try:
                old = orig_msg.text or orig_msg.caption or ''
                new_text = old.replace('⏳ Ожидает ответа', '✅ Ответ отправлен').replace('⏳ <i>Ожидает ответа</i>', '✅ <i>Ответ отправлен</i>')
                if new_text == old:
                    new_text = old + '\n\n✅ <i>Ответ отправлен</i>'
                await context.bot.edit_message_text(
                    chat_id=orig_msg.chat_id,
                    message_id=orig_msg.message_id,
                    text=new_text,
                    parse_mode='HTML'
                )
            except Exception:
                pass
            await update.message.reply_text("✅ Ответ отправлен клиенту.")
            # Меню staff — отдельным сообщением
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Выбери раздел:",
                reply_markup=_build_main_menu_keyboard(role),
                parse_mode='HTML'
            )
            return

    # Вопрос — только если пользователь нажал «Задать вопрос» и ждёт ввода
    if not context.user_data.get('awaiting_question'):
        await cmd_start(update, context)
        return

    context.user_data.pop('awaiting_question', None)
    notify_chat = _get_notification_chat_id()
    if notify_chat:
        text = (update.message.text or '').strip()
        if text:
            uname = update.effective_user.username or ''
            fname = update.effective_user.first_name or 'Клиент'
            role_label = f" [{role}]" if role != 'user' else ""
            msg_text = f"❓ <b>Вопрос от {fname}{role_label}</b> (@{uname or '—'}, ID: {user_id}):\n\n{text}\n\n⏳ <i>Ожидает ответа — ответьте на это сообщение (Reply)</i>"
            try:
                sent = await context.bot.send_message(
                    chat_id=notify_chat,
                    text=msg_text,
                    parse_mode='HTML'
                )
                context.bot_data.setdefault('support_threads', {})[f"{notify_chat}_{sent.message_id}"] = user_id
                await update.message.reply_text(
                    "✅ Ваш вопрос принят и будет рассмотрен в ближайшее время.\n\n"
                    "Ответ придёт сюда в этот чат. Ожидайте, с вами свяжутся."
                )
                # Меню — отдельным сообщением
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Выбери раздел:",
                    reply_markup=_build_main_menu_keyboard(role),
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.warning(f"Support notify: {e}")
                await cmd_start(update, context)
        else:
            context.user_data['awaiting_question'] = True
            await cmd_start(update, context)
    else:
        await update.message.reply_text(
            "💬 Поддержка пока не настроена. Boss или Admin должны добавить бота в группу и выполнить /set_notify.",
            parse_mode='HTML'
        )
        await cmd_start(update, context)


# ==================== MAIN ====================

def main():
    try:
        import config as _cfg
        if getattr(_cfg, 'TELEGRAM_RUN_POLLING', True) is False:
            print(
                "TELEGRAM_RUN_POLLING=False — polling отключён для этого проекта.\n"
                "Интерактивный бот запускайте только на основном сервере (my_shop / lilstore-bot.service).\n"
                "Уведомления о заказах с сайта работают через telegram_notify без polling."
            )
            sys.exit(0)
    except ImportError:
        pass

    token, chat_id, _, _ = get_config()
    if not token:
        print("Ошибка: задайте TELEGRAM_BOT_TOKEN в config.py")
        sys.exit(1)

    try:
        import app as app_mod
        if hasattr(app_mod, 'migrate_review_status'):
            app_mod.migrate_review_status()
        if hasattr(app_mod, 'migrate_telegram_and_cost'):
            app_mod.migrate_telegram_and_cost()
    except Exception as e:
        logger.info(f"Миграция: {e}")

    application = (
        Application.builder()
        .token(token)
        .connect_timeout(30)
        .read_timeout(60)
        .build()
    )
    # Текстовые сообщения — показывать меню (должен быть до CommandHandler для надёжности)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_text_message
    ))
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("set_notify", cmd_set_notify))
    application.add_handler(CallbackQueryHandler(handle_callback))

    async def error_handler(update, context):
        err = context.error
        if err:
            err_str = str(err).lower()
            if "not modified" in err_str or "message is not modified" in err_str:
                logger.debug("Message not modified, ignoring: %s", err)
                return
            if isinstance(err, TimedOut):
                logger.warning("Request timed out: %s", err)
                return
        logger.error("Exception while handling an update: %s", err, exc_info=err)

    application.add_error_handler(error_handler)
    print("🤖 Бот запущен. Остановка: Ctrl+C")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
