"""Add premium booking tables

Revision ID: add_premium_bookings
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

def upgrade():
    # Create premium_bookings table
    op.create_table('premium_bookings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_code', sa.String(length=20), nullable=False),
        sa.Column('selections', sa.JSON(), nullable=False),
        sa.Column('total_odds', sa.Float(), nullable=False),
        sa.Column('price_usd', sa.Float(), nullable=False),
        sa.Column('created_by_admin_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_admin_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_premium_bookings_booking_code'), 'premium_bookings', ['booking_code'], unique=True)
    
    # Create premium_booking_purchases table
    op.create_table('premium_booking_purchases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount_paid_usd', sa.Float(), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('purchased_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['booking_id'], ['premium_bookings.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('premium_booking_purchases')
    op.drop_index(op.f('ix_premium_bookings_booking_code'), table_name='premium_bookings')
    op.drop_table('premium_bookings')
