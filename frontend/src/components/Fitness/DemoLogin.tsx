import { Box, Button, Flex, Heading, SimpleGrid, Text } from "@chakra-ui/react"
import { useState } from "react"
import type { DemoPersona } from "@/hooks/useAuth"

interface DemoLoginProps {
  onLogin: (persona: DemoPersona) => Promise<void>
  isLoading: boolean
}

interface PersonaCard {
  id: DemoPersona
  title: string
  emoji: string
  description: string
  stats: string
  color: string
}

const PERSONAS: PersonaCard[] = [
  {
    id: "cut",
    title: "Cutting",
    emoji: "🔥",
    description: "Lose fat while preserving muscle",
    stats: "85kg • 180cm • Moderate deficit",
    color: "red",
  },
  {
    id: "bulk",
    title: "Bulking",
    emoji: "💪",
    description: "Build muscle with caloric surplus",
    stats: "90kg • 185cm • Moderate surplus",
    color: "green",
  },
  {
    id: "maintain",
    title: "Maintenance",
    emoji: "⚖️",
    description: "Maintain current physique",
    stats: "60kg • 165cm • Balanced intake",
    color: "blue",
  },
]

export function DemoLogin({ onLogin, isLoading }: DemoLoginProps) {
  const [selectedPersona, setSelectedPersona] = useState<DemoPersona | null>(
    null,
  )

  const handleLogin = async (persona: DemoPersona) => {
    setSelectedPersona(persona)
    try {
      await onLogin(persona)
    } catch {
      setSelectedPersona(null)
    }
  }

  return (
    <Flex
      direction="column"
      align="center"
      justify="center"
      minH="100vh"
      bg="gray.50"
      p={6}
    >
      <Box textAlign="center" mb={8}>
        <Heading size="2xl" mb={2}>
          🏋️ Fitness Copilot
        </Heading>
        <Text color="gray.600" fontSize="lg">
          Choose a demo profile to get started
        </Text>
      </Box>

      <SimpleGrid columns={{ base: 1, md: 3 }} gap={4} maxW="900px" w="full">
        {PERSONAS.map((persona) => (
          <Box
            key={persona.id}
            bg="white"
            borderRadius="xl"
            p={6}
            border="2px"
            borderColor={
              selectedPersona === persona.id ? `${persona.color}.400` : "gray.200"
            }
            cursor="pointer"
            transition="all 0.2s"
            _hover={{
              borderColor: `${persona.color}.300`,
              transform: "translateY(-2px)",
              shadow: "md",
            }}
            onClick={() => !isLoading && handleLogin(persona.id)}
          >
            <Text fontSize="4xl" mb={3}>
              {persona.emoji}
            </Text>
            <Heading size="md" mb={2}>
              {persona.title}
            </Heading>
            <Text color="gray.600" fontSize="sm" mb={3}>
              {persona.description}
            </Text>
            <Text color="gray.400" fontSize="xs">
              {persona.stats}
            </Text>
            <Button
              mt={4}
              w="full"
              colorPalette={persona.color}
              loading={isLoading && selectedPersona === persona.id}
              disabled={isLoading}
            >
              {isLoading && selectedPersona === persona.id
                ? "Loading..."
                : "Start Demo"}
            </Button>
          </Box>
        ))}
      </SimpleGrid>

      <Text color="gray.400" fontSize="sm" mt={8} textAlign="center">
        Demo mode creates a temporary user with pre-filled profile data.
        <br />
        Your data will persist in the database during the session.
      </Text>
    </Flex>
  )
}
