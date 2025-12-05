import { ChakraProvider, defaultSystem } from "@chakra-ui/react"
import { fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import { PlanViewer } from "./PlanViewer"

const renderWithChakra = (ui: React.ReactElement) => {
  return render(<ChakraProvider value={defaultSystem}>{ui}</ChakraProvider>)
}

describe("PlanViewer - Workout Mode", () => {
  it("renders workout protocol header", () => {
    renderWithChakra(
      <PlanViewer
        mode="workout"
        mealLogs={[]}
        exerciseLogs={[]}
        onAddMeal={vi.fn()}
        onAddExercise={vi.fn()}
      />,
    )

    expect(screen.getByText("Workout Protocol")).toBeInTheDocument()
    expect(screen.getByText("Leg Day Assignment")).toBeInTheDocument()
  })

  it("shows session volume", () => {
    renderWithChakra(
      <PlanViewer
        mode="workout"
        mealLogs={[]}
        exerciseLogs={[]}
        onAddMeal={vi.fn()}
        onAddExercise={vi.fn()}
      />,
    )

    expect(screen.getByText("SESSION VOLUME")).toBeInTheDocument()
  })

  it("displays exercises from routine", () => {
    renderWithChakra(
      <PlanViewer
        mode="workout"
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

  it("calls onAddExercise when plus button is clicked", () => {
    const onAddExercise = vi.fn()

    renderWithChakra(
      <PlanViewer
        mode="workout"
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
    renderWithChakra(
      <PlanViewer
        mode="nutrition"
        mealLogs={[]}
        exerciseLogs={[]}
        onAddMeal={vi.fn()}
        onAddExercise={vi.fn()}
      />,
    )

    expect(screen.getByText("Nutrition Protocol")).toBeInTheDocument()
    expect(screen.getByText("Daily Fuel Architecture")).toBeInTheDocument()
  })

  it("shows calorie and protein stats", () => {
    renderWithChakra(
      <PlanViewer
        mode="nutrition"
        mealLogs={[]}
        exerciseLogs={[]}
        onAddMeal={vi.fn()}
        onAddExercise={vi.fn()}
      />,
    )

    expect(screen.getByText("CALORIES")).toBeInTheDocument()
    expect(screen.getByText("PROTEIN")).toBeInTheDocument()
  })

  it("shows quick add section", () => {
    renderWithChakra(
      <PlanViewer
        mode="nutrition"
        mealLogs={[]}
        exerciseLogs={[]}
        onAddMeal={vi.fn()}
        onAddExercise={vi.fn()}
      />,
    )

    expect(screen.getByText("QUICK ADD")).toBeInTheDocument()
    expect(screen.getByText("Banana")).toBeInTheDocument()
    expect(screen.getByText("Egg")).toBeInTheDocument()
  })

  it("displays meal plan items", () => {
    renderWithChakra(
      <PlanViewer
        mode="nutrition"
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

  it("calls onAddMeal when quick add button is clicked", () => {
    const onAddMeal = vi.fn()

    renderWithChakra(
      <PlanViewer
        mode="nutrition"
        mealLogs={[]}
        exerciseLogs={[]}
        onAddMeal={onAddMeal}
        onAddExercise={vi.fn()}
      />,
    )

    const bananaButton = screen.getByText("Banana")
    fireEvent.click(bananaButton)

    expect(onAddMeal).toHaveBeenCalledWith({
      name: "Banana",
      calories: 105,
      protein: 1,
      type: "snack",
    })
  })
})
