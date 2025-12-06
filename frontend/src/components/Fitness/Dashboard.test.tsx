import { ChakraProvider, defaultSystem } from "@chakra-ui/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import type {
  DailyStats,
  ExerciseLog,
  MealLog,
  UserProfile,
} from "@/types/fitness"
import { Dashboard } from "./Dashboard"

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
})

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <ChakraProvider value={defaultSystem}>{ui}</ChakraProvider>
    </QueryClientProvider>,
  )
}

const mockProfile: UserProfile = {
  weight: 80,
  height: 180,
  plan: "maintain",
  theme: "light",
  onboardingComplete: true,
}

const mockStats: DailyStats = {
  caloriesConsumed: 1200,
  caloriesTarget: 2400,
  proteinConsumed: 80,
  proteinTarget: 160,
  workoutsCompleted: 2,
}

describe("Dashboard", () => {
  it("renders the dashboard header", () => {
    renderWithProviders(
      <Dashboard
        stats={mockStats}
        mealLogs={[]}
        exerciseLogs={[]}
        profile={mockProfile}
      />,
    )

    expect(screen.getByText("Dashboard")).toBeInTheDocument()
  })

  it("displays the plan badge", () => {
    renderWithProviders(
      <Dashboard
        stats={mockStats}
        mealLogs={[]}
        exerciseLogs={[]}
        profile={mockProfile}
      />,
    )

    expect(screen.getByText("MAINTAIN")).toBeInTheDocument()
  })

  it("shows calorie stats", () => {
    renderWithProviders(
      <Dashboard
        stats={mockStats}
        mealLogs={[]}
        exerciseLogs={[]}
        profile={mockProfile}
      />,
    )

    expect(screen.getByText("1200")).toBeInTheDocument()
    expect(screen.getByText("/ 2400")).toBeInTheDocument()
  })

  it("shows protein stats", () => {
    renderWithProviders(
      <Dashboard
        stats={mockStats}
        mealLogs={[]}
        exerciseLogs={[]}
        profile={mockProfile}
      />,
    )

    // Protein is displayed as "80" with "g" suffix and "/ 160g" separately
    expect(screen.getByText("Protein (g)")).toBeInTheDocument()
  })

  it("shows exercises completed count", () => {
    renderWithProviders(
      <Dashboard
        stats={mockStats}
        mealLogs={[]}
        exerciseLogs={[]}
        profile={mockProfile}
      />,
    )

    // Check for the Sets label in the circular progress
    expect(screen.getByText("Sets")).toBeInTheDocument()
    // Check for the Completed label in the card
    expect(screen.getByText("Completed")).toBeInTheDocument()
  })

  it("shows empty state when no logs", () => {
    renderWithProviders(
      <Dashboard
        stats={mockStats}
        mealLogs={[]}
        exerciseLogs={[]}
        profile={mockProfile}
      />,
    )

    expect(
      screen.getByText("No activity yet. Use Chat to log your day."),
    ).toBeInTheDocument()
  })

  it("displays meal logs", () => {
    const mealLogs: MealLog[] = [
      {
        id: "1",
        name: "Banana",
        calories: 105,
        protein: 1,
        time: new Date().toISOString(),
        type: "snack",
      },
    ]

    renderWithProviders(
      <Dashboard
        stats={mockStats}
        mealLogs={mealLogs}
        exerciseLogs={[]}
        profile={mockProfile}
      />,
    )

    expect(screen.getByText("Banana")).toBeInTheDocument()
    expect(screen.getByText("105")).toBeInTheDocument()
  })

  it("displays exercise logs", () => {
    const exerciseLogs: ExerciseLog[] = [
      {
        id: "1",
        name: "Leg Press",
        sets: 3,
        reps: 10,
        weight: 100,
        time: new Date().toISOString(),
      },
    ]

    renderWithProviders(
      <Dashboard
        stats={mockStats}
        mealLogs={[]}
        exerciseLogs={exerciseLogs}
        profile={mockProfile}
      />,
    )

    expect(screen.getByText("Leg Press")).toBeInTheDocument()
    expect(screen.getByText("100kg")).toBeInTheDocument()
  })

  it("shows rest day when no training routine", () => {
    renderWithProviders(
      <Dashboard
        stats={mockStats}
        mealLogs={[]}
        exerciseLogs={[]}
        profile={mockProfile}
        trainingRoutine={[]}
      />,
    )

    expect(screen.getByText("Rest Day")).toBeInTheDocument()
    expect(screen.getByText("No workout scheduled")).toBeInTheDocument()
  })

  it("shows training plan info when routine exists", () => {
    const trainingRoutine = [
      {
        id: "1",
        program_id: "prog-1",
        day_of_week: 0,
        exercise_name: "Squat",
        sets: 3,
        reps: 8,
        target_load_kg: 100,
        machine_hint: null,
      },
      {
        id: "2",
        program_id: "prog-1",
        day_of_week: 0,
        exercise_name: "Leg Press",
        sets: 3,
        reps: 12,
        target_load_kg: 150,
        machine_hint: null,
      },
    ]

    renderWithProviders(
      <Dashboard
        stats={mockStats}
        mealLogs={[]}
        exerciseLogs={[]}
        profile={mockProfile}
        trainingRoutine={trainingRoutine}
      />,
    )

    expect(screen.getByText("2-EXERCISE PLAN")).toBeInTheDocument()
    expect(screen.getByText("6 sets total")).toBeInTheDocument()
  })
})
