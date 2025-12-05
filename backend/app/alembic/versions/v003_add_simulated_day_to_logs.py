"""add_simulated_day_to_logs

Revision ID: v003_simulated_day_logs
Revises: v002_simulated_day
Create Date: 2025-12-05

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "v003_simulated_day_logs"
down_revision = "v002_simulated_day"
branch_labels = None
depends_on = None


def upgrade():
    # Add simulated_day column to exercise_log with default 0
    op.add_column(
        "exercise_log",
        sa.Column("simulated_day", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index(
        op.f("ix_exercise_log_simulated_day"),
        "exercise_log",
        ["simulated_day"],
        unique=False,
    )

    # Add simulated_day column to meal_log with default 0
    op.add_column(
        "meal_log",
        sa.Column("simulated_day", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index(
        op.f("ix_meal_log_simulated_day"), "meal_log", ["simulated_day"], unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_meal_log_simulated_day"), table_name="meal_log")
    op.drop_column("meal_log", "simulated_day")
    op.drop_index(op.f("ix_exercise_log_simulated_day"), table_name="exercise_log")
    op.drop_column("exercise_log", "simulated_day")
