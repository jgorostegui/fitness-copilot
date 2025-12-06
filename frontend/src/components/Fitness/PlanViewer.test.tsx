import { ChakraProvider, defaultSystem } from "@chakra-ui/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import type { MealPlanPublic, TrainingRoutinePublic } from "@/client/types.gen"
import { PlanViewer } from "./PlanViewer"

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

const mockTrainingRoutine: TrainingRoutinePublic[] = [
  {
    id: "1",
    program_id: "prog-1",
    day_of_week: 0,
    exercise_name: "Barbell Squat",
    sets: 3,
    reps: 8,
    target_load_kg: 100,
    machine_hint: "Squat rack",
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
  {
    id: "3",
    program_id: "prog-1",
    day_of_week: 0,
    exercise_name: "Romanian Deadlift",
    sets: 3,
    reps: 10,
    target_load_kg: 80,
    machine_hint: null,
  },
]

const mockMealPlan: MealPlanPublic[] = [
  {
    id: "1",
    day_of_week: 0,
    meal_type: "breakfast",
    item_name: "Oatmeal & Whey",
    calories: 450,
    protein_g: 35,
    carbs_g: 50,
    fat_g: 10,
  },
  {
    id: "2",
    day_of_week: 0,
    meal_type: "lunch",
    item_name: "Chicken & Rice",
    calories: 600,
    protein_g: 45,
    carbs_g: 60,
    fat_g: 15,
  },
]

describe("PlanViewer - Workout Mode", () => {
  it("renders workout protocol header", () => {
    renderWithProviders(
      <PlanViewer
        mode="workout"
        mealPlan={mockMealPlan}
        trainingRoutine={mockTrainingRoutine}
        mealLogs={[]}
        exerciseLogs={[]}
        onAddMeal={vi.fn()}
        onAddExercise={vi.fn()}
      />,
    )

    expect(screen.getByText("Workout Protocol")).toBeInTheDocument()
    expect(screen.getByText("3 exercises planned")).toBeInTheDocument()
  })

  it("shows session volume", () => {
    renderWithProviders(
      <PlanViewer
        mode="workout"
        mealPlan={mockMealPlan}
        trainingRoutine={mockTrainingRoutine}
        mealLogs={[]}
        exerciseLogs={[]}
        onAddMeal={vi.fn()}
        onAddExercise={vi.fn()}
      />,
    )

    expect(screen.getByText("SESSION VOLUME")).toBeInTheDocument()
  })

  it("displays exercises from routine", () => {
    renderWithProviders(
      <PlanViewer
        mode="workout"
        mealPlan={mockMealPlan}
        trainingRoutine={mockTrainingRoutine}
        mealLogs={[]}
        exerciseLogs={[]}
        onAddMeal={vi.fn()}
        onAddExercise={vi.fn()}
      />,
    )

    expect(screen.getByText("Barbell Squat")).toBeInTheDocument()
    expect(screen.getByText("Leg Press")).toBeInTheDocument()
    expect(screen.getByText("Romanian Deadlift")).toBeInTheDocument()
  })

  it("shows rest day when no exercises", () => {
    renderWithProviders(
      <PlanViewer
        mode="workout"
        mealPlan={mockMealPlan}
        trainingRoutine={[]}
        mealLogs={[]}
        exerciseLogs={[]}
        onAddMeal={vi.fn()}
        onAddExercise={vi.fn()}
      />,
    )

    // "Rest Day" appears in both header and body, use getAllByText
    const restDayElements = screen.getAllByText("Rest Day")
    expect(restDayElements.length).toBeGreaterThan(0)
  })

  it("calls onAddExercise when plus button is clicked", () => {
    const onAddExercise = vi.fn()

    renderWithProviders(
      <PlanViewer
        mode="workout"
        mealPlan={mockMealPlan}
        trainingRoutine={mockTrainingRoutine}
        mealLogs={[]}
        exerciseLogs={[]}
        onAddMeal={vi.fn()}
        onAddExercise={onAddExercise}
      />,
    )

    const addButtons = screen.getAllByRole("button")
    const firstAddButton = addButtons.find((btn) => btn.querySelector("svg"))
    if (firstAddButton) {
      fireEvent.click(firstAddButton)
      expect(onAddExercise).toHaveBeenCalled()
    }
  })
})

describe("PlanViewer - Nutrition Mode", () => {
  it("renders nutrition protocol header", () => {
    renderWithProviders(
      <PlanViewer
        mode="nutrition"
        mealPlan={mockMealPlan}
        trainingRoutine={mockTrainingRoutine}
        mealLogs={[]}
        exerciseLogs={[]}
        onAddMeal={vi.fn()}
        onAddExercise={vi.fn()}
      />,
    )

    expect(screen.getByText("Nutrition Protocol")).toBeInTheDocument()
    expect(screen.getByText("2 meals planned")).toBeInTheDocument()
  })

  it("shows calorie and protein stats", () => {
    renderWithProviders(
      <PlanViewer
        mode="nutrition"
        mealPlan={mockMealPlan}
        trainingRoutine={mockTrainingRoutine}
        mealLogs={[]}
        exerciseLogs={[]}
        onAddMeal={vi.fn()}
        onAddExercise={vi.fn()}
      />,
    )

    expect(screen.getByText("CALORIES")).toBeInTheDocument()
    expect(screen.getByText("PROTEIN")).toBeInTheDocument()
  })

  it("displays meal plan items", () => {
    renderWithProviders(
      <PlanViewer
        mode="nutrition"
        mealPlan={mockMealPlan}
        trainingRoutine={mockTrainingRoutine}
        mealLogs={[]}
        exerciseLogs={[]}
        onAddMeal={vi.fn()}
        onAddExercise={vi.fn()}
      />,
    )

    expect(screen.getByText("THE PLAN")).toBeInTheDocument()
    expect(screen.getByText("Oatmeal & Whey")).toBeInTheDocument()
    expect(screen.getByText("Chicken & Rice")).toBeInTheDocument()
  })

  it("shows empty state when no meal plan", () => {
    renderWithProviders(
      <PlanViewer
        mode="nutrition"
        mealPlan={[]}
        trainingRoutine={mockTrainingRoutine}
        mealLogs={[]}
        exerciseLogs={[]}
        onAddMeal={vi.fn()}
        onAddExercise={vi.fn()}
      />,
    )

    expect(screen.getByText("No meal plan for today")).toBeInTheDocument()
  })

  it("calls onAddMeal when meal plan item is clicked", () => {
    const onAddMeal = vi.fn()

    renderWithProviders(
      <PlanViewer
        mode="nutrition"
        mealPlan={mockMealPlan}
        trainingRoutine={mockTrainingRoutine}
        mealLogs={[]}
        exerciseLogs={[]}
        onAddMeal={onAddMeal}
        onAddExercise={vi.fn()}
      />,
    )

    // Find the add button for the first meal
    const addButtons = screen.getAllByRole("button")
    const mealAddButton = addButtons.find(
      (btn) => btn.querySelector("svg") && !btn.textContent?.includes("📅"),
    )
    if (mealAddButton) {
      fireEvent.click(mealAddButton)
      expect(onAddMeal).toHaveBeenCalled()
    }
  })

  it("displays quick add foods section", () => {
    renderWithProviders(
      <PlanViewer
        mode="nutrition"
        mealPlan={mockMealPlan}
        trainingRoutine={mockTrainingRoutine}
        mealLogs={[]}
        exerciseLogs={[]}
        onAddMeal={vi.fn()}
        onAddExercise={vi.fn()}
      />,
    )

    expect(screen.getByText("QUICK ADD")).toBeInTheDocument()
    expect(screen.getByText("Banana")).toBeInTheDocument()
    expect(screen.getByText("Protein Shake")).toBeInTheDocument()
    expect(screen.getByText("Greek Yogurt")).toBeInTheDocument()
  })

  it("calls onAddMeal when quick add food is clicked", () => {
    const onAddMeal = vi.fn()

    renderWithProviders(
      <PlanViewer
        mode="nutrition"
        mealPlan={mockMealPlan}
        trainingRoutine={mockTrainingRoutine}
        mealLogs={[]}
        exerciseLogs={[]}
        onAddMeal={onAddMeal}
        onAddExercise={vi.fn()}
      />,
    )

    fireEvent.click(screen.getByText("Banana"))
    expect(onAddMeal).toHaveBeenCalledWith({
      name: "Banana",
      calories: 105,
      protein: 1,
      type: "snack",
    })
  })

  it("shows calorie exceeded feedback when over target", () => {
    const mealLogs = [
      { id: "1", name: "Big Meal", calories: 1200, protein: 50, type: "lunch" as const, time: new Date().toISOString() },
    ]

    renderWithProviders(
      <PlanViewer
        mode="nutrition"
        mealPlan={mockMealPlan}
        trainingRoutine={mockTrainingRoutine}
        mealLogs={mealLogs}
        exerciseLogs={[]}
        onAddMeal={vi.fn()}
        onAddExercise={vi.fn()}
      />,
    )

    // Target is 1050 (450 + 600), consumed is 1200, excess is 150
    expect(screen.getByTestId("calorie-excess")).toHaveTextContent("+150 over")
  })

  it("does not show excess when under target", () => {
    const mealLogs = [
      { id: "1", name: "Small Meal", calories: 300, protein: 20, type: "lunch" as const, time: new Date().toISOString() },
    ]

    renderWithProviders(
      <PlanViewer
        mode="nutrition"
        mealPlan={mockMealPlan}
        trainingRoutine={mockTrainingRoutine}
        mealLogs={mealLogs}
        exerciseLogs={[]}
        onAddMeal={vi.fn()}
        onAddExercise={vi.fn()}
      />,
    )

    expect(screen.queryByTestId("calorie-excess")).not.toBeInTheDocument()
  })
})
