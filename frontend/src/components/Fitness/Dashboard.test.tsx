import { render, screen } from "@testing-library/react"
import { describe, it, expect } from "vitest"
import { ChakraProvider, defaultSystem } from "@chakra-ui/react"
import { Dashboard } from "./Dashboard"
import type { DailyStats, MealLog, ExerciseLog, UserProfile } from "@/types/fitness"

const renderWithChakra = (ui: React.ReactElement) => {
  return render(<ChakraProvider value={defaultSystem}>{ui}</ChakraProvider>)
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
  it("renders the monitor header", () => {
    renderWithChakra(
      <Dashboard
        stats={mockStats}
        mealLogs={[]}
        exerciseLogs={[]}
        profile={mockProfile}
      />,
    )

    expect(screen.getByText("Monitor")).toBeInTheDocument()
  })

  it("displays the plan badge", () => {
    renderWithChakra(
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
    renderWithChakra(
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
    renderWithChakra(
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
    renderWithChakra(
      <Dashboard
        stats={mockStats}
        mealLogs={[]}
        exerciseLogs={[]}
        profile={mockProfile}
      />,
    )

    expect(screen.getByText("2")).toBeInTheDocument()
    expect(screen.getByText("Completed")).toBeInTheDocument()
  })

  it("shows empty state when no logs", () => {
    renderWithChakra(
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

    renderWithChakra(
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

    renderWithChakra(
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
})
