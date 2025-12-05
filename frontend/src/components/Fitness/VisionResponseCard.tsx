import {
  Badge,
  Box,
  Button,
  Flex,
  SimpleGrid,
  Spinner,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useState } from "react"
import { FiCheck, FiPlus, FiInfo } from "react-icons/fi"
import { Chat } from "@/client/sdk.gen"
import { useQueryClient } from "@tanstack/react-query"

interface GymAnalysis {
  exercise_name: string
  sets: number
  reps: number
  weight_kg: number
  hiddenContext?: {
    formCues?: string[]
  }
}

interface FoodAnalysis {
  meal_name: string
  calories: number
  protein_g: number
  carbs_g: number
  fat_g: number
}

type ActionType =
  | "log_exercise"
  | "log_food"
  | "propose_exercise"
  | "propose_food"

interface VisionResponseCardProps {
  messageId: string
  actionType: ActionType
  actionData: Record<string, unknown>
  isTracked?: boolean
  onTrackingConfirmed?: () => void
}

/**
 * Specialized card for displaying vision analysis results.
 * Shows gym equipment analysis with form cues or food analysis with macros.
 * Supports preview mode (propose_*) with "Add to Track" button.
 */
export function VisionResponseCard({
  messageId,
  actionType,
  actionData,
  isTracked: initialIsTracked,
  onTrackingConfirmed,
}: VisionResponseCardProps) {
  const queryClient = useQueryClient()
  const [isTracked, setIsTracked] = useState(
    initialIsTracked ?? actionData.isTracked === true
  )
  const [isConfirming, setIsConfirming] = useState(false)
  const [showFormTips, setShowFormTips] = useState(false)

  const isPreviewMode =
    actionType === "propose_food" || actionType === "propose_exercise"
  const isExercise =
    actionType === "log_exercise" || actionType === "propose_exercise"

  const handleConfirmTracking = async () => {
    if (isTracked || isConfirming) return

    setIsConfirming(true)
    try {
      await Chat.chatConfirmTracking({
        path: { message_id: messageId },
      })
      setIsTracked(true)
      // Invalidate logs and summary queries to refresh the data
      queryClient.invalidateQueries({ queryKey: ["logs"] })
      queryClient.invalidateQueries({ queryKey: ["summary"] })
      onTrackingConfirmed?.()
    } catch (error) {
      console.error("Failed to confirm tracking:", error)
    } finally {
      setIsConfirming(false)
    }
  }

  if (isExercise) {
    const data = actionData as unknown as GymAnalysis
    const formCues = data.hiddenContext?.formCues || []

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
            {isTracked ? (
              <Badge colorScheme="green" size="sm">
                <Flex align="center" gap={1}>
                  <FiCheck size={10} />
                  Tracked
                </Flex>
              </Badge>
            ) : isPreviewMode ? (
              <Badge colorScheme="yellow" size="sm">
                Preview
              </Badge>
            ) : (
              <Badge colorScheme="green" size="sm">
                ✓ Logged
              </Badge>
            )}
          </Box>
        </Flex>

        {/* Form Tips Section - Hidden by default for preview mode */}
        {showFormTips && formCues.length > 0 && (
          <Box mb={3} bg="purple.50" p={3} borderRadius="lg">
            <Text fontSize="xs" fontWeight="bold" color="purple.600" mb={1}>
              💡 FORM TIPS
            </Text>
            <VStack align="start" gap={1}>
              {formCues.map((cue, i) => (
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

        {/* Action Buttons */}
        {isPreviewMode && (
          <Flex mt={3} gap={2} direction="column">
            {!isTracked && (
              <Button
                size="sm"
                colorPalette="purple"
                onClick={handleConfirmTracking}
                disabled={isConfirming}
                width="full"
              >
                {isConfirming ? (
                  <Flex align="center" gap={2}>
                    <Spinner size="xs" />
                    Adding...
                  </Flex>
                ) : (
                  <Flex align="center" gap={2}>
                    <FiPlus />
                    Add to Track
                  </Flex>
                )}
              </Button>
            )}
            {formCues.length > 0 && !showFormTips && (
              <Button
                size="sm"
                variant="outline"
                colorPalette="purple"
                onClick={() => setShowFormTips(true)}
                width="full"
              >
                <Flex align="center" gap={2}>
                  <FiInfo />
                  Show Form Tips
                </Flex>
              </Button>
            )}
          </Flex>
        )}
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
          {isTracked ? (
            <Badge colorScheme="green" size="sm">
              <Flex align="center" gap={1}>
                <FiCheck size={10} />
                Tracked
              </Flex>
            </Badge>
          ) : isPreviewMode ? (
            <Badge colorScheme="yellow" size="sm">
              Preview
            </Badge>
          ) : (
            <Badge colorScheme="green" size="sm">
              ✓ Logged
            </Badge>
          )}
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

      {/* Add to Track Button for preview mode */}
      {isPreviewMode && !isTracked && (
        <Button
          mt={3}
          size="sm"
          colorPalette="green"
          onClick={handleConfirmTracking}
          disabled={isConfirming}
          width="full"
        >
          {isConfirming ? (
            <Flex align="center" gap={2}>
              <Spinner size="xs" />
              Adding...
            </Flex>
          ) : (
            <Flex align="center" gap={2}>
              <FiPlus />
              Add to Track
            </Flex>
          )}
        </Button>
      )}
    </Box>
  )
}

/**
 * Check if action data contains vision-specific fields.
 * Used to determine whether to render VisionResponseCard vs generic ActionCard.
 */
export function isVisionResponse(
  actionType: string,
  actionData: Record<string, unknown> | null
): boolean {
  if (!actionData) return false

  // Handle propose_* action types (vision preview mode)
  if (actionType === "propose_exercise") {
    return typeof actionData.exercise_name === "string"
  }

  if (actionType === "propose_food") {
    return typeof actionData.meal_name === "string"
  }

  // Handle log_* action types (legacy direct logging)
  if (actionType === "log_exercise") {
    // Vision responses have hiddenContext with formCues
    return (
      typeof actionData.exercise_name === "string" ||
      Array.isArray(actionData.form_cues)
    )
  }

  if (actionType === "log_food") {
    // Vision responses have meal_name (not just food/name)
    return typeof actionData.meal_name === "string"
  }

  return false
}
