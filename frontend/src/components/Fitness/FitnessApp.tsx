import { Box, Flex, Spinner, Text } from "@chakra-ui/react"
import { useCallback, useState } from "react"
import { useAuth } from "@/hooks/useAuth"
import { useChat } from "@/hooks/useChat"
import { useFitnessStore } from "@/hooks/useFitnessStore"
import { useLogs } from "@/hooks/useLogs"
import { useMealPlan } from "@/hooks/useMealPlan"
import { useProfile } from "@/hooks/useProfile"
import { useSummary } from "@/hooks/useSummary"
import { useTrainingRoutine } from "@/hooks/useTrainingRoutine"
import type {
  DailyStats,
  ExerciseLog,
  MealLog,
  UserProfile,
} from "@/types/fitness"
import { BottomNav } from "./BottomNav"
import { ChatInterface } from "./ChatInterface"
import { Dashboard } from "./Dashboard"
import { DemoLogin } from "./DemoLogin"
import { Onboarding } from "./Onboarding"
import { PlanViewer } from "./PlanViewer"
import { Profile } from "./Profile"

type Tab = "monitor" | "workout" | "chat" | "nutrition" | "profile"

const FullScreenLoader = () => (
  <Flex h="100vh" w="full" align="center" justify="center" bg="gray.50">
    <Flex direction="column" align="center" gap={4}>
      <Spinner size="xl" color="blue.500" />
      <Text color="gray.500">Loading...</Text>
    </Flex>
  </Flex>
)

export const FitnessApp = () => {
  const [activeTab, setActiveTab] = useState<Tab>("monitor")
  const {
    isAuthenticated,
    isLoading: authLoading,
    loginDemo,
    logout,
  } = useAuth()
  const {
    profile: apiProfile,
    isLoading: profileLoading,
    updateProfileAsync,
  } = useProfile(isAuthenticated)
  const { profile, setProfile, resetProfile } = useFitnessStore()

  // Use API hooks for real data
  const { summary } = useSummary(isAuthenticated)
  const {
    mealLogs: apiMealLogs,
    exerciseLogs: apiExerciseLogs,
    logMeal,
    logExercise,
  } = useLogs(isAuthenticated)
  const { sendMessage, clearMessages } = useChat(isAuthenticated)
  const { mealPlan, isLoading: mealPlanLoading } = useMealPlan(isAuthenticated)
  const { trainingRoutine, isLoading: trainingLoading } =
    useTrainingRoutine(isAuthenticated)

  // Quick-add handlers that use direct log API (not chat)
  const addMealLog = useCallback(
    (meal: Omit<MealLog, "id" | "time">) => {
      logMeal({
        meal_name: meal.name,
        meal_type: meal.type || "snack",
        calories: meal.calories,
        protein_g: meal.protein,
        carbs_g: 0,
        fat_g: 0,
      })
    },
    [logMeal],
  )

  const addExerciseLog = useCallback(
    (exercise: Omit<ExerciseLog, "id" | "time">) => {
      logExercise({
        exercise_name: exercise.name,
        sets: exercise.sets,
        reps: exercise.reps,
        weight_kg: exercise.weight,
      })
    },
    [logExercise],
  )

  // Map API logs to local types
  const mealLogs: MealLog[] = apiMealLogs.map((log) => ({
    id: log.id,
    name: log.mealName,
    calories: log.calories,
    protein: log.proteinG,
    time: log.loggedAt,
    type: log.mealType as MealLog["type"],
  }))

  const exerciseLogs: ExerciseLog[] = apiExerciseLogs.map((log) => ({
    id: log.id,
    name: log.exerciseName,
    sets: log.sets,
    reps: log.reps,
    weight: log.weightKg,
    time: log.loggedAt,
  }))

  // Build stats from API summary
  const stats: DailyStats = {
    caloriesConsumed: summary?.caloriesConsumed ?? 0,
    caloriesTarget: summary?.caloriesTarget ?? 2000,
    proteinConsumed: summary?.proteinConsumed ?? 0,
    proteinTarget: summary?.proteinTarget ?? 150,
    workoutsCompleted: summary?.workoutsCompleted ?? 0,
  }

  // Show demo login if not authenticated
  if (!isAuthenticated) {
    return <DemoLogin onLogin={loginDemo} isLoading={authLoading} />
  }

  // Show loader while fetching profile
  if (profileLoading) {
    return <FullScreenLoader />
  }

  // Show onboarding if profile exists but onboarding not complete
  if (apiProfile && !apiProfile.onboardingComplete) {
    return (
      <Onboarding
        initialProfile={apiProfile}
        onComplete={async (localProfile) => {
          // Update API profile with onboarding_complete: true
          await updateProfileAsync({
            weight_kg: localProfile.weight,
            height_cm: localProfile.height,
            onboarding_complete: true,
          })
          setProfile(localProfile)
        }}
        onBack={() => {
          // Go back to demo login to choose a different persona
          resetProfile()
          logout()
        }}
      />
    )
  }

  // Build current profile from API or local state
  // If API profile has completed onboarding but local profile is missing, build from API
  const currentProfile: UserProfile | null =
    profile ??
    (apiProfile?.onboardingComplete
      ? {
          weight: apiProfile.weightKg ?? 80,
          height: apiProfile.heightCm ?? 180,
          plan: apiProfile.goalMethod?.includes("cut")
            ? "cut"
            : apiProfile.goalMethod?.includes("gain")
              ? "bulk"
              : "maintain",
          theme: "light",
          onboardingComplete: true,
        }
      : null)

  // Fallback to onboarding if no profile available
  if (!currentProfile) {
    return <Onboarding onComplete={setProfile} />
  }

  return (
    <Box
      h="100vh"
      w="full"
      bg="gray.50"
      color="gray.900"
      position="relative"
      overflow="hidden"
    >
      <Box h="full" pb={16}>
        {activeTab === "monitor" && (
          <Dashboard
            stats={stats}
            mealLogs={mealLogs}
            exerciseLogs={exerciseLogs}
            profile={currentProfile}
            trainingRoutine={trainingRoutine}
          />
        )}
        {activeTab === "workout" && (
          <PlanViewer
            mode="workout"
            mealPlan={mealPlan}
            trainingRoutine={trainingRoutine}
            mealLogs={mealLogs}
            exerciseLogs={exerciseLogs}
            isLoading={trainingLoading}
            onAddMeal={addMealLog}
            onAddExercise={addExerciseLog}
          />
        )}
        {activeTab === "chat" && <ChatInterface />}
        {activeTab === "nutrition" && (
          <PlanViewer
            mode="nutrition"
            mealPlan={mealPlan}
            trainingRoutine={trainingRoutine}
            mealLogs={mealLogs}
            exerciseLogs={exerciseLogs}
            isLoading={mealPlanLoading}
            onAddMeal={addMealLog}
            onAddExercise={addExerciseLog}
          />
        )}
        {activeTab === "profile" && (
          <Profile
            profile={currentProfile}
            onUpdate={setProfile}
            onReset={() => {
              // Clear chat history (which also clears logs via the hook)
              clearMessages()
              // Also send reset to clear today's logs
              sendMessage({ content: "reset" })
              resetProfile()
            }}
            onLogout={() => {
              resetProfile() // Clear local state first
              logout() // Then clear auth token
            }}
          />
        )}
      </Box>
      <BottomNav activeTab={activeTab} onTabChange={setActiveTab} />
    </Box>
  )
}
