import { useQuery } from "@tanstack/react-query"
import { Logs } from "@/client"
import type { DailyLogsResponse } from "@/client/types.gen"

export const LOGS_QUERY_KEY = ["logs", "today"]

/**
 * Hook for fetching today's meal and exercise logs.
 */
export function useLogs(enabled = true) {
  const query = useQuery({
    queryKey: LOGS_QUERY_KEY,
    queryFn: async () => {
      const response = await Logs.logsGetTodaysLogs()
      if (response.error) {
        throw response.error
      }
      return response.data as DailyLogsResponse
    },
    enabled,
    staleTime: 1000 * 30, // 30 seconds
  })

  return {
    mealLogs: query.data?.mealLogs ?? [],
    exerciseLogs: query.data?.exerciseLogs ?? [],
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
  }
}
