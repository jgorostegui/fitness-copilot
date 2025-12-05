import { Box, Flex, Text } from "@chakra-ui/react"
import { useEffect, useState } from "react"
import type { DailyStats } from "@/types/fitness"

interface ActionCardProps {
  type: string
  data: Record<string, unknown>
  stats: DailyStats
}

/**
 * Card component for displaying logged food or exercise actions.
 * Shows animated progress bars for food and sets/reps for exercises.
 */
export function ActionCard({ type, data, stats }: ActionCardProps) {
  const [animate, setAnimate] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setAnimate(true), 100)
    return () => clearTimeout(timer)
  }, [])

  if (type === "log_food") {
    const itemCalories = (data?.calories as number) || 0
    const previousTotal = Math.max(0, stats.caloriesConsumed - itemCalories)
    const prevPercent = Math.min(
      100,
      (previousTotal / stats.caloriesTarget) * 100,
    )
    const currentPercent = Math.min(
      100,
      (stats.caloriesConsumed / stats.caloriesTarget) * 100,
    )

    return (
      <Box
        mt={2}
        bg="white"
        border="1px"
        borderColor="gray.200"
        borderRadius="xl"
        p={3}
        maxW="280px"
      >
        <Flex justify="space-between" align="center" mb={2}>
          <Flex align="center" gap={2}>
            <Box bg="orange.50" p={1.5} borderRadius="lg" color="orange.500">
              🔥
            </Box>
            <Box>
              <Text fontSize="sm" fontWeight="bold">
                {(data.food as string) || (data.name as string)}
              </Text>
              <Text fontSize="xs" color="gray.500">
                Logged to Daily Intake
              </Text>
            </Box>
          </Flex>
          <Box textAlign="right">
            <Text fontSize="sm" fontWeight="bold">
              +{itemCalories}
            </Text>
            <Text fontSize="xs" color="gray.400">
              KCAL
            </Text>
          </Box>
        </Flex>
        <Box>
          <Flex justify="space-between" fontSize="xs" color="gray.500" mb={1}>
            <Text>Daily Energy</Text>
            <Text>
              {stats.caloriesConsumed} / {stats.caloriesTarget}
            </Text>
          </Flex>
          <Box
            h={2}
            bg="gray.100"
            borderRadius="full"
            overflow="hidden"
            position="relative"
          >
            <Box
              position="absolute"
              top={0}
              left={0}
              h="full"
              bg="gray.300"
              borderRadius="full"
              w={`${prevPercent}%`}
              transition="width 1s"
            />
            <Box
              position="absolute"
              top={0}
              h="full"
              bg="blue.500"
              borderRadius="full"
              left={`${prevPercent}%`}
              w={animate ? `${currentPercent - prevPercent}%` : "0%"}
              transition="width 1s"
              boxShadow="0 0 10px rgba(59,130,246,0.5)"
            />
          </Box>
        </Box>
        {(data.protein as number) > 0 && (
          <Flex
            mt={2}
            align="center"
            gap={1}
            fontSize="xs"
            color="green.600"
            bg="green.50"
            px={2}
            py={1}
            borderRadius="md"
            w="fit-content"
          >
            ✓ {data.protein as number}g Protein Added
          </Flex>
        )}
      </Box>
    )
  }

  if (type === "log_exercise") {
    return (
      <Box
        mt={2}
        bg="white"
        border="1px"
        borderColor="gray.200"
        borderRadius="xl"
        p={3}
        maxW="280px"
      >
        <Flex justify="space-between" align="center" mb={2}>
          <Flex align="center" gap={2}>
            <Box bg="purple.50" p={1.5} borderRadius="lg" color="purple.500">
              🏋️
            </Box>
            <Box>
              <Text fontSize="sm" fontWeight="bold">
                {(data.exercise as string) || (data.name as string)}
              </Text>
              <Text fontSize="xs" color="gray.500">
                Workout Logged
              </Text>
            </Box>
          </Flex>
          <Text fontSize="sm" fontWeight="bold">
            {(data.weight_kg as number) || (data.weight as number) || 0}kg
          </Text>
        </Flex>
        <Flex gap={2}>
          <Box flex={1} bg="gray.50" p={2} borderRadius="lg" textAlign="center">
            <Text fontSize="sm" fontWeight="bold">
              {data.sets as number}
            </Text>
            <Text fontSize="xs" color="gray.400">
              SETS
            </Text>
          </Box>
          <Box flex={1} bg="gray.50" p={2} borderRadius="lg" textAlign="center">
            <Text fontSize="sm" fontWeight="bold">
              {data.reps as number}
            </Text>
            <Text fontSize="xs" color="gray.400">
              REPS
            </Text>
          </Box>
        </Flex>
      </Box>
    )
  }

  return null
}
