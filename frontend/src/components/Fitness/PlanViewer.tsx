import {
  Box,
  Button,
  Container,
  Flex,
  Heading,
  SimpleGrid,
  Spinner,
  Text,
  VStack,
} from "@chakra-ui/react"
import { FiCheck, FiPlus } from "react-icons/fi"
import type { MealPlanPublic, TrainingRoutinePublic } from "@/client/types.gen"
import { DaySelector } from "@/components/Fitness/DaySelector"
import type { ExerciseLog, MealLog } from "@/types/fitness"

// Common quick-add foods for convenience
const QUICK_ADD_FOODS = [
  { name: "Banana", calories: 105, protein: 1, type: "snack" },
  { name: "Protein Shake", calories: 150, protein: 25, type: "snack" },
  { name: "Greek Yogurt", calories: 100, protein: 17, type: "snack" },
  { name: "Apple", calories: 95, protein: 0, type: "snack" },
  { name: "Almonds (28g)", calories: 164, protein: 6, type: "snack" },
  { name: "Boiled Egg", calories: 78, protein: 6, type: "snack" },
]

interface PlanViewerProps {
  mode: "workout" | "nutrition"
  mealPlan: MealPlanPublic[]
  trainingRoutine: TrainingRoutinePublic[]
  mealLogs: MealLog[]
  exerciseLogs: ExerciseLog[]
  isLoading?: boolean
  onAddMeal: (meal: Omit<MealLog, "id" | "time">) => void
  onAddExercise: (exercise: Omit<ExerciseLog, "id" | "time">) => void
}

export const PlanViewer = ({
  mode,
  mealPlan,
  trainingRoutine,
  mealLogs,
  exerciseLogs,
  isLoading = false,
  onAddMeal,
  onAddExercise,
}: PlanViewerProps) => {
  const isWorkout = mode === "workout"
  const title = isWorkout ? "Workout Protocol" : "Nutrition Protocol"

  const totalCalories = mealLogs.reduce((acc, log) => acc + log.calories, 0)
  const totalProtein = mealLogs.reduce((acc, log) => acc + log.protein, 0)
  const targetCalories = mealPlan.reduce((acc, item) => acc + item.calories, 0)
  const targetProtein = mealPlan.reduce((acc, item) => acc + item.protein_g, 0)

  // Calorie tracking with exceeded feedback
  const effectiveTargetCalories = targetCalories || 2000
  const caloriePercentage = (totalCalories / effectiveTargetCalories) * 100
  const isOverCalories = totalCalories > effectiveTargetCalories
  const calorieExcess = totalCalories - effectiveTargetCalories
  const calorieBarColor = isOverCalories
    ? "red.500"
    : caloriePercentage > 90
      ? "orange.500"
      : "blue.500"

  // Count total sets logged (each log entry represents sets done)
  const totalSetsLogged = exerciseLogs.reduce((acc, log) => acc + log.sets, 0)
  const targetSets = trainingRoutine.reduce((acc, item) => acc + item.sets, 0)

  const handleQuickAddFood = (
    name: string,
    cal: number,
    pro: number,
    type: string,
  ) => {
    onAddMeal({
      name,
      calories: cal,
      protein: pro,
      type: type as MealLog["type"],
    })
  }

  const handleLogSet = (exerciseName: string, reps: number, weight: number) => {
    onAddExercise({ name: exerciseName, sets: 1, reps, weight })
  }

  if (isLoading) {
    return (
      <Flex h="full" align="center" justify="center" bg="gray.50">
        <Spinner size="lg" color="blue.500" />
      </Flex>
    )
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
              {isWorkout
                ? trainingRoutine.length > 0
                  ? `${trainingRoutine.length} exercises planned`
                  : "Rest Day"
                : `${mealPlan.length} meals planned`}
            </Text>
          </Box>
          <Flex align="center" gap={2}>
            <DaySelector />
            <Box
              p={2}
              bg={isWorkout ? "blue.50" : "green.50"}
              borderRadius="full"
              fontSize="lg"
            >
              {isWorkout ? "🏋️" : "🍽️"}
            </Box>
          </Flex>
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

              {trainingRoutine.length === 0 ? (
                <Box
                  textAlign="center"
                  py={8}
                  bg="white"
                  borderRadius="xl"
                  border="1px dashed"
                  borderColor="gray.300"
                >
                  <Text fontSize="4xl" mb={2}>
                    🧘
                  </Text>
                  <Text color="gray.500" fontWeight="medium">
                    Rest Day
                  </Text>
                  <Text color="gray.400" fontSize="sm">
                    No workout scheduled for today
                  </Text>
                </Box>
              ) : (
                <Box>
                  <Text fontSize="xs" fontWeight="bold" color="gray.500" mb={3}>
                    THE PROTOCOL
                  </Text>
                  <VStack gap={3} align="stretch">
                    {trainingRoutine.map((item) => {
                      // Sum total sets logged for this exercise
                      const loggedForThis = exerciseLogs
                        .filter(
                          (l) =>
                            l.name.toLowerCase() ===
                            item.exercise_name.toLowerCase(),
                        )
                        .reduce((acc, log) => acc + log.sets, 0)
                      const isComplete = loggedForThis >= item.sets

                      return (
                        <Box
                          key={item.id}
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
                                  {item.exercise_name}
                                </Text>
                                {isComplete && (
                                  <FiCheck color="var(--chakra-colors-blue-600)" />
                                )}
                              </Flex>
                              <Text fontSize="xs" color="gray.500" mt={1}>
                                Target: {item.sets} Sets × {item.reps} Reps @{" "}
                                {item.target_load_kg}kg
                              </Text>
                              {item.machine_hint && (
                                <Text fontSize="xs" color="gray.400" mt={0.5}>
                                  💡 {item.machine_hint}
                                </Text>
                              )}
                            </Box>
                            <Button
                              size="sm"
                              colorPalette={isComplete ? "gray" : "blue"}
                              disabled={isComplete}
                              onClick={() =>
                                handleLogSet(
                                  item.exercise_name,
                                  item.reps,
                                  item.target_load_kg,
                                )
                              }
                            >
                              {isComplete ? <FiCheck /> : <FiPlus />}
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
              )}

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
                  borderColor={isOverCalories ? "red.200" : "gray.200"}
                >
                  <Flex justify="space-between" align="center" mb={1}>
                    <Text fontSize="xs" fontWeight="bold" color="gray.400">
                      CALORIES
                    </Text>
                    {isOverCalories && (
                      <Text
                        fontSize="xs"
                        fontWeight="bold"
                        color="red.500"
                        data-testid="calorie-excess"
                      >
                        +{calorieExcess} over
                      </Text>
                    )}
                  </Flex>
                  <Text
                    fontSize="2xl"
                    fontWeight="bold"
                    mb={2}
                    color={isOverCalories ? "red.600" : "inherit"}
                  >
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
                      bg={calorieBarColor}
                      borderRadius="full"
                      w={`${Math.min(100, caloriePercentage)}%`}
                      transition="all 0.5s"
                      data-testid="calorie-progress-bar"
                    />
                  </Box>
                  <Text fontSize="xs" color="gray.400" mt={1}>
                    / {targetCalories} kcal
                  </Text>
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
                      w={`${Math.min(100, (totalProtein / (targetProtein || 160)) * 100)}%`}
                      transition="width 0.5s"
                    />
                  </Box>
                  <Text fontSize="xs" color="gray.400" mt={1}>
                    / {targetProtein}g
                  </Text>
                </Box>
              </Flex>

              {mealPlan.length === 0 ? (
                <Box
                  textAlign="center"
                  py={8}
                  bg="white"
                  borderRadius="xl"
                  border="1px dashed"
                  borderColor="gray.300"
                >
                  <Text fontSize="4xl" mb={2}>
                    🍽️
                  </Text>
                  <Text color="gray.500" fontWeight="medium">
                    No meal plan for today
                  </Text>
                  <Text color="gray.400" fontSize="sm">
                    Use chat to log your meals
                  </Text>
                </Box>
              ) : (
                <Box>
                  <Text fontSize="xs" fontWeight="bold" color="gray.500" mb={3}>
                    THE PLAN
                  </Text>
                  <VStack gap={3} align="stretch">
                    {mealPlan.map((item) => {
                      const isLogged = mealLogs.some(
                        (l) =>
                          l.name.toLowerCase() ===
                            item.item_name.toLowerCase() ||
                          l.calories === item.calories,
                      )

                      return (
                        <Flex
                          key={item.id}
                          justify="space-between"
                          align="center"
                          bg="white"
                          p={4}
                          borderRadius="xl"
                          border="1px"
                          borderColor="gray.200"
                        >
                          <Box>
                            <Flex align="center" gap={2}>
                              <Text
                                fontSize="xs"
                                fontWeight="bold"
                                color="gray.400"
                                textTransform="uppercase"
                              >
                                {item.meal_type}
                              </Text>
                            </Flex>
                            <Text
                              fontWeight="bold"
                              fontSize="sm"
                              color={isLogged ? "gray.400" : "gray.900"}
                              textDecoration={
                                isLogged ? "line-through" : "none"
                              }
                            >
                              {item.item_name}
                            </Text>
                            <Text fontSize="xs" color="gray.500" mt={0.5}>
                              {item.calories} kcal • {item.protein_g}g Protein
                            </Text>
                          </Box>
                          <Button
                            size="sm"
                            variant={isLogged ? "ghost" : "outline"}
                            colorPalette={isLogged ? "gray" : "green"}
                            disabled={isLogged}
                            onClick={() =>
                              handleQuickAddFood(
                                item.item_name,
                                item.calories,
                                item.protein_g,
                                item.meal_type,
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
              )}

              <Box>
                <Text fontSize="xs" fontWeight="bold" color="gray.500" mb={3}>
                  QUICK ADD
                </Text>
                <SimpleGrid columns={2} gap={2}>
                  {QUICK_ADD_FOODS.map((food) => (
                    <Button
                      key={food.name}
                      size="sm"
                      variant="outline"
                      colorPalette="green"
                      justifyContent="flex-start"
                      h="auto"
                      py={2}
                      px={3}
                      onClick={() =>
                        handleQuickAddFood(
                          food.name,
                          food.calories,
                          food.protein,
                          food.type,
                        )
                      }
                    >
                      <Box textAlign="left">
                        <Text fontSize="xs" fontWeight="medium">
                          {food.name}
                        </Text>
                        <Text fontSize="xs" color="gray.500">
                          {food.calories} kcal • {food.protein}g
                        </Text>
                      </Box>
                    </Button>
                  ))}
                </SimpleGrid>
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
