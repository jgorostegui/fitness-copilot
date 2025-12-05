import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Logs } from "@/client"
import type {
  DailyLogsResponse,
  ExerciseLogCreate,
  MealLogCreate,
} from "@/client/types.gen"

export const LOGS_QUERY_KEY = ["logs", "today"]
export const SUMMARY_QUERY_KEY = ["summary", "today"]

/**
 * Hook for fetching and creating today's meal and exercise logs.
 */
export function useLogs(enabled = true) {
  const queryClient = useQueryClient()

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
    staleTime: 0, // Always refetch when invalidated
    refetchOnMount: true,
    refetchOnWindowFocus: true,
  })

  const logMealMutation = useMutation({
    mutationFn: async (meal: MealLogCreate) => {
      const response = await Logs.logsLogMeal({ body: meal })
      if (response.error) {
        throw response.error
      }
      return response.data
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: LOGS_QUERY_KEY })
      await queryClient.invalidateQueries({ queryKey: SUMMARY_QUERY_KEY })
    },
  })

  const logExerciseMutation = useMutation({
    mutationFn: async (exercise: ExerciseLogCreate) => {
      const response = await Logs.logsLogExercise({ body: exercise })
      if (response.error) {
        throw response.error
      }
      return response.data
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: LOGS_QUERY_KEY })
      await queryClient.invalidateQueries({ queryKey: SUMMARY_QUERY_KEY })
    },
  })

  return {
    mealLogs: query.data?.mealLogs ?? [],
    exerciseLogs: query.data?.exerciseLogs ?? [],
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
    logMeal: logMealMutation.mutate,
    logMealAsync: logMealMutation.mutateAsync,
    isLoggingMeal: logMealMutation.isPending,
    logExercise: logExerciseMutation.mutate,
    logExerciseAsync: logExerciseMutation.mutateAsync,
    isLoggingExercise: logExerciseMutation.isPending,
  }
}
