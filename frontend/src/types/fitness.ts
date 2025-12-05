export type PlanType = "cut" | "bulk" | "maintain"

export interface UserProfile {
  weight: number
  height: number
  plan: PlanType
  theme: "light" | "dark"
  onboardingComplete: boolean
}

export interface MealLog {
  id: string
  name: string
  calories: number
  protein: number
  time: string
  type: "breakfast" | "lunch" | "dinner" | "snack"
}

export interface ExerciseLog {
  id: string
  name: string
  sets: number
  reps: number
  weight: number
  time: string
}

export type Sender = "user" | "ai" | "system"

export interface Message {
  id: string
  text: string
  sender: Sender
  timestamp: Date
  image?: string
  actionType?: "log_food" | "log_exercise" | "none"
  actionData?: {
    name?: string
    calories?: number
    protein?: number
    sets?: number
    reps?: number
    weight?: number
  }
}

export interface DailyStats {
  caloriesConsumed: number
  caloriesTarget: number
  proteinConsumed: number
  proteinTarget: number
  workoutsCompleted: number
}

export interface RoutineItem {
  exercise: string
  sets: number
  reps: string
  target: string
}

export interface MealPlanItem {
  meal: string
  calories: number
  protein: number
}
