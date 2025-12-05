import { useQuery } from "@tanstack/react-query"
import { Summary } from "@/client"
import type { DailySummary } from "@/client/types.gen"

export const SUMMARY_QUERY_KEY = ["summary", "today"]

/**
 * Hook for fetching today's daily summary (calories, protein, workouts).
 */
export function useSummary(enabled = true) {
  const query = useQuery({
    queryKey: SUMMARY_QUERY_KEY,
    queryFn: async () => {
      const response = await Summary.summaryGetTodaysSummary()
      if (response.error) {
        throw response.error
      }
      return response.data as DailySummary
    },
    enabled,
    staleTime: 1000 * 30, // 30 seconds
  })

  return {
    summary: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
  }
}
