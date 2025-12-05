"""Add foundation models for Fitness Copilot

Revision ID: f001_foundation
Revises: 1a31ce608336
Create Date: 2024-12-05

Adds training_program, training_routine, meal_plan, meal_log, exercise_log tables.
Adds enhanced user profile fields.
Removes item table (template cruft).
"""

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

revision = "f001_foundation"
down_revision = "1a31ce608336"
branch_labels = None
depends_on = None


def upgrade():
    # Drop item table (template cruft)
    op.drop_table("item")

    # Create training_program table
    op.create_table(
        "training_program",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column("days_per_week", sa.Integer(), nullable=False),
        sa.Column("difficulty", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create training_routine table
    op.create_table(
        "training_routine",
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("exercise_name", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("machine_hint", sqlmodel.sql.sqltypes.AutoString(length=200), nullable=True),
        sa.Column("sets", sa.Integer(), nullable=False),
        sa.Column("reps", sa.Integer(), nullable=False),
        sa.Column("target_load_kg", sa.Float(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("program_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["program_id"], ["training_program.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


    # Create meal_plan table
    op.create_table(
        "meal_plan",
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("meal_type", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("item_name", sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False),
        sa.Column("calories", sa.Integer(), nullable=False),
        sa.Column("protein_g", sa.Float(), nullable=False),
        sa.Column("carbs_g", sa.Float(), nullable=False),
        sa.Column("fat_g", sa.Float(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_meal_plan_user_id", "meal_plan", ["user_id"])

    # Create meal_log table
    op.create_table(
        "meal_log",
        sa.Column("meal_name", sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False),
        sa.Column("meal_type", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("calories", sa.Integer(), nullable=False),
        sa.Column("protein_g", sa.Float(), nullable=False),
        sa.Column("carbs_g", sa.Float(), nullable=False),
        sa.Column("fat_g", sa.Float(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("logged_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_meal_log_user_id", "meal_log", ["user_id"])
    op.create_index("ix_meal_log_logged_at", "meal_log", ["logged_at"])

    # Create exercise_log table
    op.create_table(
        "exercise_log",
        sa.Column("exercise_name", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("sets", sa.Integer(), nullable=False),
        sa.Column("reps", sa.Integer(), nullable=False),
        sa.Column("weight_kg", sa.Float(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("logged_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_exercise_log_user_id", "exercise_log", ["user_id"])
    op.create_index("ix_exercise_log_logged_at", "exercise_log", ["logged_at"])

    # Add enhanced profile fields to user table
    op.add_column("user", sa.Column("age", sa.Integer(), nullable=True))
    op.add_column("user", sa.Column("sex", sqlmodel.sql.sqltypes.AutoString(length=10), nullable=True))
    op.add_column("user", sa.Column("weight_kg", sa.Float(), nullable=True))
    op.add_column("user", sa.Column("height_cm", sa.Integer(), nullable=True))
    op.add_column("user", sa.Column("body_fat_percentage", sa.Float(), nullable=True))
    op.add_column("user", sa.Column("goal_method", sqlmodel.sql.sqltypes.AutoString(length=30), nullable=True))
    op.add_column("user", sa.Column("goal_weight_kg", sa.Float(), nullable=True))
    op.add_column("user", sa.Column("custom_kg_per_week", sa.Float(), nullable=True))
    op.add_column("user", sa.Column("custom_kcal_per_day", sa.Integer(), nullable=True))
    op.add_column("user", sa.Column("activity_level", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True))
    op.add_column("user", sa.Column("selected_program_id", sa.Uuid(), nullable=True))
    op.add_column("user", sa.Column("protein_g_per_kg", sa.Float(), nullable=False, server_default="2.0"))
    op.add_column("user", sa.Column("fat_rest_g_per_kg", sa.Float(), nullable=False, server_default="0.7"))
    op.add_column("user", sa.Column("fat_train_g_per_kg", sa.Float(), nullable=False, server_default="0.8"))
    op.add_column("user", sa.Column("tef_factor", sa.Float(), nullable=False, server_default="0.10"))
    op.add_column("user", sa.Column("onboarding_complete", sa.Boolean(), nullable=False, server_default="false"))

    op.create_foreign_key("fk_user_selected_program", "user", "training_program", ["selected_program_id"], ["id"])



def downgrade():
    # Drop foreign key for selected_program_id
    op.drop_constraint("fk_user_selected_program", "user", type_="foreignkey")

    # Drop enhanced profile columns from user table
    op.drop_column("user", "onboarding_complete")
    op.drop_column("user", "tef_factor")
    op.drop_column("user", "fat_train_g_per_kg")
    op.drop_column("user", "fat_rest_g_per_kg")
    op.drop_column("user", "protein_g_per_kg")
    op.drop_column("user", "selected_program_id")
    op.drop_column("user", "activity_level")
    op.drop_column("user", "custom_kcal_per_day")
    op.drop_column("user", "custom_kg_per_week")
    op.drop_column("user", "goal_weight_kg")
    op.drop_column("user", "goal_method")
    op.drop_column("user", "body_fat_percentage")
    op.drop_column("user", "height_cm")
    op.drop_column("user", "weight_kg")
    op.drop_column("user", "sex")
    op.drop_column("user", "age")

    # Drop exercise_log table
    op.drop_index("ix_exercise_log_logged_at", table_name="exercise_log")
    op.drop_index("ix_exercise_log_user_id", table_name="exercise_log")
    op.drop_table("exercise_log")

    # Drop meal_log table
    op.drop_index("ix_meal_log_logged_at", table_name="meal_log")
    op.drop_index("ix_meal_log_user_id", table_name="meal_log")
    op.drop_table("meal_log")

    # Drop meal_plan table
    op.drop_index("ix_meal_plan_user_id", table_name="meal_plan")
    op.drop_table("meal_plan")

    # Drop training_routine table
    op.drop_table("training_routine")

    # Drop training_program table
    op.drop_table("training_program")

    # Recreate item table
    op.create_table(
        "item",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
