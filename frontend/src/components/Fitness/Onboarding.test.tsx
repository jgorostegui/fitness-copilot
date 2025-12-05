import { render, screen, fireEvent } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import { ChakraProvider, defaultSystem } from "@chakra-ui/react"
import { Onboarding } from "./Onboarding"

const renderWithChakra = (ui: React.ReactElement) => {
  return render(<ChakraProvider value={defaultSystem}>{ui}</ChakraProvider>)
}

describe("Onboarding", () => {
  it("renders the setup form", () => {
    const onComplete = vi.fn()
    renderWithChakra(<Onboarding onComplete={onComplete} />)

    expect(screen.getByText("Setup Profile")).toBeInTheDocument()
    expect(screen.getByText("WEIGHT (KG)")).toBeInTheDocument()
    expect(screen.getByText("HEIGHT (CM)")).toBeInTheDocument()
    expect(screen.getByText("GOAL")).toBeInTheDocument()
  })

  it("renders goal buttons", () => {
    const onComplete = vi.fn()
    renderWithChakra(<Onboarding onComplete={onComplete} />)

    expect(screen.getByText("Cut")).toBeInTheDocument()
    expect(screen.getByText("Maintain")).toBeInTheDocument()
    expect(screen.getByText("Bulk")).toBeInTheDocument()
  })

  it("calls onComplete with profile data on submit", () => {
    const onComplete = vi.fn()
    renderWithChakra(<Onboarding onComplete={onComplete} />)

    const submitButton = screen.getByText("Start Journey →")
    fireEvent.click(submitButton)

    expect(onComplete).toHaveBeenCalledWith({
      weight: 80,
      height: 180,
      plan: "maintain",
      theme: "light",
      onboardingComplete: true,
    })
  })

  it("allows changing the goal", () => {
    const onComplete = vi.fn()
    renderWithChakra(<Onboarding onComplete={onComplete} />)

    const cutButton = screen.getByText("Cut")
    fireEvent.click(cutButton)

    const submitButton = screen.getByText("Start Journey →")
    fireEvent.click(submitButton)

    expect(onComplete).toHaveBeenCalledWith(
      expect.objectContaining({ plan: "cut" }),
    )
  })
})
