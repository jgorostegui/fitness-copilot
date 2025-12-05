import { Badge, Box, Flex, SimpleGrid, Text, VStack } from "@chakra-ui/react"

interface GymAnalysis {
  exercise_name: string
  form_cues: string[]
  sets: number
  reps: number
  weight_kg: number
}

interface FoodAnalysis {
  meal_name: string
  calories: number
  protein_g: number
  carbs_g: number
  fat_g: number
}

interface VisionResponseCardProps {
  actionType: "log_exercise" | "log_food"
  actionData: Record<string, unknown>
}

/**
 * Specialized card for displaying vision analysis results.
 * Shows gym equipment analysis with form cues or food analysis with macros.
 */
export function VisionResponseCard({
  actionType,
  actionData,
}: VisionResponseCardProps) {
  if (actionType === "log_exercise") {
    const data = actionData as unknown as GymAnalysis
    return (
      <Box
        mt={2}
        bg="white"
        border="1px"
        borderColor="purple.200"
        borderRadius="xl"
        p={4}
        maxW="300px"
        boxShadow="sm"
      >
        <Flex align="center" gap={2} mb={3}>
          <Box bg="purple.50" p={2} borderRadius="lg">
            <Text fontSize="xl">🏋️</Text>
          </Box>
          <Box flex={1}>
            <Text fontSize="md" fontWeight="bold" color="purple.700">
              {data.exercise_name}
            </Text>
            <Badge colorScheme="green" size="sm">
              ✓ Logged
            </Badge>
          </Box>
        </Flex>

        {data.form_cues && data.form_cues.length > 0 && (
          <Box mb={3}>
            <Text fontSize="xs" fontWeight="bold" color="gray.500" mb={1}>
              FORM TIPS
            </Text>
            <VStack align="start" gap={1}>
              {data.form_cues.map((cue, i) => (
                <Text key={i} fontSize="sm" color="gray.700">
                  • {cue}
                </Text>
              ))}
            </VStack>
          </Box>
        )}

        <Box borderTop="1px" borderColor="gray.200" mb={3} />

        <SimpleGrid columns={3} gap={2}>
          <Box bg="purple.50" p={2} borderRadius="lg" textAlign="center">
            <Text fontSize="lg" fontWeight="bold" color="purple.700">
              {data.sets}
            </Text>
            <Text fontSize="xs" color="gray.500">
              SETS
            </Text>
          </Box>
          <Box bg="purple.50" p={2} borderRadius="lg" textAlign="center">
            <Text fontSize="lg" fontWeight="bold" color="purple.700">
              {data.reps}
            </Text>
            <Text fontSize="xs" color="gray.500">
              REPS
            </Text>
          </Box>
          <Box bg="purple.50" p={2} borderRadius="lg" textAlign="center">
            <Text fontSize="lg" fontWeight="bold" color="purple.700">
              {data.weight_kg > 0 ? `${data.weight_kg}kg` : "-"}
            </Text>
            <Text fontSize="xs" color="gray.500">
              WEIGHT
            </Text>
          </Box>
        </SimpleGrid>
      </Box>
    )
  }

  // Food analysis card
  const data = actionData as unknown as FoodAnalysis
  return (
    <Box
      mt={2}
      bg="white"
      border="1px"
      borderColor="green.200"
      borderRadius="xl"
      p={4}
      maxW="300px"
      boxShadow="sm"
    >
      <Flex align="center" gap={2} mb={3}>
        <Box bg="green.50" p={2} borderRadius="lg">
          <Text fontSize="xl">🍽️</Text>
        </Box>
        <Box flex={1}>
          <Text fontSize="md" fontWeight="bold" color="green.700">
            {data.meal_name}
          </Text>
          <Badge colorScheme="green" size="sm">
            ✓ Logged
          </Badge>
        </Box>
      </Flex>

      <SimpleGrid columns={4} gap={2}>
        <Box bg="orange.50" p={2} borderRadius="lg" textAlign="center">
          <Text fontSize="md" fontWeight="bold" color="orange.600">
            {data.calories}
          </Text>
          <Text fontSize="xs" color="gray.500">
            KCAL
          </Text>
        </Box>
        <Box bg="blue.50" p={2} borderRadius="lg" textAlign="center">
          <Text fontSize="md" fontWeight="bold" color="blue.600">
            {data.protein_g}g
          </Text>
          <Text fontSize="xs" color="gray.500">
            PROTEIN
          </Text>
        </Box>
        <Box bg="yellow.50" p={2} borderRadius="lg" textAlign="center">
          <Text fontSize="md" fontWeight="bold" color="yellow.700">
            {data.carbs_g}g
          </Text>
          <Text fontSize="xs" color="gray.500">
            CARBS
          </Text>
        </Box>
        <Box bg="red.50" p={2} borderRadius="lg" textAlign="center">
          <Text fontSize="md" fontWeight="bold" color="red.500">
            {data.fat_g}g
          </Text>
          <Text fontSize="xs" color="gray.500">
            FAT
          </Text>
        </Box>
      </SimpleGrid>
    </Box>
  )
}

/**
 * Check if action data contains vision-specific fields.
 * Used to determine whether to render VisionResponseCard vs generic ActionCard.
 */
export function isVisionResponse(
  actionType: string,
  actionData: Record<string, unknown> | null,
): boolean {
  if (!actionData) return false

  if (actionType === "log_exercise") {
    // Vision responses have form_cues array
    return Array.isArray(actionData.form_cues)
  }

  if (actionType === "log_food") {
    // Vision responses have meal_name (not just food/name)
    return typeof actionData.meal_name === "string"
  }

  return false
}
