"""Add simulated_day column to user table

Revision ID: v002_simulated_day
Revises: v001_chat_attachment
Create Date: 2025-12-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'v002_simulated_day'
down_revision = 'v001_chat_attachment'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('simulated_day', sa.Integer(), nullable=False, server_default='0'))


def downgrade():
    op.drop_column('user', 'simulated_day')
