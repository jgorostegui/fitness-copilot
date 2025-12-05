import { useQuery } from "@tanstack/react-query"
import { Plans } from "@/client"

export function useMealPlan(enabled = true) {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["mealPlan"],
    queryFn: async () => {
      const response = await Plans.plansGetTodaysMealPlan()
      if (response.error) {
        throw response.error
      }
      return response.data
    },
    enabled,
  })

  return {
    mealPlan: data?.data ?? [],
    isLoading,
    error,
    refetch,
  }
}
