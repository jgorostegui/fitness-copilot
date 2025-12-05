"""Add chat_attachment table for vision feature

Revision ID: v001_chat_attachment
Revises: 45b4c5a848fe
Create Date: 2025-12-05

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'v001_chat_attachment'
down_revision = '45b4c5a848fe'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('chat_attachment',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('content_type', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('data', sa.LargeBinary(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_attachment_user_id'), 'chat_attachment', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_chat_attachment_user_id'), table_name='chat_attachment')
    op.drop_table('chat_attachment')
