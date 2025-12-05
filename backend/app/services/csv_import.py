"""
CSV import service for loading training programs and meal plans.

Loads predefined data from CSV files into the database on application startup.
"""

import csv
import uuid
from datetime import datetime
from pathlib import Path

from sqlmodel import Session, select

from app.models import MealPlan, TrainingProgram, TrainingRoutine


class CSVImportService:
    """Service for importing CSV data into the database."""

    def __init__(self, data_dir: Path | str = "data"):
        self.data_dir = Path(data_dir)

    def load_training_programs(
        self, session: Session, csv_path: str | None = None
    ) -> int:
        """
        Load training programs and routines from CSV.

        CSV format:
        program_id,program_name,description,days_per_week,difficulty,day_of_week,
        exercise_name,machine_hint,sets,reps,target_load_kg

        Returns the number of programs loaded.
        """
        if csv_path is None:
            csv_path = str(self.data_dir / "programs.csv")

        path = Path(csv_path)
        if not path.exists():
            return 0

        # Track programs we've created and whether they already had routines
        programs: dict[str, TrainingProgram] = {}
        programs_with_routines: set[str] = set()
        routines_count = 0

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                program_key = row["program_id"]

                # Create program if not exists
                if program_key not in programs:
                    # Check if program already exists in DB
                    existing = session.exec(
                        select(TrainingProgram).where(
                            TrainingProgram.name == row["program_name"]
                        )
                    ).first()

                    if existing:
                        programs[program_key] = existing
                        # Check if this program already has routines
                        existing_routines = session.exec(
                            select(TrainingRoutine).where(
                                TrainingRoutine.program_id == existing.id
                            )
                        ).first()
                        if existing_routines:
                            programs_with_routines.add(program_key)
                    else:
                        program = TrainingProgram(
                            name=row["program_name"],
                            description=row["description"],
                            days_per_week=int(row["days_per_week"]),
                            difficulty=row["difficulty"],
                            created_at=datetime.utcnow(),
                        )
                        session.add(program)
                        session.flush()  # Get the ID
                        programs[program_key] = program

                # Skip creating routines if program already has them
                if program_key in programs_with_routines:
                    continue

                # Create routine for this row
                program = programs[program_key]

                # Validate numeric fields
                sets = int(row["sets"])
                reps = int(row["reps"])
                target_load = float(row["target_load_kg"])
                day_of_week = int(row["day_of_week"])

                if sets <= 0 or reps <= 0:
                    continue  # Skip invalid rows
                if target_load < 0:
                    continue
                if day_of_week < 0 or day_of_week > 6:
                    continue

                routine = TrainingRoutine(
                    program_id=program.id,
                    day_of_week=day_of_week,
                    exercise_name=row["exercise_name"],
                    machine_hint=row.get("machine_hint") or None,
                    sets=sets,
                    reps=reps,
                    target_load_kg=target_load,
                    created_at=datetime.utcnow(),
                )
                session.add(routine)
                routines_count += 1

        session.commit()
        return len(programs)

    def load_meal_plans(
        self, session: Session, user_id: uuid.UUID, csv_path: str | None = None
    ) -> int:
        """
        Load meal plans from CSV for a specific user.

        CSV format:
        day_of_week,meal_type,item_name,calories,protein_g,carbs_g,fat_g

        Returns the number of meal plan items loaded.
        """
        if csv_path is None:
            csv_path = str(self.data_dir / "meal_plans.csv")

        path = Path(csv_path)
        if not path.exists():
            return 0

        count = 0
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Validate numeric fields
                calories = int(row["calories"])
                protein_g = float(row["protein_g"])
                carbs_g = float(row["carbs_g"])
                fat_g = float(row["fat_g"])
                day_of_week = int(row["day_of_week"])

                if calories < 0 or protein_g < 0 or carbs_g < 0 or fat_g < 0:
                    continue  # Skip invalid rows
                if day_of_week < 0 or day_of_week > 6:
                    continue

                meal_plan = MealPlan(
                    user_id=user_id,
                    day_of_week=day_of_week,
                    meal_type=row["meal_type"],
                    item_name=row["item_name"],
                    calories=calories,
                    protein_g=protein_g,
                    carbs_g=carbs_g,
                    fat_g=fat_g,
                    created_at=datetime.utcnow(),
                )
                session.add(meal_plan)
                count += 1

        session.commit()
        return count

    def load_default_training_programs(self, session: Session) -> int:
        """
        Load default training programs if none exist.

        Returns the number of programs loaded.
        """
        # Check if programs already exist
        existing = session.exec(select(TrainingProgram)).first()
        if existing:
            return 0

        return self.load_training_programs(session)

    def load_meal_plans_for_persona(
        self, session: Session, user_id: uuid.UUID, persona: str
    ) -> int:
        """
        Load meal plans from persona-specific CSV for a user.

        Args:
            session: Database session
            user_id: User ID to assign meal plans to
            persona: One of "cut", "bulk", or "maintain"

        Returns the number of meal plan items loaded.
        """
        csv_filename = f"meal_plans_{persona}.csv"
        csv_path = str(self.data_dir / csv_filename)
        return self.load_meal_plans(session, user_id, csv_path)

    def load_training_programs_for_persona(
        self, session: Session, persona: str
    ) -> TrainingProgram | None:
        """
        Load training programs from persona-specific CSV.

        Args:
            session: Database session
            persona: One of "cut", "bulk", or "maintain"

        Returns the TrainingProgram created, or None if file doesn't exist.
        """
        csv_filename = f"routines_{persona}.csv"
        csv_path = str(self.data_dir / csv_filename)

        path = Path(csv_path)
        if not path.exists():
            return None

        # Load programs from persona-specific CSV
        self.load_training_programs(session, csv_path)

        # Return the first program loaded (persona CSVs should have one program)
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            first_row = next(reader, None)
            if first_row:
                return session.exec(
                    select(TrainingProgram).where(
                        TrainingProgram.name == first_row["program_name"]
                    )
                ).first()

        return None


# Singleton instance
csv_import_service = CSVImportService()
