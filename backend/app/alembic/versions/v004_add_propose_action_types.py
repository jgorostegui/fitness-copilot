"""Add PROPOSE_FOOD and PROPOSE_EXERCISE to chatactiontype enum.

Revision ID: v004
Revises: v003_add_simulated_day_to_logs
Create Date: 2025-12-05

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "v004_add_propose_action_types"
down_revision = "v003_simulated_day_logs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new enum values to chatactiontype
    # Note: Must match the enum NAME (uppercase) not the value, as that's how
    # SQLAlchemy serializes Python enums to PostgreSQL enum types
    op.execute("ALTER TYPE chatactiontype ADD VALUE IF NOT EXISTS 'PROPOSE_FOOD'")
    op.execute("ALTER TYPE chatactiontype ADD VALUE IF NOT EXISTS 'PROPOSE_EXERCISE'")


def downgrade() -> None:
    # PostgreSQL doesn't support removing enum values easily
    # This would require recreating the enum type
    pass
