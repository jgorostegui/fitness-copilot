import {
  Box,
  Button,
  Container,
  Flex,
  Heading,
  IconButton,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { FiArrowLeft } from "react-icons/fi"
import { useState } from "react"
import type { UserProfilePublic } from "../../client/types.gen"
import type { PlanType, UserProfile } from "@/types/fitness"

interface OnboardingProps {
  onComplete: (profile: UserProfile) => void | Promise<void>
  initialProfile?: UserProfilePublic
  onBack?: () => void
}

// Map API goal method to local plan type
const mapGoalToPlan = (goalMethod?: string | null): PlanType => {
  if (!goalMethod) return "maintain"
  if (goalMethod.includes("cut")) return "cut"
  if (goalMethod.includes("gain")) return "bulk"
  return "maintain"
}

export const Onboarding = ({
  onComplete,
  initialProfile,
  onBack,
}: OnboardingProps) => {
  const [weight, setWeight] = useState(initialProfile?.weightKg ?? 80)
  const [height, setHeight] = useState(initialProfile?.heightCm ?? 180)
  const [plan, setPlan] = useState<PlanType>(
    mapGoalToPlan(initialProfile?.goalMethod),
  )
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    try {
      await onComplete({
        weight,
        height,
        plan,
        theme: "light",
        onboardingComplete: true,
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Container
      maxW="sm"
      h="100vh"
      display="flex"
      alignItems="center"
      justifyContent="center"
      position="relative"
    >
      {onBack && (
        <Flex
          position="absolute"
          top={4}
          left={4}
          right={4}
          justify="flex-start"
        >
          <IconButton
            aria-label="Go back"
            variant="ghost"
            onClick={onBack}
            size="lg"
          >
            <FiArrowLeft />
          </IconButton>
        </Flex>
      )}
      <Box as="form" onSubmit={handleSubmit} w="full">
        <VStack gap={6} align="stretch">
          <Box textAlign="center">
            <Text fontSize="4xl" mb={2}>
              🏋️
            </Text>
            <Heading size="lg">Setup Profile</Heading>
            <Text color="gray.500" fontSize="sm">
              Let's calculate your baseline metrics
            </Text>
          </Box>

          <Box>
            <Text fontSize="xs" fontWeight="semibold" color="gray.500" mb={1}>
              WEIGHT (KG)
            </Text>
            <Input
              type="number"
              value={weight}
              onChange={(e) => setWeight(Number(e.target.value))}
              size="lg"
            />
          </Box>

          <Box>
            <Text fontSize="xs" fontWeight="semibold" color="gray.500" mb={1}>
              HEIGHT (CM)
            </Text>
            <Input
              type="number"
              value={height}
              onChange={(e) => setHeight(Number(e.target.value))}
              size="lg"
            />
          </Box>

          <Box>
            <Text fontSize="xs" fontWeight="semibold" color="gray.500" mb={2}>
              GOAL
            </Text>
            <Box display="flex" gap={2}>
              {(["cut", "maintain", "bulk"] as PlanType[]).map((p) => (
                <Button
                  key={p}
                  flex={1}
                  variant={plan === p ? "solid" : "outline"}
                  colorPalette={plan === p ? "blue" : "gray"}
                  onClick={() => setPlan(p)}
                  type="button"
                >
                  {p.charAt(0).toUpperCase() + p.slice(1)}
                </Button>
              ))}
            </Box>
          </Box>

          <Button
            type="submit"
            colorPalette="blue"
            size="lg"
            loading={isSubmitting}
            disabled={isSubmitting}
          >
            Start Journey →
          </Button>
        </VStack>
      </Box>
    </Container>
  )
}
