# -*- coding: utf-8 -*-
"""
Синхронизация изображений товаров с папками.
Обновляет product.image, если в папке Devices/ИмяТовара/ или Sticks/ИмяТовара/ есть файлы.
Поддерживаемые форматы: .jpg, .jpeg, .png, .webp
"""
import os
import sys

# Добавляем путь проекта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PRODUCTS_BASE = 'static/images/products'

def main():
    from app import app, db
    from models import Product
    
    with app.app_context():
        products = Product.query.all()
        updated = 0
        for p in products:
            # Пробуем пути: Devices/ИмяТовара и Sticks/ИмяТовара
            for subdir in ('Devices', 'Sticks'):
                folder = os.path.join(PRODUCTS_BASE, subdir, p.name)
                if not os.path.isdir(folder):
                    continue
                files = sorted([f for f in os.listdir(folder) 
                               if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
                if not files:
                    continue
                new_path = f"{subdir}/{p.name}/{files[0]}"
                if p.image != new_path:
                    p.image = new_path
                    updated += 1
                    print(f"  OK {p.name}: {new_path}")
                break
        if updated > 0:
            db.session.commit()
            print(f"\nОбновлено: {updated} товаров")
        else:
            print("Изменений нет. Проверьте:")
            print("  1. Папки: static/images/products/Devices/Iqos Iluma i Standart Seletti/")
            print("  2. Файлы: .jpg, .jpeg, .png или .webp")
            print("  3. Имя папки должно ТОЧНО совпадать с названием товара в БД")

if __name__ == "__main__":
    main()
