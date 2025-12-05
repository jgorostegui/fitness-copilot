import { ChakraProvider, defaultSystem } from "@chakra-ui/react"
import { fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import type { UserProfile } from "@/types/fitness"
import { Profile } from "./Profile"

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

describe("Profile", () => {
  it("renders the settings header", () => {
    const onUpdate = vi.fn()
    const onReset = vi.fn()

    renderWithChakra(
      <Profile profile={mockProfile} onUpdate={onUpdate} onReset={onReset} />,
    )

    expect(screen.getByText("Settings")).toBeInTheDocument()
  })

  it("displays user avatar section", () => {
    const onUpdate = vi.fn()
    const onReset = vi.fn()

    renderWithChakra(
      <Profile profile={mockProfile} onUpdate={onUpdate} onReset={onReset} />,
    )

    expect(screen.getByText("Operator")).toBeInTheDocument()
    expect(screen.getByText("Fitness Copilot User")).toBeInTheDocument()
  })

  it("shows appearance toggle", () => {
    const onUpdate = vi.fn()
    const onReset = vi.fn()

    renderWithChakra(
      <Profile profile={mockProfile} onUpdate={onUpdate} onReset={onReset} />,
    )

    expect(screen.getByText("APPEARANCE")).toBeInTheDocument()
    expect(screen.getByText("Light")).toBeInTheDocument()
    expect(screen.getByText("Dark")).toBeInTheDocument()
  })

  it("shows biometrics section", () => {
    const onUpdate = vi.fn()
    const onReset = vi.fn()

    renderWithChakra(
      <Profile profile={mockProfile} onUpdate={onUpdate} onReset={onReset} />,
    )

    expect(screen.getByText("BIOMETRICS")).toBeInTheDocument()
    expect(screen.getByText("Weight")).toBeInTheDocument()
    expect(screen.getByText("Height")).toBeInTheDocument()
  })

  it("shows strategy section", () => {
    const onUpdate = vi.fn()
    const onReset = vi.fn()

    renderWithChakra(
      <Profile profile={mockProfile} onUpdate={onUpdate} onReset={onReset} />,
    )

    expect(screen.getByText("STRATEGY")).toBeInTheDocument()
    expect(screen.getByText("Current Phase")).toBeInTheDocument()
  })

  it("calls onReset when reset button is clicked", () => {
    const onUpdate = vi.fn()
    const onReset = vi.fn()

    renderWithChakra(
      <Profile profile={mockProfile} onUpdate={onUpdate} onReset={onReset} />,
    )

    const resetButton = screen.getByText("Reset Profile Data")
    fireEvent.click(resetButton)

    expect(onReset).toHaveBeenCalled()
  })

  it("calls onUpdate when save is clicked", () => {
    const onUpdate = vi.fn()
    const onReset = vi.fn()

    renderWithChakra(
      <Profile profile={mockProfile} onUpdate={onUpdate} onReset={onReset} />,
    )

    const saveButton = screen.getByText("Save")
    fireEvent.click(saveButton)

    expect(onUpdate).toHaveBeenCalledWith(
      expect.objectContaining({
        weight: 80,
        height: 180,
        plan: "maintain",
      }),
    )
  })
})
