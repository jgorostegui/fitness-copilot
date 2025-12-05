import { useCallback, useEffect, useState } from "react"
import { useQueryClient } from "@tanstack/react-query"
import { client } from "@/client/client.gen"
import { Demo } from "@/client"

const TOKEN_KEY = "fitness_copilot_token"

export type DemoPersona = "cut" | "bulk" | "maintain"

export interface UseAuthReturn {
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  loginDemo: (persona: DemoPersona) => Promise<void>
  logout: () => void
}

/**
 * Hook for managing authentication state and demo login.
 *
 * Stores JWT token in localStorage and configures the API client
 * to use the token for authenticated requests.
 */
export function useAuth(): UseAuthReturn {
  const queryClient = useQueryClient()
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem(TOKEN_KEY),
  )
  const [isLoading, setIsLoading] = useState(false)

  // Configure client with token on mount and when token changes
  useEffect(() => {
    if (token) {
      client.setConfig({
        auth: () => token,
      })
    } else {
      client.setConfig({
        auth: undefined,
      })
    }
  }, [token])

  const loginDemo = useCallback(async (persona: DemoPersona) => {
    setIsLoading(true)
    try {
      const response = await Demo.demoDemoLogin({
        path: { persona },
      })

      if (response.data) {
        const accessToken = response.data.access_token
        localStorage.setItem(TOKEN_KEY, accessToken)
        setToken(accessToken)
      } else {
        throw new Error("Login failed: no token received")
      }
    } finally {
      setIsLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    // Also clear the local fitness profile to ensure clean state on re-login
    localStorage.removeItem("fitness_profile")
    setToken(null)
    // Clear client auth config
    client.setConfig({
      auth: undefined,
    })
    // Clear all cached queries to ensure fresh data on next login
    queryClient.clear()
  }, [queryClient])

  return {
    token,
    isAuthenticated: !!token,
    isLoading,
    loginDemo,
    logout,
  }
}
