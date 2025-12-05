import { useCallback, useMemo, useState } from "react"
import { TARGET_CALORIES, TARGET_PROTEIN } from "@/constants/fitness"
import type {
  DailyStats,
  ExerciseLog,
  MealLog,
  Message,
  UserProfile,
} from "@/types/fitness"

const STORAGE_KEY = "fitness_profile"

const loadProfile = (): UserProfile | null => {
  const stored = localStorage.getItem(STORAGE_KEY)
  return stored ? JSON.parse(stored) : null
}

const saveProfile = (profile: UserProfile) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(profile))
}

export const useFitnessStore = () => {
  const [profile, setProfileState] = useState<UserProfile | null>(loadProfile)
  const [mealLogs, setMealLogs] = useState<MealLog[]>([])
  const [exerciseLogs, setExerciseLogs] = useState<ExerciseLog[]>([])
  const [chatHistory, setChatHistory] = useState<Message[]>([
    {
      id: "init",
      text: "I'm your fitness copilot. Send me a message, photo, or voice note.",
      sender: "ai",
      timestamp: new Date(),
    },
  ])

  const setProfile = useCallback((newProfile: UserProfile) => {
    setProfileState(newProfile)
    saveProfile(newProfile)
  }, [])

  const resetProfile = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY)
    setProfileState(null)
    setMealLogs([])
    setExerciseLogs([])
    setChatHistory([
      {
        id: "init",
        text: "I'm your fitness copilot. Send me a message, photo, or voice note.",
        sender: "ai",
        timestamp: new Date(),
      },
    ])
  }, [])

  const stats: DailyStats = useMemo(() => {
    if (!profile) {
      return {
        caloriesConsumed: 0,
        caloriesTarget: 2000,
        proteinConsumed: 0,
        proteinTarget: 150,
        workoutsCompleted: 0,
      }
    }

    return {
      caloriesConsumed: mealLogs.reduce((acc, log) => acc + log.calories, 0),
      caloriesTarget: TARGET_CALORIES[profile.plan],
      proteinConsumed: mealLogs.reduce((acc, log) => acc + log.protein, 0),
      proteinTarget: TARGET_PROTEIN[profile.plan],
      workoutsCompleted: exerciseLogs.length,
    }
  }, [profile, mealLogs, exerciseLogs])

  const addMealLog = useCallback(
    (meal: Omit<MealLog, "id" | "time">) => {
      const newMeal: MealLog = {
        ...meal,
        id: Date.now().toString(),
        time: new Date().toISOString(),
      }
      setMealLogs((prev) => [...prev, newMeal])
    },
    [],
  )

  const addExerciseLog = useCallback(
    (exercise: Omit<ExerciseLog, "id" | "time">) => {
      const newExercise: ExerciseLog = {
        ...exercise,
        id: Date.now().toString(),
        time: new Date().toISOString(),
      }
      setExerciseLogs((prev) => [...prev, newExercise])
    },
    [],
  )

  const handleChatAction = useCallback(
    (action: { type: string; data?: Record<string, unknown> }) => {
      if (!action?.data) return

      if (action.type === "log_food") {
        addMealLog({
          name: (action.data.name as string) || "Food Item",
          calories: (action.data.calories as number) || 0,
          protein: (action.data.protein as number) || 0,
          type: "snack",
        })
      } else if (action.type === "log_exercise") {
        addExerciseLog({
          name: (action.data.name as string) || "Exercise",
          sets: (action.data.sets as number) || 0,
          reps: (action.data.reps as number) || 0,
          weight: (action.data.weight as number) || 0,
        })
      }
    },
    [addMealLog, addExerciseLog],
  )

  return {
    profile,
    setProfile,
    resetProfile,
    stats,
    mealLogs,
    exerciseLogs,
    addMealLog,
    addExerciseLog,
    chatHistory,
    setChatHistory,
    handleChatAction,
  }
}
