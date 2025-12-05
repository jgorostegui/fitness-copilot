"""
Mock data service for training programs.

Provides predefined training programs (4, 5, 6 days/week) without CSV files.
"""

from datetime import datetime

from sqlmodel import Session, select

from app.models import TrainingProgram, TrainingRoutine


# Predefined training programs
TRAINING_PROGRAMS = [
    {
        "name": "Upper/Lower Split",
        "description": "4-day upper/lower body split for intermediate lifters",
        "days_per_week": 4,
        "difficulty": "intermediate",
        "routines": [
            # Day 0 (Monday) - Upper A
            {"day": 0, "exercise": "Bench Press", "hint": "Barbell", "sets": 4, "reps": 8, "load": 60},
            {"day": 0, "exercise": "Barbell Row", "hint": "Barbell", "sets": 4, "reps": 8, "load": 50},
            {"day": 0, "exercise": "Overhead Press", "hint": "Barbell or Dumbbells", "sets": 3, "reps": 10, "load": 30},
            {"day": 0, "exercise": "Pull-ups", "hint": "Assisted if needed", "sets": 3, "reps": 8, "load": 0},
            {"day": 0, "exercise": "Tricep Pushdown", "hint": "Cable", "sets": 3, "reps": 12, "load": 20},
            {"day": 0, "exercise": "Bicep Curl", "hint": "Dumbbells", "sets": 3, "reps": 12, "load": 10},
            # Day 1 (Tuesday) - Lower A
            {"day": 1, "exercise": "Squat", "hint": "Barbell", "sets": 4, "reps": 6, "load": 80},
            {"day": 1, "exercise": "Romanian Deadlift", "hint": "Barbell", "sets": 3, "reps": 10, "load": 60},
            {"day": 1, "exercise": "Leg Press", "hint": "Machine", "sets": 3, "reps": 12, "load": 100},
            {"day": 1, "exercise": "Leg Curl", "hint": "Machine", "sets": 3, "reps": 12, "load": 30},
            {"day": 1, "exercise": "Calf Raise", "hint": "Machine or Standing", "sets": 4, "reps": 15, "load": 40},
            # Day 3 (Thursday) - Upper B
            {"day": 3, "exercise": "Incline Bench Press", "hint": "Barbell or Dumbbells", "sets": 4, "reps": 10, "load": 50},
            {"day": 3, "exercise": "Lat Pulldown", "hint": "Cable", "sets": 4, "reps": 10, "load": 50},
            {"day": 3, "exercise": "Dumbbell Shoulder Press", "hint": "Dumbbells", "sets": 3, "reps": 12, "load": 20},
            {"day": 3, "exercise": "Cable Row", "hint": "Cable", "sets": 3, "reps": 12, "load": 40},
            {"day": 3, "exercise": "Skull Crushers", "hint": "EZ Bar", "sets": 3, "reps": 12, "load": 15},
            {"day": 3, "exercise": "Hammer Curl", "hint": "Dumbbells", "sets": 3, "reps": 12, "load": 12},
            # Day 4 (Friday) - Lower B
            {"day": 4, "exercise": "Deadlift", "hint": "Barbell", "sets": 4, "reps": 5, "load": 100},
            {"day": 4, "exercise": "Front Squat", "hint": "Barbell", "sets": 3, "reps": 8, "load": 50},
            {"day": 4, "exercise": "Walking Lunges", "hint": "Dumbbells", "sets": 3, "reps": 12, "load": 20},
            {"day": 4, "exercise": "Leg Extension", "hint": "Machine", "sets": 3, "reps": 15, "load": 30},
            {"day": 4, "exercise": "Seated Calf Raise", "hint": "Machine", "sets": 4, "reps": 15, "load": 30},
        ],
    },
    {
        "name": "Push/Pull/Legs",
        "description": "5-day PPL split for intermediate to advanced lifters",
        "days_per_week": 5,
        "difficulty": "intermediate",
        "routines": [
            # Day 0 (Monday) - Push
            {"day": 0, "exercise": "Bench Press", "hint": "Barbell", "sets": 4, "reps": 6, "load": 70},
            {"day": 0, "exercise": "Overhead Press", "hint": "Barbell", "sets": 4, "reps": 8, "load": 40},
            {"day": 0, "exercise": "Incline Dumbbell Press", "hint": "Dumbbells", "sets": 3, "reps": 10, "load": 25},
            {"day": 0, "exercise": "Lateral Raise", "hint": "Dumbbells", "sets": 3, "reps": 15, "load": 8},
            {"day": 0, "exercise": "Tricep Dips", "hint": "Parallel Bars", "sets": 3, "reps": 10, "load": 0},
            # Day 1 (Tuesday) - Pull
            {"day": 1, "exercise": "Deadlift", "hint": "Barbell", "sets": 4, "reps": 5, "load": 100},
            {"day": 1, "exercise": "Pull-ups", "hint": "Weighted if possible", "sets": 4, "reps": 8, "load": 0},
            {"day": 1, "exercise": "Barbell Row", "hint": "Barbell", "sets": 4, "reps": 8, "load": 60},
            {"day": 1, "exercise": "Face Pull", "hint": "Cable", "sets": 3, "reps": 15, "load": 15},
            {"day": 1, "exercise": "Barbell Curl", "hint": "EZ Bar", "sets": 3, "reps": 10, "load": 25},
            # Day 2 (Wednesday) - Legs
            {"day": 2, "exercise": "Squat", "hint": "Barbell", "sets": 4, "reps": 6, "load": 90},
            {"day": 2, "exercise": "Romanian Deadlift", "hint": "Barbell", "sets": 3, "reps": 10, "load": 70},
            {"day": 2, "exercise": "Leg Press", "hint": "Machine", "sets": 3, "reps": 12, "load": 120},
            {"day": 2, "exercise": "Leg Curl", "hint": "Machine", "sets": 3, "reps": 12, "load": 35},
            {"day": 2, "exercise": "Calf Raise", "hint": "Standing", "sets": 4, "reps": 15, "load": 50},
            # Day 3 (Thursday) - Push
            {"day": 3, "exercise": "Dumbbell Bench Press", "hint": "Dumbbells", "sets": 4, "reps": 10, "load": 30},
            {"day": 3, "exercise": "Arnold Press", "hint": "Dumbbells", "sets": 3, "reps": 10, "load": 18},
            {"day": 3, "exercise": "Cable Fly", "hint": "Cable", "sets": 3, "reps": 12, "load": 15},
            {"day": 3, "exercise": "Tricep Pushdown", "hint": "Cable", "sets": 3, "reps": 12, "load": 25},
            # Day 4 (Friday) - Pull
            {"day": 4, "exercise": "Lat Pulldown", "hint": "Cable", "sets": 4, "reps": 10, "load": 55},
            {"day": 4, "exercise": "Seated Cable Row", "hint": "Cable", "sets": 4, "reps": 10, "load": 50},
            {"day": 4, "exercise": "Dumbbell Shrug", "hint": "Dumbbells", "sets": 3, "reps": 12, "load": 30},
            {"day": 4, "exercise": "Hammer Curl", "hint": "Dumbbells", "sets": 3, "reps": 12, "load": 14},
        ],
    },
    {
        "name": "PPL Advanced",
        "description": "6-day Push/Pull/Legs for advanced lifters with high volume",
        "days_per_week": 6,
        "difficulty": "advanced",
        "routines": [
            # Day 0 (Monday) - Push A
            {"day": 0, "exercise": "Bench Press", "hint": "Barbell", "sets": 5, "reps": 5, "load": 80},
            {"day": 0, "exercise": "Overhead Press", "hint": "Barbell", "sets": 4, "reps": 6, "load": 45},
            {"day": 0, "exercise": "Incline Bench Press", "hint": "Barbell", "sets": 4, "reps": 8, "load": 55},
            {"day": 0, "exercise": "Dumbbell Fly", "hint": "Dumbbells", "sets": 3, "reps": 12, "load": 15},
            {"day": 0, "exercise": "Lateral Raise", "hint": "Dumbbells", "sets": 4, "reps": 15, "load": 10},
            {"day": 0, "exercise": "Tricep Pushdown", "hint": "Cable", "sets": 4, "reps": 12, "load": 30},
            # Day 1 (Tuesday) - Pull A
            {"day": 1, "exercise": "Deadlift", "hint": "Barbell", "sets": 5, "reps": 5, "load": 120},
            {"day": 1, "exercise": "Weighted Pull-ups", "hint": "Add weight", "sets": 4, "reps": 6, "load": 10},
            {"day": 1, "exercise": "Barbell Row", "hint": "Barbell", "sets": 4, "reps": 8, "load": 70},
            {"day": 1, "exercise": "Face Pull", "hint": "Cable", "sets": 4, "reps": 15, "load": 20},
            {"day": 1, "exercise": "Barbell Curl", "hint": "Barbell", "sets": 4, "reps": 10, "load": 30},
            # Day 2 (Wednesday) - Legs A
            {"day": 2, "exercise": "Squat", "hint": "Barbell", "sets": 5, "reps": 5, "load": 100},
            {"day": 2, "exercise": "Romanian Deadlift", "hint": "Barbell", "sets": 4, "reps": 8, "load": 80},
            {"day": 2, "exercise": "Leg Press", "hint": "Machine", "sets": 4, "reps": 10, "load": 150},
            {"day": 2, "exercise": "Leg Curl", "hint": "Machine", "sets": 4, "reps": 12, "load": 40},
            {"day": 2, "exercise": "Standing Calf Raise", "hint": "Machine", "sets": 5, "reps": 15, "load": 60},
            # Day 3 (Thursday) - Push B
            {"day": 3, "exercise": "Close Grip Bench Press", "hint": "Barbell", "sets": 4, "reps": 8, "load": 60},
            {"day": 3, "exercise": "Dumbbell Shoulder Press", "hint": "Dumbbells", "sets": 4, "reps": 10, "load": 25},
            {"day": 3, "exercise": "Cable Crossover", "hint": "Cable", "sets": 3, "reps": 12, "load": 20},
            {"day": 3, "exercise": "Front Raise", "hint": "Dumbbells", "sets": 3, "reps": 12, "load": 10},
            {"day": 3, "exercise": "Overhead Tricep Extension", "hint": "Cable", "sets": 4, "reps": 12, "load": 25},
            # Day 4 (Friday) - Pull B
            {"day": 4, "exercise": "Pendlay Row", "hint": "Barbell", "sets": 4, "reps": 6, "load": 65},
            {"day": 4, "exercise": "Lat Pulldown", "hint": "Cable", "sets": 4, "reps": 10, "load": 60},
            {"day": 4, "exercise": "Cable Row", "hint": "Cable", "sets": 4, "reps": 10, "load": 55},
            {"day": 4, "exercise": "Rear Delt Fly", "hint": "Machine or Dumbbells", "sets": 4, "reps": 15, "load": 10},
            {"day": 4, "exercise": "Incline Dumbbell Curl", "hint": "Dumbbells", "sets": 4, "reps": 10, "load": 12},
            # Day 5 (Saturday) - Legs B
            {"day": 5, "exercise": "Front Squat", "hint": "Barbell", "sets": 4, "reps": 6, "load": 70},
            {"day": 5, "exercise": "Sumo Deadlift", "hint": "Barbell", "sets": 4, "reps": 6, "load": 100},
            {"day": 5, "exercise": "Bulgarian Split Squat", "hint": "Dumbbells", "sets": 3, "reps": 10, "load": 20},
            {"day": 5, "exercise": "Leg Extension", "hint": "Machine", "sets": 4, "reps": 12, "load": 40},
            {"day": 5, "exercise": "Seated Calf Raise", "hint": "Machine", "sets": 5, "reps": 15, "load": 40},
        ],
    },
]



class MockDataService:
    """Service for loading mock training programs into the database."""

    @staticmethod
    def load_training_programs(session: Session) -> int:
        """
        Load predefined training programs if none exist.
        
        Returns the number of programs created.
        """
        # Check if programs already exist
        existing = session.exec(select(TrainingProgram)).first()
        if existing:
            return 0

        count = 0
        for program_data in TRAINING_PROGRAMS:
            # Create program
            program = TrainingProgram(
                name=program_data["name"],
                description=program_data["description"],
                days_per_week=program_data["days_per_week"],
                difficulty=program_data["difficulty"],
                created_at=datetime.utcnow(),
            )
            session.add(program)
            session.flush()  # Get the ID

            # Create routines
            for routine_data in program_data["routines"]:
                routine = TrainingRoutine(
                    program_id=program.id,
                    day_of_week=routine_data["day"],
                    exercise_name=routine_data["exercise"],
                    machine_hint=routine_data["hint"],
                    sets=routine_data["sets"],
                    reps=routine_data["reps"],
                    target_load_kg=routine_data["load"],
                    created_at=datetime.utcnow(),
                )
                session.add(routine)

            count += 1

        session.commit()
        return count

    @staticmethod
    def get_program_count(session: Session) -> int:
        """Get the number of training programs in the database."""
        from sqlmodel import func
        result = session.exec(select(func.count()).select_from(TrainingProgram)).one()
        return result


# Singleton instance
mock_data_service = MockDataService()
