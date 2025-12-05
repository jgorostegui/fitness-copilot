import { ChakraProvider, defaultSystem } from "@chakra-ui/react"
import { fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import { BottomNav } from "./BottomNav"

const renderWithChakra = (ui: React.ReactElement) => {
  return render(<ChakraProvider value={defaultSystem}>{ui}</ChakraProvider>)
}

describe("BottomNav", () => {
  it("renders all navigation tabs", () => {
    renderWithChakra(<BottomNav activeTab="monitor" onTabChange={vi.fn()} />)

    expect(screen.getByText("Monitor")).toBeInTheDocument()
    expect(screen.getByText("Workout")).toBeInTheDocument()
    expect(screen.getByText("Chat")).toBeInTheDocument()
    expect(screen.getByText("Nutrition")).toBeInTheDocument()
    expect(screen.getByText("Profile")).toBeInTheDocument()
  })

  it("calls onTabChange when monitor tab is clicked", () => {
    const onTabChange = vi.fn()
    renderWithChakra(<BottomNav activeTab="chat" onTabChange={onTabChange} />)

    fireEvent.click(screen.getByText("Monitor"))
    expect(onTabChange).toHaveBeenCalledWith("monitor")
  })

  it("calls onTabChange when workout tab is clicked", () => {
    const onTabChange = vi.fn()
    renderWithChakra(
      <BottomNav activeTab="monitor" onTabChange={onTabChange} />,
    )

    fireEvent.click(screen.getByText("Workout"))
    expect(onTabChange).toHaveBeenCalledWith("workout")
  })

  it("calls onTabChange when chat tab is clicked", () => {
    const onTabChange = vi.fn()
    renderWithChakra(
      <BottomNav activeTab="monitor" onTabChange={onTabChange} />,
    )

    // Chat is the center button, find it by its container
    const chatButton =
      screen.getByText("Chat").closest("button") ||
      screen.getByText("Chat").parentElement?.querySelector("button")
    if (chatButton) {
      fireEvent.click(chatButton)
    } else {
      // Fallback: click the text's parent
      fireEvent.click(screen.getByText("Chat").parentElement!)
    }
    expect(onTabChange).toHaveBeenCalledWith("chat")
  })

  it("calls onTabChange when nutrition tab is clicked", () => {
    const onTabChange = vi.fn()
    renderWithChakra(
      <BottomNav activeTab="monitor" onTabChange={onTabChange} />,
    )

    fireEvent.click(screen.getByText("Nutrition"))
    expect(onTabChange).toHaveBeenCalledWith("nutrition")
  })

  it("calls onTabChange when profile tab is clicked", () => {
    const onTabChange = vi.fn()
    renderWithChakra(
      <BottomNav activeTab="monitor" onTabChange={onTabChange} />,
    )

    fireEvent.click(screen.getByText("Profile"))
    expect(onTabChange).toHaveBeenCalledWith("profile")
  })
})
