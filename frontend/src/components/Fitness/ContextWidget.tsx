import { Box, Button, Flex, Text } from "@chakra-ui/react"
import { useEffect, useState } from "react"
import type { TrainingRoutinePublic } from "@/client/types.gen"
import type { DailyStats, ExerciseLog, MealLog } from "@/types/fitness"

interface ContextWidgetProps {
  mode: "gym" | "kitchen"
  toggleMode: () => void
  stats: DailyStats
  exerciseLogs: ExerciseLog[]
  mealLogs: MealLog[]
  trainingRoutine: TrainingRoutinePublic[]
  onQuickLog: (text: string) => void
}

/**
 * Context-aware widget that shows gym or kitchen mode.
 * Displays current exercise target or calorie/protein remaining.
 */
export function ContextWidget({
  mode,
  toggleMode,
  stats,
  exerciseLogs,
  mealLogs,
  trainingRoutine,
  onQuickLog,
}: ContextWidgetProps) {
  const [sessionTime, setSessionTime] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => setSessionTime((prev) => prev + 1), 1000)
    return () => clearInterval(timer)
  }, [])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, "0")}`
  }

  if (mode === "gym") {
    const completedNames = new Set(
      exerciseLogs.map((l) => l.name.toLowerCase()),
    )
    const nextIndex = trainingRoutine.findIndex(
      (r) => !completedNames.has(r.exercise_name.toLowerCase()),
    )
    const currentTarget = nextIndex !== -1 ? trainingRoutine[nextIndex] : null
    const allDone = nextIndex === -1 && trainingRoutine.length > 0
    const isRestDay = trainingRoutine.length === 0

    return (
      <Box
        bg="white"
        borderBottom="1px"
        borderColor="gray.200"
        px={4}
        py={3}
        cursor="pointer"
        onClick={toggleMode}
        _active={{ bg: "gray.50" }}
      >
        <Flex justify="space-between" align="start">
          <Box>
            <Text
              fontSize="xs"
              fontWeight="bold"
              color="blue.600"
              bg="blue.50"
              px={2}
              py={0.5}
              borderRadius="sm"
              w="fit-content"
              mb={1}
            >
              🏋️ GYM MODE
            </Text>
            <Text fontSize="lg" fontWeight="bold">
              {isRestDay
                ? "Rest Day 🧘"
                : allDone
                  ? "Session Complete ✓"
                  : currentTarget?.exercise_name || "No exercise"}
            </Text>
            {!isRestDay && !allDone && currentTarget && (
              <Flex gap={2} mt={1}>
                <Text
                  fontSize="xs"
                  bg="gray.100"
                  px={1.5}
                  py={0.5}
                  borderRadius="sm"
                >
                  {currentTarget.sets} Sets
                </Text>
                <Text
                  fontSize="xs"
                  bg="gray.100"
                  px={1.5}
                  py={0.5}
                  borderRadius="sm"
                >
                  {currentTarget.reps} Reps
                </Text>
                <Text fontSize="xs" color="blue.600">
                  {currentTarget.target_load_kg}kg
                </Text>
              </Flex>
            )}
          </Box>
          <Box textAlign="right">
            <Text fontSize="xs" color="gray.400">
              Session
            </Text>
            <Text fontSize="xl" fontWeight="bold" fontFamily="mono">
              {formatTime(sessionTime)}
            </Text>
          </Box>
        </Flex>
        <Text fontSize="xs" color="gray.400" mt={2} textAlign="center">
          Tap to switch to Kitchen mode
        </Text>
      </Box>
    )
  }

  const caloriesLeft = Math.max(
    0,
    stats.caloriesTarget - stats.caloriesConsumed,
  )
  const recentLogs = mealLogs.slice(-3).reverse()

  return (
    <Box bg="white" borderBottom="1px" borderColor="gray.200" px={4} py={3}>
      <Flex
        justify="space-between"
        align="start"
        cursor="pointer"
        onClick={toggleMode}
        _active={{ opacity: 0.8 }}
      >
        <Box>
          <Text
            fontSize="xs"
            fontWeight="bold"
            color="green.600"
            bg="green.50"
            px={2}
            py={0.5}
            borderRadius="sm"
            w="fit-content"
            mb={1}
          >
            🍽️ KITCHEN MODE
          </Text>
          <Flex align="baseline" gap={1}>
            <Text fontSize="3xl" fontWeight="bold">
              {Math.round(caloriesLeft)}
            </Text>
            <Text fontSize="xs" fontWeight="bold" color="gray.400">
              kcal left
            </Text>
          </Flex>
        </Box>
        <Box textAlign="right">
          <Text fontSize="xs" color="gray.400">
            Protein Left
          </Text>
          <Text fontSize="xl" fontWeight="bold" fontFamily="mono">
            {Math.max(
              0,
              Math.round(stats.proteinTarget - stats.proteinConsumed),
            )}
            g
          </Text>
        </Box>
      </Flex>

      <Box mt={3}>
        <Text fontSize="xs" fontWeight="bold" color="gray.400" mb={2}>
          QUICK ADD
        </Text>
        <Flex gap={2} flexWrap="wrap">
          {[
            {
              emoji: "🥗",
              name: "Chicken Salad",
              text: "I ate a Grilled Chicken Salad",
            },
            {
              emoji: "🥣",
              name: "Oatmeal",
              text: "I had Oatmeal with Berries",
            },
            {
              emoji: "🍳",
              name: "Eggs & Toast",
              text: "I ate Eggs and Avocado Toast",
            },
            {
              emoji: "🍗",
              name: "Rice & Chicken",
              text: "I had Rice and Grilled Chicken",
            },
          ].map((item, idx) => (
            <Button
              key={idx}
              size="sm"
              variant="outline"
              onClick={(e) => {
                e.stopPropagation()
                onQuickLog(item.text)
              }}
            >
              {item.emoji} {item.name}
            </Button>
          ))}
        </Flex>
      </Box>

      {recentLogs.length > 0 && (
        <Flex gap={2} mt={3} overflow="hidden">
          {recentLogs.map((log) => (
            <Flex
              key={log.id}
              align="center"
              gap={1}
              bg="gray.50"
              px={2}
              py={1}
              borderRadius="full"
              border="1px"
              borderColor="gray.100"
            >
              <Box w={1.5} h={1.5} borderRadius="full" bg="green.400" />
              <Text fontSize="xs" color="gray.600" maxW="80px" truncate>
                {log.name}
              </Text>
            </Flex>
          ))}
        </Flex>
      )}

      <Text fontSize="xs" color="gray.400" mt={2} textAlign="center">
        Tap to switch to Gym mode
      </Text>
    </Box>
  )
}
