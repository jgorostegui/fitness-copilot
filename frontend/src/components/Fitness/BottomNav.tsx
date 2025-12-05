import { Box, Flex, Text } from "@chakra-ui/react"
import { FiHome, FiMessageSquare, FiUser } from "react-icons/fi"
import { GiWeightLiftingUp } from "react-icons/gi"
import { IoNutritionOutline } from "react-icons/io5"

type Tab = "monitor" | "workout" | "chat" | "nutrition" | "profile"

interface BottomNavProps {
  activeTab: Tab
  onTabChange: (tab: Tab) => void
}

const TabButton = ({
  active,
  onClick,
  icon: Icon,
  label,
  isCenter,
}: {
  active: boolean
  onClick: () => void
  icon: React.ElementType
  label: string
  isCenter?: boolean
}) => {
  if (isCenter) {
    return (
      <Flex direction="column" align="center" position="relative" top={-4}>
        <Box
          as="button"
          onClick={onClick}
          w={14}
          h={14}
          borderRadius="full"
          bg={active ? "blue.600" : "blue.500"}
          color="white"
          display="flex"
          alignItems="center"
          justifyContent="center"
          boxShadow="lg"
          _active={{ transform: "scale(0.95)" }}
          transition="all 0.2s"
        >
          <Icon size={24} />
        </Box>
        <Text
          fontSize="xs"
          fontWeight={active ? "bold" : "medium"}
          color={active ? "blue.600" : "gray.400"}
          mt={1}
        >
          {label}
        </Text>
      </Flex>
    )
  }

  return (
    <Flex
      as="button"
      direction="column"
      align="center"
      justify="flex-end"
      gap={1}
      w={14}
      h="full"
      pb={2}
      onClick={onClick}
      color={active ? "blue.600" : "gray.400"}
      _active={{ transform: "scale(0.95)" }}
      transition="all 0.2s"
    >
      <Icon size={20} />
      <Text fontSize="10px" fontWeight={active ? "bold" : "medium"}>
        {label}
      </Text>
    </Flex>
  )
}

export const BottomNav = ({ activeTab, onTabChange }: BottomNavProps) => {
  return (
    <Box
      position="fixed"
      bottom={0}
      left={0}
      right={0}
      bg="white"
      borderTop="1px"
      borderColor="gray.200"
      zIndex={50}
      h={16}
    >
      <Flex justify="space-around" align="flex-end" h="full" px={1} pb={1}>
        <TabButton
          active={activeTab === "monitor"}
          onClick={() => onTabChange("monitor")}
          icon={FiHome}
          label="Monitor"
        />
        <TabButton
          active={activeTab === "workout"}
          onClick={() => onTabChange("workout")}
          icon={GiWeightLiftingUp}
          label="Workout"
        />
        <TabButton
          active={activeTab === "chat"}
          onClick={() => onTabChange("chat")}
          icon={FiMessageSquare}
          label="Chat"
          isCenter
        />
        <TabButton
          active={activeTab === "nutrition"}
          onClick={() => onTabChange("nutrition")}
          icon={IoNutritionOutline}
          label="Nutrition"
        />
        <TabButton
          active={activeTab === "profile"}
          onClick={() => onTabChange("profile")}
          icon={FiUser}
          label="Profile"
        />
      </Flex>
    </Box>
  )
}
