from app import db
from models import Category, Product, Review
import json
from datetime import datetime, timedelta
import random

def create_test_data():
    """Создание тестовых данных"""
    
    # Категории
    categories = [
        {'name': 'IQOS ILUMA', 'slug': 'iqos-iluma', 'description': 'Устройства IQOS ILUMA', 'image': 'iluma-category.jpg'},
        {'name': 'Стики TEREA', 'slug': 'terea-sticks', 'description': 'Стики для IQOS ILUMA', 'image': 'terea-category.jpg'},
        {'name': 'Аксессуары', 'slug': 'accessories', 'description': 'Аксессуары для IQOS', 'image': 'accessories.jpg'},
    ]
    
    for cat_data in categories:
        category = Category(**cat_data)
        db.session.add(category)
    db.session.commit()
    
    # Товары
    products = [
        {
            'name': 'IQOS ILUMA Prime Golden',
            'price': 12990,
            'old_price': 14990,
            'description': 'Премиальное устройство IQOS ILUMA Prime в цвете Golden',
            'characteristics': json.dumps({'Цвет': 'Golden', 'Время зарядки': '90 минут', 'Вес': '100г'}),
            'image': 'iluma-prime-golden.jpg',
            'in_stock': True,
            'category_id': 1
        },
        {
            'name': 'IQOS ILUMA One',
            'price': 8990,
            'old_price': 9990,
            'description': 'Компактное устройство IQOS ILUMA One',
            'characteristics': json.dumps({'Цвет': 'Black', 'Время зарядки': '60 минут', 'Вес': '80г'}),
            'image': 'iluma-one.jpg',
            'in_stock': True,
            'category_id': 1
        },
        {
            'name': 'IQOS ILUMA Prime Galaxy Blue',
            'price': 14000,
            'description': 'Эксклюзивная модель Galaxy Blue',
            'characteristics': json.dumps({'Цвет': 'Galaxy Blue', 'Время зарядки': '90 минут', 'Вес': '100г'}),
            'image': 'iluma-prime-blue.jpg',
            'in_stock': True,
            'category_id': 1
        },
        {
            'name': 'Стики TEREA Rich Regular',
            'price': 450,
            'description': 'Крепкие стики с насыщенным вкусом табака',
            'characteristics': json.dumps({'Вкус': 'Rich Regular', 'Крепость': '5/5'}),
            'image': 'terea-rich.jpg',
            'in_stock': True,
            'category_id': 2
        },
        {
            'name': 'Стики TEREA Smooth Regular',
            'price': 450,
            'description': 'Мягкие стики с классическим вкусом',
            'characteristics': json.dumps({'Вкус': 'Smooth Regular', 'Крепость': '3/5'}),
            'image': 'terea-smooth.jpg',
            'in_stock': True,
            'category_id': 2
        },
        {
            'name': 'Стики TEREA Yellow',
            'price': 450,
            'description': 'Легкие стики с мягким вкусом',
            'characteristics': json.dumps({'Вкус': 'Yellow', 'Крепость': '2/5'}),
            'image': 'terea-yellow.jpg',
            'in_stock': True,
            'category_id': 2
        },
        {
            'name': 'Чехол для IQOS ILUMA',
            'price': 1290,
            'description': 'Силиконовый чехол для защиты устройства',
            'characteristics': json.dumps({'Цвет': 'Черный', 'Материал': 'Силикон'}),
            'image': 'case-black.jpg',
            'in_stock': True,
            'category_id': 3
        },
        {
            'name': 'Зарядное устройство',
            'price': 1990,
            'description': 'Быстрая зарядка для IQOS',
            'characteristics': json.dumps({'Мощность': '15W', 'Тип': 'USB-C'}),
            'image': 'charger.jpg',
            'in_stock': True,
            'category_id': 3
        }
    ]
    
    for prod_data in products:
        product = Product(**prod_data)
        db.session.add(product)
    db.session.commit()
    
    # Отзывы
    review_texts = [
        "Отличный товар, быстрая доставка!",
        "Спасибо магазину, все пришло в целости",
        "Пользуюсь неделю, все отлично",
        "Рекомендую продавца, качество оригинал",
        "Доставили быстро, упаковано хорошо",
        "Отличный магазин, буду заказывать еще",
        "Товар соответствует описанию, спасибо",
        "Лучшая цена, быстрая отправка"
    ]
    
    customers = [
        "Алексей", "Елена", "Дмитрий", "Анна", "Иван", "Мария", 
        "Павел", "Екатерина", "Сергей", "Ольга"
    ]
    
    products = Product.query.all()
    
    for _ in range(20):
        review = Review(
            product_id=random.choice(products).id,
            customer_name=random.choice(customers),
            rating=random.randint(4, 5),
            text=random.choice(review_texts),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
        )
        db.session.add(review)
    
    db.session.commit()
    print("Тестовые данные успешно созданы!")