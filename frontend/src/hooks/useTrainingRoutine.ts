import { useQuery } from "@tanstack/react-query"
import { Plans } from "@/client"

export function useTrainingRoutine(enabled = true) {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["trainingRoutine"],
    queryFn: async () => {
      const response = await Plans.plansGetTodaysTraining()
      if (response.error) {
        throw response.error
      }
      return response.data
    },
    enabled,
  })

  return {
    trainingRoutine: data?.data ?? [],
    isLoading,
    error,
    refetch,
  }
}
