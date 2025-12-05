import {
  MutationCache,
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query"
import { createRouter, RouterProvider } from "@tanstack/react-router"
import { StrictMode } from "react"
import ReactDOM from "react-dom/client"
import { client } from "./client/client.gen"
import { CustomProvider } from "./components/ui/provider"
import { routeTree } from "./routeTree.gen"

// Configure API client with base URL and auth token
client.setConfig({
  baseUrl: import.meta.env.VITE_API_URL || "http://localhost:8000",
  auth: () => localStorage.getItem("fitness_copilot_token") || "",
})

// Handle API errors globally (401/403 -> logout)
const handleApiError = (error: Error) => {
  // Check if it's an API error with 401/403 status
  if (error && "status" in error) {
    const status = (error as { status: number }).status
    if ([401, 403].includes(status)) {
      localStorage.removeItem("fitness_copilot_token")
      window.location.href = "/"
    }
  }
}

const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: handleApiError,
  }),
  mutationCache: new MutationCache({
    onError: handleApiError,
  }),
})

const router = createRouter({ routeTree })
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router
  }
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <CustomProvider>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>
    </CustomProvider>
  </StrictMode>,
)
