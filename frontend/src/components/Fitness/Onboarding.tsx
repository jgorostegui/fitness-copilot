import { Box, Button, Container, Heading, Input, Text, VStack } from "@chakra-ui/react"
import { useState } from "react"
import type { PlanType, UserProfile } from "@/types/fitness"

interface OnboardingProps {
  onComplete: (profile: UserProfile) => void
}

export const Onboarding = ({ onComplete }: OnboardingProps) => {
  const [weight, setWeight] = useState(80)
  const [height, setHeight] = useState(180)
  const [plan, setPlan] = useState<PlanType>("maintain")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onComplete({
      weight,
      height,
      plan,
      theme: "light",
      onboardingComplete: true,
    })
  }

  return (
    <Container maxW="sm" h="100vh" display="flex" alignItems="center" justifyContent="center">
      <Box as="form" onSubmit={handleSubmit} w="full">
        <VStack gap={6} align="stretch">
          <Box textAlign="center">
            <Text fontSize="4xl" mb={2}>🏋️</Text>
            <Heading size="lg">Setup Profile</Heading>
            <Text color="gray.500" fontSize="sm">Let's calculate your baseline metrics</Text>
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

          <Button type="submit" colorPalette="blue" size="lg">
            Start Journey →
          </Button>
        </VStack>
      </Box>
    </Container>
  )
}
