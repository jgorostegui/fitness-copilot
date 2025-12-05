import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Profile } from "@/client"
import type { UserProfilePublic, UserProfileUpdate } from "@/client"

export const PROFILE_QUERY_KEY = ["profile", "me"]

/**
 * Hook for fetching and updating the current user's profile.
 */
export function useProfile(enabled = true) {
  const queryClient = useQueryClient()

  const query = useQuery({
    queryKey: PROFILE_QUERY_KEY,
    queryFn: async () => {
      const response = await Profile.profileGetCurrentUserProfile()
      if (response.error) {
        throw response.error
      }
      return response.data as UserProfilePublic
    },
    enabled,
    staleTime: 1000 * 60 * 5, // 5 minutes
  })

  const updateMutation = useMutation({
    mutationFn: async (data: UserProfileUpdate) => {
      const response = await Profile.profileUpdateCurrentUserProfile({
        body: data,
      })
      if (response.error) {
        throw response.error
      }
      return response.data as UserProfilePublic
    },
    onSuccess: (data) => {
      queryClient.setQueryData(PROFILE_QUERY_KEY, data)
    },
  })

  return {
    profile: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    updateProfile: updateMutation.mutate,
    updateProfileAsync: updateMutation.mutateAsync,
    isUpdating: updateMutation.isPending,
  }
}
