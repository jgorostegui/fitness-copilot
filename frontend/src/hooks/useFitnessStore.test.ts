import { act, renderHook } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import { useFitnessStore } from "./useFitnessStore"

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key]
    }),
    clear: vi.fn(() => {
      store = {}
    }),
  }
})()

Object.defineProperty(window, "localStorage", { value: localStorageMock })

describe("useFitnessStore", () => {
  beforeEach(() => {
    localStorageMock.clear()
    vi.clearAllMocks()
  })

  it("starts with null profile", () => {
    const { result } = renderHook(() => useFitnessStore())
    expect(result.current.profile).toBeNull()
  })

  it("sets and persists profile", () => {
    const { result } = renderHook(() => useFitnessStore())

    act(() => {
      result.current.setProfile({
        weight: 80,
        height: 180,
        plan: "maintain",
        theme: "light",
        onboardingComplete: true,
      })
    })

    expect(result.current.profile).not.toBeNull()
    expect(result.current.profile?.weight).toBe(80)
    expect(localStorageMock.setItem).toHaveBeenCalled()
  })

  it("resets profile and clears data", () => {
    const { result } = renderHook(() => useFitnessStore())

    act(() => {
      result.current.setProfile({
        weight: 80,
        height: 180,
        plan: "maintain",
        theme: "light",
        onboardingComplete: true,
      })
    })

    act(() => {
      result.current.resetProfile()
    })

    expect(result.current.profile).toBeNull()
    expect(localStorageMock.removeItem).toHaveBeenCalled()
  })

  it("adds meal log", () => {
    const { result } = renderHook(() => useFitnessStore())

    act(() => {
      result.current.addMealLog({
        name: "Banana",
        calories: 105,
        protein: 1,
        type: "snack",
      })
    })

    expect(result.current.mealLogs).toHaveLength(1)
    expect(result.current.mealLogs[0].name).toBe("Banana")
  })

  it("adds exercise log", () => {
    const { result } = renderHook(() => useFitnessStore())

    act(() => {
      result.current.addExerciseLog({
        name: "Leg Press",
        sets: 3,
        reps: 10,
        weight: 100,
      })
    })

    expect(result.current.exerciseLogs).toHaveLength(1)
    expect(result.current.exerciseLogs[0].name).toBe("Leg Press")
  })

  it("calculates stats correctly", () => {
    const { result } = renderHook(() => useFitnessStore())

    act(() => {
      result.current.setProfile({
        weight: 80,
        height: 180,
        plan: "maintain",
        theme: "light",
        onboardingComplete: true,
      })
    })

    act(() => {
      result.current.addMealLog({
        name: "Banana",
        calories: 105,
        protein: 1,
        type: "snack",
      })
      result.current.addMealLog({
        name: "Shake",
        calories: 130,
        protein: 24,
        type: "snack",
      })
    })

    expect(result.current.stats.caloriesConsumed).toBe(235)
    expect(result.current.stats.proteinConsumed).toBe(25)
    expect(result.current.stats.caloriesTarget).toBe(2400) // maintain target
  })

  it("handles chat action for food", () => {
    const { result } = renderHook(() => useFitnessStore())

    act(() => {
      result.current.handleChatAction({
        type: "log_food",
        data: { name: "Apple", calories: 95, protein: 0 },
      })
    })

    expect(result.current.mealLogs).toHaveLength(1)
    expect(result.current.mealLogs[0].name).toBe("Apple")
  })

  it("handles chat action for exercise", () => {
    const { result } = renderHook(() => useFitnessStore())

    act(() => {
      result.current.handleChatAction({
        type: "log_exercise",
        data: { name: "Squat", sets: 3, reps: 8, weight: 80 },
      })
    })

    expect(result.current.exerciseLogs).toHaveLength(1)
    expect(result.current.exerciseLogs[0].name).toBe("Squat")
  })

  it("initializes chat history with welcome message", () => {
    const { result } = renderHook(() => useFitnessStore())

    expect(result.current.chatHistory).toHaveLength(1)
    expect(result.current.chatHistory[0].sender).toBe("ai")
  })
})
