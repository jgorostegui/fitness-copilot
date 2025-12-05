import {
  Box,
  Button,
  Container,
  Flex,
  Heading,
  Text,
  VStack,
} from "@chakra-ui/react"
import { FiCheck, FiPlus } from "react-icons/fi"
import { TODAY_MEAL_PLAN, TODAY_ROUTINE } from "@/constants/fitness"
import type { ExerciseLog, MealLog } from "@/types/fitness"

interface PlanViewerProps {
  mode: "workout" | "nutrition"
  mealLogs: MealLog[]
  exerciseLogs: ExerciseLog[]
  onAddMeal: (meal: Omit<MealLog, "id" | "time">) => void
  onAddExercise: (exercise: Omit<ExerciseLog, "id" | "time">) => void
}

export const PlanViewer = ({
  mode,
  mealLogs,
  exerciseLogs,
  onAddMeal,
  onAddExercise,
}: PlanViewerProps) => {
  const isWorkout = mode === "workout"
  const title = isWorkout ? "Workout Protocol" : "Nutrition Protocol"

  const totalCalories = mealLogs.reduce((acc, log) => acc + log.calories, 0)
  const totalProtein = mealLogs.reduce((acc, log) => acc + log.protein, 0)
  const targetCalories = TODAY_MEAL_PLAN.reduce(
    (acc, item) => acc + item.calories,
    0,
  )

  const totalSetsLogged = exerciseLogs.length
  const targetSets = TODAY_ROUTINE.reduce((acc, item) => acc + item.sets, 0)

  const handleQuickAddFood = (name: string, cal: number, pro: number) => {
    onAddMeal({ name, calories: cal, protein: pro, type: "snack" })
  }

  const handleLogSet = (exerciseName: string, reps: string) => {
    const repsParsed = Number.parseInt(reps.split("-")[0], 10) || 10
    onAddExercise({ name: exerciseName, sets: 1, reps: repsParsed, weight: 0 })
  }

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
        <Flex justify="space-between" align="center">
          <Box>
            <Heading size="md">{title}</Heading>
            <Text fontSize="xs" color="gray.500">
              {isWorkout ? "Leg Day Assignment" : "Daily Fuel Architecture"}
            </Text>
          </Box>
          <Box
            p={2}
            bg={isWorkout ? "blue.50" : "green.50"}
            borderRadius="full"
            fontSize="lg"
          >
            {isWorkout ? "🏋️" : "🍽️"}
          </Box>
        </Flex>
      </Box>

      <Container maxW="full" p={4}>
        <VStack gap={6} align="stretch">
          {isWorkout ? (
            <>
              <Box
                bg="white"
                borderRadius="xl"
                p={4}
                border="1px"
                borderColor="gray.200"
              >
                <Flex justify="space-between" align="center">
                  <Box>
                    <Text fontSize="xs" fontWeight="bold" color="gray.400">
                      SESSION VOLUME
                    </Text>
                    <Flex align="baseline" gap={1}>
                      <Text fontSize="2xl" fontWeight="bold">
                        {totalSetsLogged}
                      </Text>
                      <Text fontSize="sm" color="gray.400">
                        / {targetSets} Sets
                      </Text>
                    </Flex>
                  </Box>
                  <Box
                    w={10}
                    h={10}
                    borderRadius="full"
                    bg="blue.50"
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                  >
                    <Text fontSize="xs" fontWeight="bold" color="blue.600">
                      {targetSets > 0
                        ? Math.round((totalSetsLogged / targetSets) * 100)
                        : 0}
                      %
                    </Text>
                  </Box>
                </Flex>
              </Box>

              <Box>
                <Text fontSize="xs" fontWeight="bold" color="gray.500" mb={3}>
                  THE PROTOCOL
                </Text>
                <VStack gap={3} align="stretch">
                  {TODAY_ROUTINE.map((item, idx) => {
                    const loggedForThis = exerciseLogs.filter(
                      (l) =>
                        l.name.toLowerCase() === item.exercise.toLowerCase(),
                    ).length
                    const isComplete = loggedForThis >= item.sets

                    return (
                      <Box
                        key={idx}
                        bg="white"
                        p={4}
                        borderRadius="xl"
                        border="1px"
                        borderColor={isComplete ? "blue.200" : "gray.200"}
                        boxShadow={
                          isComplete
                            ? "0 0 0 1px var(--chakra-colors-blue-200)"
                            : "sm"
                        }
                      >
                        <Flex justify="space-between" align="start" mb={3}>
                          <Box>
                            <Flex align="center" gap={2}>
                              <Text
                                fontWeight="bold"
                                fontSize="sm"
                                color={isComplete ? "blue.600" : "gray.900"}
                              >
                                {item.exercise}
                              </Text>
                              {isComplete && (
                                <FiCheck color="var(--chakra-colors-blue-600)" />
                              )}
                            </Flex>
                            <Text fontSize="xs" color="gray.500" mt={1}>
                              Target: {item.sets} Sets × {item.reps} Reps
                            </Text>
                          </Box>
                          <Button
                            size="sm"
                            colorPalette="blue"
                            onClick={() =>
                              handleLogSet(item.exercise, item.reps)
                            }
                          >
                            <FiPlus />
                          </Button>
                        </Flex>

                        <Flex gap={1.5}>
                          {Array.from({ length: item.sets }).map((_, i) => (
                            <Box
                              key={i}
                              h={1.5}
                              flex={1}
                              borderRadius="full"
                              bg={i < loggedForThis ? "blue.500" : "gray.100"}
                              transition="background 0.3s"
                            />
                          ))}
                        </Flex>
                      </Box>
                    )
                  })}
                </VStack>
              </Box>

              {exerciseLogs.length > 0 && (
                <Box>
                  <Text fontSize="xs" fontWeight="bold" color="gray.500" mb={3}>
                    COMPLETED SETS
                  </Text>
                  <VStack gap={2} align="stretch">
                    {exerciseLogs
                      .slice()
                      .reverse()
                      .map((log) => (
                        <Flex
                          key={log.id}
                          justify="space-between"
                          align="center"
                          bg="white"
                          p={3}
                          borderRadius="lg"
                          border="1px"
                          borderColor="gray.100"
                        >
                          <Text
                            fontSize="sm"
                            fontWeight="medium"
                            color="gray.700"
                          >
                            {log.name}
                          </Text>
                          <Text
                            fontSize="xs"
                            color="gray.400"
                            fontFamily="mono"
                          >
                            1 Set × {log.reps} Reps
                          </Text>
                        </Flex>
                      ))}
                  </VStack>
                </Box>
              )}
            </>
          ) : (
            <>
              <Flex gap={4}>
                <Box
                  flex={1}
                  bg="white"
                  p={4}
                  borderRadius="xl"
                  border="1px"
                  borderColor="gray.200"
                >
                  <Text fontSize="xs" fontWeight="bold" color="gray.400" mb={1}>
                    CALORIES
                  </Text>
                  <Text fontSize="2xl" fontWeight="bold" mb={2}>
                    {totalCalories}
                  </Text>
                  <Box
                    h={1.5}
                    bg="gray.100"
                    borderRadius="full"
                    overflow="hidden"
                  >
                    <Box
                      h="full"
                      bg="blue.500"
                      borderRadius="full"
                      w={`${Math.min(100, (totalCalories / (targetCalories || 2000)) * 100)}%`}
                      transition="width 0.5s"
                    />
                  </Box>
                </Box>
                <Box
                  flex={1}
                  bg="white"
                  p={4}
                  borderRadius="xl"
                  border="1px"
                  borderColor="gray.200"
                >
                  <Text fontSize="xs" fontWeight="bold" color="gray.400" mb={1}>
                    PROTEIN
                  </Text>
                  <Text fontSize="2xl" fontWeight="bold" mb={2}>
                    {totalProtein}g
                  </Text>
                  <Box
                    h={1.5}
                    bg="gray.100"
                    borderRadius="full"
                    overflow="hidden"
                  >
                    <Box
                      h="full"
                      bg="green.500"
                      borderRadius="full"
                      w={`${Math.min(100, (totalProtein / 160) * 100)}%`}
                      transition="width 0.5s"
                    />
                  </Box>
                </Box>
              </Flex>

              <Box>
                <Text fontSize="xs" fontWeight="bold" color="gray.500" mb={3}>
                  QUICK ADD
                </Text>
                <Flex gap={3} flexWrap="wrap">
                  {[
                    { emoji: "🍌", name: "Banana", cal: 105, pro: 1 },
                    { emoji: "🥚", name: "Egg", cal: 70, pro: 6 },
                    { emoji: "☕", name: "Coffee", cal: 5, pro: 0 },
                    { emoji: "🥤", name: "Shake", cal: 130, pro: 24 },
                  ].map((item, idx) => (
                    <Button
                      key={idx}
                      variant="outline"
                      h="auto"
                      py={3}
                      px={4}
                      flexDirection="column"
                      onClick={() =>
                        handleQuickAddFood(item.name, item.cal, item.pro)
                      }
                    >
                      <Text fontSize="2xl" mb={1}>
                        {item.emoji}
                      </Text>
                      <Text fontSize="xs" fontWeight="bold">
                        {item.name}
                      </Text>
                    </Button>
                  ))}
                </Flex>
              </Box>

              <Box>
                <Text fontSize="xs" fontWeight="bold" color="gray.500" mb={3}>
                  THE PLAN
                </Text>
                <VStack gap={3} align="stretch">
                  {TODAY_MEAL_PLAN.map((item, idx) => {
                    const isLogged = mealLogs.some(
                      (l) =>
                        l.name.includes(item.meal) ||
                        l.calories === item.calories,
                    )

                    return (
                      <Flex
                        key={idx}
                        justify="space-between"
                        align="center"
                        bg="white"
                        p={4}
                        borderRadius="xl"
                        border="1px"
                        borderColor="gray.200"
                      >
                        <Box>
                          <Text
                            fontWeight="bold"
                            fontSize="sm"
                            color={isLogged ? "gray.400" : "gray.900"}
                            textDecoration={isLogged ? "line-through" : "none"}
                          >
                            {item.meal}
                          </Text>
                          <Text fontSize="xs" color="gray.500" mt={0.5}>
                            {item.calories} kcal • {item.protein}g Protein
                          </Text>
                        </Box>
                        <Button
                          size="sm"
                          variant={isLogged ? "ghost" : "outline"}
                          colorPalette={isLogged ? "gray" : "green"}
                          disabled={isLogged}
                          onClick={() =>
                            handleQuickAddFood(
                              item.meal,
                              item.calories,
                              item.protein,
                            )
                          }
                        >
                          {isLogged ? <FiCheck /> : <FiPlus />}
                        </Button>
                      </Flex>
                    )
                  })}
                </VStack>
              </Box>

              {mealLogs.length > 0 && (
                <Box pt={2} borderTop="1px" borderColor="gray.200">
                  <Text fontSize="xs" fontWeight="bold" color="gray.500" mb={3}>
                    CONSUMED
                  </Text>
                  <VStack gap={2} align="stretch">
                    {mealLogs
                      .slice()
                      .reverse()
                      .map((log) => (
                        <Flex
                          key={log.id}
                          justify="space-between"
                          align="center"
                          bg="white"
                          p={2}
                          px={3}
                          borderRadius="lg"
                          border="1px"
                          borderColor="gray.100"
                        >
                          <Text
                            fontSize="xs"
                            fontWeight="medium"
                            color="gray.700"
                          >
                            {log.name}
                          </Text>
                          <Text
                            fontSize="xs"
                            color="gray.400"
                            fontFamily="mono"
                          >
                            {log.calories} kcal
                          </Text>
                        </Flex>
                      ))}
                  </VStack>
                </Box>
              )}
            </>
          )}
        </VStack>
      </Container>
    </Box>
  )
}
