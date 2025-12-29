"""Add market_type and selection columns if missing

Revision ID: 20251122_add_market_selection_if_missing
Revises: cfed9773af9b
Create Date: 2025-11-22 08:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251122_add_market_selection_if_missing'
down_revision = 'cfed9773af9b'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = [c['name'] for c in insp.get_columns('bets')]

    if 'market_type' not in cols:
        op.add_column('bets', sa.Column('market_type', sa.String(length=50), nullable=True))

    if 'selection' not in cols:
        op.add_column('bets', sa.Column('selection', sa.String(length=100), nullable=True))


def downgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = [c['name'] for c in insp.get_columns('bets')]

    if 'selection' in cols:
        op.drop_column('bets', 'selection')

    if 'market_type' in cols:
        op.drop_column('bets', 'market_type')
