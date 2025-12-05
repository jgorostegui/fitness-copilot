import type { MealPlanItem, RoutineItem } from "@/types/fitness"

export const TARGET_CALORIES = {
  cut: 1800,
  maintain: 2400,
  bulk: 3000,
}

export const TARGET_PROTEIN = {
  cut: 180,
  maintain: 160,
  bulk: 200,
}

export const TODAY_ROUTINE: RoutineItem[] = [
  { exercise: "Barbell Squat", sets: 3, reps: "5-8", target: "RPE 8" },
  { exercise: "Leg Press", sets: 3, reps: "10-12", target: "RPE 7" },
  { exercise: "Romanian Deadlift", sets: 3, reps: "8-10", target: "RPE 8" },
  { exercise: "Leg Extension", sets: 2, reps: "15", target: "Failure" },
]

export const TODAY_MEAL_PLAN: MealPlanItem[] = [
  { meal: "Oatmeal & Whey", calories: 450, protein: 35 },
  { meal: "Chicken & Rice", calories: 600, protein: 45 },
  { meal: "Greek Yogurt", calories: 200, protein: 20 },
  { meal: "Salmon & Asparagus", calories: 550, protein: 40 },
]
