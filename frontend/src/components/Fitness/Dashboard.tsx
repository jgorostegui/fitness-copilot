import { Box, Container, Flex, Heading, Text, VStack } from "@chakra-ui/react"
import type {
  DailyStats,
  ExerciseLog,
  MealLog,
  UserProfile,
} from "@/types/fitness"

interface DashboardProps {
  stats: DailyStats
  mealLogs: MealLog[]
  exerciseLogs: ExerciseLog[]
  profile: UserProfile
}

const CircularProgress = ({
  value,
  max,
  label,
  color,
}: {
  value: number
  max: number
  label: string
  color: string
}) => {
  const percentage = Math.min(100, (value / max) * 100)
  const circumference = 2 * Math.PI * 40
  const strokeDashoffset = circumference - (percentage / 100) * circumference

  return (
    <Box textAlign="center">
      <Box position="relative" w="100px" h="100px" mx="auto">
        <svg
          width="100"
          height="100"
          viewBox="0 0 100 100"
          role="img"
          aria-label={`${label} progress: ${percentage}%`}
        >
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            stroke="var(--chakra-colors-gray-200)"
            strokeWidth="8"
          />
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            transform="rotate(-90 50 50)"
            style={{ transition: "stroke-dashoffset 0.5s ease" }}
          />
        </svg>
        <Box
          position="absolute"
          top="50%"
          left="50%"
          transform="translate(-50%, -50%)"
          textAlign="center"
        >
          <Text fontWeight="bold" fontSize="lg">
            {value}
          </Text>
          <Text fontSize="xs" color="gray.500">
            / {max}
          </Text>
        </Box>
      </Box>
      <Text fontSize="sm" fontWeight="medium" mt={2} color="gray.600">
        {label}
      </Text>
    </Box>
  )
}

export const Dashboard = ({
  stats,
  mealLogs,
  exerciseLogs,
  profile,
}: DashboardProps) => {
  const allLogs = [...mealLogs, ...exerciseLogs].sort(
    (a, b) => new Date(b.time).getTime() - new Date(a.time).getTime(),
  )

  return (
    <Box h="full" overflowY="auto" pb={24}>
      <Box
        bg="white"
        borderBottom="1px"
        borderColor="gray.200"
        px={4}
        py={4}
        position="sticky"
        top={0}
        zIndex={10}
      >
        <Heading size="md">Monitor</Heading>
        <Flex justify="space-between" align="center" mt={1}>
          <Text fontSize="xs" color="gray.500">
            {new Date().toLocaleDateString(undefined, {
              weekday: "long",
              month: "long",
              day: "numeric",
            })}
          </Text>
          <Text
            fontSize="xs"
            fontWeight="bold"
            color="blue.600"
            bg="blue.50"
            px={2}
            py={0.5}
            borderRadius="full"
          >
            {profile.plan.toUpperCase()}
          </Text>
        </Flex>
      </Box>

      <Container maxW="full" p={4}>
        <VStack gap={6} align="stretch">
          <Flex gap={4} justify="center">
            <CircularProgress
              value={stats.caloriesConsumed}
              max={stats.caloriesTarget}
              label="Calories"
              color="var(--chakra-colors-blue-500)"
            />
            <CircularProgress
              value={stats.proteinConsumed}
              max={stats.proteinTarget}
              label="Protein (g)"
              color="var(--chakra-colors-green-500)"
            />
          </Flex>

          <Flex gap={4}>
            <Box
              flex={1}
              bg="white"
              p={3}
              borderRadius="xl"
              border="1px"
              borderColor="gray.200"
            >
              <Flex align="center" gap={2}>
                <Box
                  bg="orange.50"
                  p={2}
                  borderRadius="lg"
                  fontWeight="bold"
                  color="orange.500"
                >
                  {stats.workoutsCompleted}
                </Box>
                <Box>
                  <Text fontSize="xs" color="gray.500">
                    EXERCISES
                  </Text>
                  <Text fontSize="sm" fontWeight="semibold">
                    Completed
                  </Text>
                </Box>
              </Flex>
            </Box>
            <Box
              flex={1}
              bg="white"
              p={3}
              borderRadius="xl"
              border="1px"
              borderColor="gray.200"
            >
              <Flex align="center" gap={2}>
                <Box
                  bg="purple.50"
                  p={2}
                  borderRadius="lg"
                  fontWeight="bold"
                  color="purple.500"
                >
                  {Math.round(
                    (stats.caloriesConsumed / stats.caloriesTarget) * 100,
                  )}
                  %
                </Box>
                <Box>
                  <Text fontSize="xs" color="gray.500">
                    DAILY GOAL
                  </Text>
                  <Text fontSize="sm" fontWeight="semibold">
                    Progress
                  </Text>
                </Box>
              </Flex>
            </Box>
          </Flex>

          <Box>
            <Text fontSize="xs" fontWeight="bold" color="gray.500" mb={3}>
              📋 ACTIVITY LOG
            </Text>
            {allLogs.length === 0 ? (
              <Box
                textAlign="center"
                py={8}
                bg="white"
                borderRadius="xl"
                border="1px dashed"
                borderColor="gray.300"
              >
                <Text color="gray.400" fontSize="sm">
                  No activity yet. Use Chat to log your day.
                </Text>
              </Box>
            ) : (
              <VStack gap={2} align="stretch">
                {allLogs.map((log) => (
                  <Box
                    key={log.id}
                    bg="white"
                    p={3}
                    borderRadius="xl"
                    border="1px"
                    borderColor="gray.200"
                  >
                    <Flex justify="space-between" align="center">
                      <Flex align="center" gap={2}>
                        <Box
                          w={2}
                          h={2}
                          borderRadius="full"
                          bg={"calories" in log ? "green.400" : "blue.400"}
                        />
                        <Box>
                          <Text fontWeight="semibold" fontSize="sm">
                            {log.name}
                          </Text>
                          <Text fontSize="xs" color="gray.400">
                            {new Date(log.time).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </Text>
                        </Box>
                      </Flex>
                      <Box textAlign="right">
                        {"calories" in log ? (
                          <>
                            <Text fontWeight="bold" fontSize="sm">
                              {log.calories}
                            </Text>
                            <Text fontSize="xs" color="gray.400">
                              kcal
                            </Text>
                          </>
                        ) : (
                          <>
                            <Text fontWeight="bold" fontSize="sm">
                              {(log as ExerciseLog).weight}kg
                            </Text>
                            <Text fontSize="xs" color="gray.400">
                              {(log as ExerciseLog).sets} sets
                            </Text>
                          </>
                        )}
                      </Box>
                    </Flex>
                  </Box>
                ))}
              </VStack>
            )}
          </Box>
        </VStack>
      </Container>
    </Box>
  )
}
