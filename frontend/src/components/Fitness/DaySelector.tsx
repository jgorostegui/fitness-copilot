import { Box, Button, Flex, Menu, Text } from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Profile } from "@/client"

const DAY_NAMES = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
]

/**
 * DaySelector component for changing the simulated day.
 * Used for demo purposes to test different days in the weekly plan.
 */
export function DaySelector() {
  const queryClient = useQueryClient()

  const { data: dayData, isLoading } = useQuery({
    queryKey: ["simulatedDay"],
    queryFn: async () => {
      const response = await Profile.profileGetSimulatedDay()
      if (response.error) {
        throw response.error
      }
      return response.data
    },
  })

  const updateDayMutation = useMutation({
    mutationFn: async (day: number) => {
      const response = await Profile.profileUpdateSimulatedDay({
        body: { simulated_day: day },
      })
      if (response.error) {
        throw response.error
      }
      return response.data
    },
    onSuccess: () => {
      // Invalidate queries that depend on simulated day
      queryClient.invalidateQueries({ queryKey: ["simulatedDay"] })
      queryClient.invalidateQueries({ queryKey: ["mealPlan"] })
      queryClient.invalidateQueries({ queryKey: ["trainingRoutine"] })
      queryClient.invalidateQueries({ queryKey: ["profile"] })
      // Use exact query keys that match the hooks
      queryClient.invalidateQueries({ queryKey: ["summary", "today"] })
      queryClient.invalidateQueries({ queryKey: ["logs", "today"] })
    },
  })

  if (isLoading) {
    return (
      <Button variant="outline" size="sm" colorPalette="blue" loading>
        <Text fontSize="xs" fontWeight="bold">
          📅 Loading...
        </Text>
      </Button>
    )
  }

  if (!dayData) {
    return (
      <Button variant="outline" size="sm" colorPalette="gray" disabled>
        <Text fontSize="xs" fontWeight="bold">
          📅 Monday
        </Text>
      </Button>
    )
  }

  const currentDay = dayData.simulatedDay
  const currentDayName = dayData.dayName

  return (
    <Box>
      <Menu.Root>
        <Menu.Trigger asChild>
          <Button
            variant="outline"
            size="sm"
            colorPalette="blue"
            loading={updateDayMutation.isPending}
          >
            <Text fontSize="xs" fontWeight="bold">
              📅 {currentDayName}
            </Text>
          </Button>
        </Menu.Trigger>
        <Menu.Positioner>
          <Menu.Content>
            {DAY_NAMES.map((name, index) => (
              <Menu.Item
                key={index}
                value={String(index)}
                onClick={() => updateDayMutation.mutate(index)}
              >
                <Flex justify="space-between" w="full" gap={2}>
                  <Text>{name}</Text>
                  {index === currentDay && <Text color="blue.500">✓</Text>}
                </Flex>
              </Menu.Item>
            ))}
          </Menu.Content>
        </Menu.Positioner>
      </Menu.Root>
    </Box>
  )
}
