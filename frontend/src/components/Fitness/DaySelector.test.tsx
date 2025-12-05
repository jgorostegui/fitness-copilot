import { ChakraProvider, defaultSystem } from "@chakra-ui/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import { DaySelector } from "./DaySelector"

// Mock the Profile API
vi.mock("@/client", () => ({
  Profile: {
    profileGetSimulatedDay: vi.fn(),
    profileUpdateSimulatedDay: vi.fn(),
  },
}))

import { Profile } from "@/client"

const createQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  })

const renderWithProviders = (ui: React.ReactElement) => {
  const queryClient = createQueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      <ChakraProvider value={defaultSystem}>{ui}</ChakraProvider>
    </QueryClientProvider>,
  )
}

describe("DaySelector", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("shows loading state initially", () => {
    vi.mocked(Profile.profileGetSimulatedDay).mockReturnValue(
      new Promise(() => {}), // Never resolves
    )

    renderWithProviders(<DaySelector />)

    expect(screen.getByText("📅 Loading...")).toBeInTheDocument()
  })

  it("displays current day name when loaded", async () => {
    vi.mocked(Profile.profileGetSimulatedDay).mockResolvedValue({
      data: { simulatedDay: 0, dayName: "Monday" },
      error: undefined,
    })

    renderWithProviders(<DaySelector />)

    await waitFor(() => {
      expect(screen.getByText("📅 Monday")).toBeInTheDocument()
    })
  })

  it("displays Wednesday when simulated day is 2", async () => {
    vi.mocked(Profile.profileGetSimulatedDay).mockResolvedValue({
      data: { simulatedDay: 2, dayName: "Wednesday" },
      error: undefined,
    })

    renderWithProviders(<DaySelector />)

    await waitFor(() => {
      expect(screen.getByText("📅 Wednesday")).toBeInTheDocument()
    })
  })

  it("displays Sunday when simulated day is 6", async () => {
    vi.mocked(Profile.profileGetSimulatedDay).mockResolvedValue({
      data: { simulatedDay: 6, dayName: "Sunday" },
      error: undefined,
    })

    renderWithProviders(<DaySelector />)

    await waitFor(() => {
      expect(screen.getByText("📅 Sunday")).toBeInTheDocument()
    })
  })

  it("shows default Monday when no data", async () => {
    vi.mocked(Profile.profileGetSimulatedDay).mockResolvedValue({
      data: undefined,
      error: undefined,
    })

    renderWithProviders(<DaySelector />)

    await waitFor(() => {
      expect(screen.getByText("📅 Monday")).toBeInTheDocument()
    })
  })
})
