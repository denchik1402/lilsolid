"""Initial schema — все таблицы из models.py

Revision ID: 001
Revises:
Create Date: 2025-03-02

Использование:
  - Новая БД: py -m alembic upgrade head
  - Существующая БД (уже с таблицами): py -m alembic stamp head
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'category',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_table(
        'bot_setting',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(50), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    op.create_table(
        'telegram_user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(100), nullable=True),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('role', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id')
    )
    op.create_table(
        'product',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('slug', sa.String(200), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('cost', sa.Float(), nullable=True),
        sa.Column('old_price', sa.Float(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('characteristics', sa.Text(), nullable=True),
        sa.Column('image', sa.String(200), nullable=True),
        sa.Column('images', sa.Text(), nullable=True),
        sa.Column('in_stock', sa.Boolean(), nullable=True),
        sa.Column('views', sa.Integer(), nullable=True),
        sa.Column('model', sa.String(50), nullable=True),
        sa.Column('color', sa.String(50), nullable=True),
        sa.Column('is_exclusive', sa.Boolean(), nullable=True),
        sa.Column('is_hit', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_table(
        'review',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_name', sa.String(100), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('status', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'order',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_number', sa.String(20), nullable=True),
        sa.Column('customer_name', sa.String(100), nullable=False),
        sa.Column('customer_phone', sa.String(20), nullable=False),
        sa.Column('customer_email', sa.String(100), nullable=True),
        sa.Column('delivery_address', sa.Text(), nullable=True),
        sa.Column('delivery_method', sa.String(50), nullable=True),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('courier_telegram_id', sa.BigInteger(), nullable=True),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('promo_code', sa.String(50), nullable=True),
        sa.Column('discount_amount', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_number')
    )
    op.create_table(
        'order_item',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'promo_code',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('discount_type', sa.String(20), nullable=False),
        sa.Column('discount_value', sa.Float(), nullable=False),
        sa.Column('min_order', sa.Float(), nullable=True),
        sa.Column('max_uses', sa.Integer(), nullable=True),
        sa.Column('used_count', sa.Integer(), nullable=True),
        sa.Column('valid_from', sa.DateTime(), nullable=True),
        sa.Column('valid_until', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_table(
        'banner',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('image', sa.String(200), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('subtitle', sa.String(300), nullable=True),
        sa.Column('button_text', sa.String(50), nullable=True),
        sa.Column('button_url', sa.String(500), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('badge_type', sa.String(20), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('impressions', sa.Integer(), nullable=True),
        sa.Column('clicks', sa.Integer(), nullable=True),
        sa.Column('ab_test_group', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'home_block',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('image', sa.String(200), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('button_text', sa.String(50), nullable=True),
        sa.Column('button_url', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('home_block')
    op.drop_table('banner')
    op.drop_table('promo_code')
    op.drop_table('order_item')
    op.drop_table('order')
    op.drop_table('review')
    op.drop_table('product')
    op.drop_table('telegram_user')
    op.drop_table('bot_setting')
    op.drop_table('category')
