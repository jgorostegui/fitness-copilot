import {
  Box,
  Button,
  Container,
  Flex,
  Heading,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useState } from "react"
import { FiLogOut, FiMoon, FiSun } from "react-icons/fi"
import type { PlanType, UserProfile } from "@/types/fitness"

interface ProfileProps {
  profile: UserProfile
  onUpdate: (profile: UserProfile) => void
  onReset: () => void
  onLogout?: () => void
}

export const Profile = ({ profile, onUpdate, onReset, onLogout }: ProfileProps) => {
  const [weight, setWeight] = useState(profile.weight)
  const [height, setHeight] = useState(profile.height)
  const [plan, setPlan] = useState<PlanType>(profile.plan)
  const [theme, setTheme] = useState<"light" | "dark">(profile.theme)

  const handleSave = () => {
    onUpdate({ ...profile, weight, height, plan, theme })
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
          <Heading size="md">Settings</Heading>
          <Button
            variant="ghost"
            colorPalette="blue"
            size="sm"
            onClick={handleSave}
          >
            Save
          </Button>
        </Flex>
      </Box>

      <Container maxW="full" p={4}>
        <VStack gap={6} align="stretch">
          <Flex direction="column" align="center" py={4}>
            <Box
              w={20}
              h={20}
              bg="gray.100"
              borderRadius="full"
              display="flex"
              alignItems="center"
              justifyContent="center"
              fontSize="3xl"
              mb={3}
            >
              🤖
            </Box>
            <Heading size="sm">Operator</Heading>
            <Text fontSize="sm" color="gray.500">
              Fitness Copilot User
            </Text>
          </Flex>

          <Box>
            <Text fontSize="xs" fontWeight="semibold" color="gray.500" mb={2}>
              APPEARANCE
            </Text>
            <Flex
              bg="white"
              borderRadius="xl"
              border="1px"
              borderColor="gray.200"
              p={1}
            >
              <Button
                flex={1}
                variant={theme === "light" ? "solid" : "ghost"}
                size="sm"
                onClick={() => setTheme("light")}
              >
                <FiSun /> Light
              </Button>
              <Button
                flex={1}
                variant={theme === "dark" ? "solid" : "ghost"}
                size="sm"
                onClick={() => setTheme("dark")}
              >
                <FiMoon /> Dark
              </Button>
            </Flex>
          </Box>

          <Box>
            <Text fontSize="xs" fontWeight="semibold" color="gray.500" mb={2}>
              BIOMETRICS
            </Text>
            <VStack
              bg="white"
              borderRadius="xl"
              border="1px"
              borderColor="gray.200"
              divideY="1px"
              divideColor="gray.100"
              gap={0}
            >
              <Flex w="full" justify="space-between" align="center" p={4}>
                <Flex align="center" gap={3}>
                  <Box bg="blue.50" p={1.5} borderRadius="md" color="blue.600">
                    ⚖️
                  </Box>
                  <Text fontSize="sm" fontWeight="medium">
                    Weight
                  </Text>
                </Flex>
                <Flex align="center" gap={2}>
                  <Input
                    type="number"
                    value={weight}
                    onChange={(e) => setWeight(Number(e.target.value))}
                    w={16}
                    textAlign="right"
                    size="sm"
                    variant="flushed"
                  />
                  <Text fontSize="sm" color="gray.400">
                    kg
                  </Text>
                </Flex>
              </Flex>

              <Flex w="full" justify="space-between" align="center" p={4}>
                <Flex align="center" gap={3}>
                  <Box
                    bg="indigo.50"
                    p={1.5}
                    borderRadius="md"
                    color="indigo.600"
                  >
                    📏
                  </Box>
                  <Text fontSize="sm" fontWeight="medium">
                    Height
                  </Text>
                </Flex>
                <Flex align="center" gap={2}>
                  <Input
                    type="number"
                    value={height}
                    onChange={(e) => setHeight(Number(e.target.value))}
                    w={16}
                    textAlign="right"
                    size="sm"
                    variant="flushed"
                  />
                  <Text fontSize="sm" color="gray.400">
                    cm
                  </Text>
                </Flex>
              </Flex>
            </VStack>
          </Box>

          <Box>
            <Text fontSize="xs" fontWeight="semibold" color="gray.500" mb={2}>
              STRATEGY
            </Text>
            <Box
              bg="white"
              borderRadius="xl"
              border="1px"
              borderColor="gray.200"
              p={4}
            >
              <Flex justify="space-between" align="center">
                <Flex align="center" gap={3}>
                  <Box
                    bg="green.50"
                    p={1.5}
                    borderRadius="md"
                    color="green.600"
                  >
                    🎯
                  </Box>
                  <Text fontSize="sm" fontWeight="medium">
                    Current Phase
                  </Text>
                </Flex>
                <select
                  value={plan}
                  onChange={(e) => setPlan(e.target.value as PlanType)}
                  style={{
                    background: "transparent",
                    border: "none",
                    fontSize: "14px",
                    fontWeight: 500,
                    textAlign: "right",
                  }}
                >
                  <option value="cut">Cut</option>
                  <option value="maintain">Maintain</option>
                  <option value="bulk">Bulk</option>
                </select>
              </Flex>
            </Box>
          </Box>

          <Box pt={8}>
            <VStack gap={3}>
              <Button
                w="full"
                variant="outline"
                colorPalette="gray"
                onClick={onReset}
              >
                Reset Profile Data
              </Button>
              {onLogout && (
                <Button
                  w="full"
                  variant="outline"
                  colorPalette="red"
                  onClick={onLogout}
                >
                  <FiLogOut /> Logout
                </Button>
              )}
            </VStack>
            <Text textAlign="center" fontSize="xs" color="gray.400" mt={4}>
              Fitness Copilot v0.1.0
            </Text>
          </Box>
        </VStack>
      </Container>
    </Box>
  )
}
