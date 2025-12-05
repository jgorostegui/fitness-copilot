import {
  Box,
  Button,
  Flex,
  IconButton,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useEffect, useRef, useState } from "react"
import { FiCamera, FiMic, FiSend, FiX } from "react-icons/fi"
import { TODAY_ROUTINE } from "@/constants/fitness"
import { sendMessageToAI } from "@/services/mockAiService"
import type {
  DailyStats,
  ExerciseLog,
  MealLog,
  Message,
  UserProfile,
} from "@/types/fitness"

interface ChatInterfaceProps {
  history: Message[]
  setHistory: React.Dispatch<React.SetStateAction<Message[]>>
  onAction: (action: { type: string; data?: Record<string, unknown> }) => void
  stats: DailyStats
  profile: UserProfile
  mealLogs: MealLog[]
  exerciseLogs: ExerciseLog[]
}

const ActionCard = ({
  type,
  data,
  stats,
}: {
  type: string
  data: Record<string, unknown>
  stats: DailyStats
}) => {
  const [animate, setAnimate] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setAnimate(true), 100)
    return () => clearTimeout(timer)
  }, [])

  if (type === "log_food") {
    const itemCalories = (data?.calories as number) || 0
    const previousTotal = Math.max(0, stats.caloriesConsumed - itemCalories)
    const prevPercent = Math.min(
      100,
      (previousTotal / stats.caloriesTarget) * 100,
    )
    const currentPercent = Math.min(
      100,
      (stats.caloriesConsumed / stats.caloriesTarget) * 100,
    )

    return (
      <Box
        mt={2}
        bg="white"
        border="1px"
        borderColor="gray.200"
        borderRadius="xl"
        p={3}
        maxW="280px"
      >
        <Flex justify="space-between" align="center" mb={2}>
          <Flex align="center" gap={2}>
            <Box bg="orange.50" p={1.5} borderRadius="lg" color="orange.500">
              🔥
            </Box>
            <Box>
              <Text fontSize="sm" fontWeight="bold">
                {data.name as string}
              </Text>
              <Text fontSize="xs" color="gray.500">
                Logged to Daily Intake
              </Text>
            </Box>
          </Flex>
          <Box textAlign="right">
            <Text fontSize="sm" fontWeight="bold">
              +{itemCalories}
            </Text>
            <Text fontSize="xs" color="gray.400">
              KCAL
            </Text>
          </Box>
        </Flex>
        <Box>
          <Flex justify="space-between" fontSize="xs" color="gray.500" mb={1}>
            <Text>Daily Energy</Text>
            <Text>
              {stats.caloriesConsumed} / {stats.caloriesTarget}
            </Text>
          </Flex>
          <Box
            h={2}
            bg="gray.100"
            borderRadius="full"
            overflow="hidden"
            position="relative"
          >
            <Box
              position="absolute"
              top={0}
              left={0}
              h="full"
              bg="gray.300"
              borderRadius="full"
              w={`${prevPercent}%`}
              transition="width 1s"
            />
            <Box
              position="absolute"
              top={0}
              h="full"
              bg="blue.500"
              borderRadius="full"
              left={`${prevPercent}%`}
              w={animate ? `${currentPercent - prevPercent}%` : "0%"}
              transition="width 1s"
              boxShadow="0 0 10px rgba(59,130,246,0.5)"
            />
          </Box>
        </Box>
        {(data.protein as number) > 0 && (
          <Flex
            mt={2}
            align="center"
            gap={1}
            fontSize="xs"
            color="green.600"
            bg="green.50"
            px={2}
            py={1}
            borderRadius="md"
            w="fit-content"
          >
            ✓ {data.protein as number}g Protein Added
          </Flex>
        )}
      </Box>
    )
  }

  if (type === "log_exercise") {
    return (
      <Box
        mt={2}
        bg="white"
        border="1px"
        borderColor="gray.200"
        borderRadius="xl"
        p={3}
        maxW="280px"
      >
        <Flex justify="space-between" align="center" mb={2}>
          <Flex align="center" gap={2}>
            <Box bg="purple.50" p={1.5} borderRadius="lg" color="purple.500">
              🏋️
            </Box>
            <Box>
              <Text fontSize="sm" fontWeight="bold">
                {data.name as string}
              </Text>
              <Text fontSize="xs" color="gray.500">
                Workout Logged
              </Text>
            </Box>
          </Flex>
          <Text fontSize="sm" fontWeight="bold">
            {data.weight as number}kg
          </Text>
        </Flex>
        <Flex gap={2}>
          <Box flex={1} bg="gray.50" p={2} borderRadius="lg" textAlign="center">
            <Text fontSize="sm" fontWeight="bold">
              {data.sets as number}
            </Text>
            <Text fontSize="xs" color="gray.400">
              SETS
            </Text>
          </Box>
          <Box flex={1} bg="gray.50" p={2} borderRadius="lg" textAlign="center">
            <Text fontSize="sm" fontWeight="bold">
              {data.reps as number}
            </Text>
            <Text fontSize="xs" color="gray.400">
              REPS
            </Text>
          </Box>
        </Flex>
      </Box>
    )
  }

  return null
}

const ContextWidget = ({
  mode,
  toggleMode,
  stats,
  exerciseLogs,
  mealLogs,
  onQuickLog,
}: {
  mode: "gym" | "kitchen"
  toggleMode: () => void
  stats: DailyStats
  exerciseLogs: ExerciseLog[]
  mealLogs: MealLog[]
  onQuickLog: (text: string) => void
}) => {
  const [sessionTime, setSessionTime] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => setSessionTime((prev) => prev + 1), 1000)
    return () => clearInterval(timer)
  }, [])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, "0")}`
  }

  if (mode === "gym") {
    const completedNames = new Set(
      exerciseLogs.map((l) => l.name.toLowerCase()),
    )
    const nextIndex = TODAY_ROUTINE.findIndex(
      (r) => !completedNames.has(r.exercise.toLowerCase()),
    )
    const currentTarget = nextIndex !== -1 ? TODAY_ROUTINE[nextIndex] : null
    const allDone = nextIndex === -1 && TODAY_ROUTINE.length > 0

    return (
      <Box
        bg="white"
        borderBottom="1px"
        borderColor="gray.200"
        px={4}
        py={3}
        cursor="pointer"
        onClick={toggleMode}
        _active={{ bg: "gray.50" }}
      >
        <Flex justify="space-between" align="start">
          <Box>
            <Text
              fontSize="xs"
              fontWeight="bold"
              color="blue.600"
              bg="blue.50"
              px={2}
              py={0.5}
              borderRadius="sm"
              w="fit-content"
              mb={1}
            >
              🏋️ GYM MODE
            </Text>
            <Text fontSize="lg" fontWeight="bold">
              {allDone
                ? "Session Complete ✓"
                : currentTarget?.exercise || "Rest Day"}
            </Text>
            {!allDone && currentTarget && (
              <Flex gap={2} mt={1}>
                <Text
                  fontSize="xs"
                  bg="gray.100"
                  px={1.5}
                  py={0.5}
                  borderRadius="sm"
                >
                  {currentTarget.sets} Sets
                </Text>
                <Text
                  fontSize="xs"
                  bg="gray.100"
                  px={1.5}
                  py={0.5}
                  borderRadius="sm"
                >
                  {currentTarget.reps} Reps
                </Text>
                <Text fontSize="xs" color="blue.600">
                  {currentTarget.target}
                </Text>
              </Flex>
            )}
          </Box>
          <Box textAlign="right">
            <Text fontSize="xs" color="gray.400">
              Session
            </Text>
            <Text fontSize="xl" fontWeight="bold" fontFamily="mono">
              {formatTime(sessionTime)}
            </Text>
          </Box>
        </Flex>
        <Text fontSize="xs" color="gray.400" mt={2} textAlign="center">
          Tap to switch to Kitchen mode
        </Text>
      </Box>
    )
  }

  const caloriesLeft = Math.max(
    0,
    stats.caloriesTarget - stats.caloriesConsumed,
  )
  const recentLogs = mealLogs.slice(-3).reverse()

  return (
    <Box bg="white" borderBottom="1px" borderColor="gray.200" px={4} py={3}>
      <Flex
        justify="space-between"
        align="start"
        cursor="pointer"
        onClick={toggleMode}
        _active={{ opacity: 0.8 }}
      >
        <Box>
          <Text
            fontSize="xs"
            fontWeight="bold"
            color="green.600"
            bg="green.50"
            px={2}
            py={0.5}
            borderRadius="sm"
            w="fit-content"
            mb={1}
          >
            🍽️ KITCHEN MODE
          </Text>
          <Flex align="baseline" gap={1}>
            <Text fontSize="3xl" fontWeight="bold">
              {Math.round(caloriesLeft)}
            </Text>
            <Text fontSize="xs" fontWeight="bold" color="gray.400">
              kcal left
            </Text>
          </Flex>
        </Box>
        <Box textAlign="right">
          <Text fontSize="xs" color="gray.400">
            Protein Left
          </Text>
          <Text fontSize="xl" fontWeight="bold" fontFamily="mono">
            {Math.max(
              0,
              Math.round(stats.proteinTarget - stats.proteinConsumed),
            )}
            g
          </Text>
        </Box>
      </Flex>

      <Box mt={3}>
        <Text fontSize="xs" fontWeight="bold" color="gray.400" mb={2}>
          QUICK ADD
        </Text>
        <Flex gap={2} flexWrap="wrap">
          {[
            { emoji: "🍌", name: "Banana", text: "I ate a Banana" },
            { emoji: "🥤", name: "Shake", text: "I had a Protein Shake" },
            { emoji: "☕", name: "Coffee", text: "I drank a Coffee" },
            { emoji: "🥚", name: "Eggs", text: "I ate 2 Eggs" },
          ].map((item, idx) => (
            <Button
              key={idx}
              size="sm"
              variant="outline"
              onClick={(e) => {
                e.stopPropagation()
                onQuickLog(item.text)
              }}
            >
              {item.emoji} {item.name}
            </Button>
          ))}
        </Flex>
      </Box>

      {recentLogs.length > 0 && (
        <Flex gap={2} mt={3} overflow="hidden">
          {recentLogs.map((log) => (
            <Flex
              key={log.id}
              align="center"
              gap={1}
              bg="gray.50"
              px={2}
              py={1}
              borderRadius="full"
              border="1px"
              borderColor="gray.100"
            >
              <Box w={1.5} h={1.5} borderRadius="full" bg="green.400" />
              <Text fontSize="xs" color="gray.600" maxW="80px" truncate>
                {log.name}
              </Text>
            </Flex>
          ))}
        </Flex>
      )}

      <Text fontSize="xs" color="gray.400" mt={2} textAlign="center">
        Tap to switch to Gym mode
      </Text>
    </Box>
  )
}

export const ChatInterface = ({
  history,
  setHistory,
  onAction,
  stats,
  mealLogs,
  exerciseLogs,
}: ChatInterfaceProps) => {
  const [inputText, setInputText] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [widgetMode, setWidgetMode] = useState<"gym" | "kitchen">("gym")
  const fileInputRef = useRef<HTMLInputElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [])

  useEffect(() => {
    const lastMsg = history[history.length - 1]
    if (lastMsg?.actionType === "log_food") {
      setWidgetMode("kitchen")
    } else if (lastMsg?.actionType === "log_exercise") {
      setWidgetMode("gym")
    }
  }, [history])

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      const reader = new FileReader()
      reader.onload = (ev) => setSelectedImage(ev.target?.result as string)
      reader.readAsDataURL(e.target.files[0])
    }
  }

  const handleSend = async (textOverride?: string) => {
    const textToSend = textOverride || inputText
    if ((!textToSend.trim() && !selectedImage) || isTyping) return

    const userMsg: Message = {
      id: Date.now().toString(),
      text: textToSend,
      sender: "user",
      timestamp: new Date(),
      image: selectedImage || undefined,
    }

    setHistory((prev) => [...prev, userMsg])
    setInputText("")
    setSelectedImage(null)
    setIsTyping(true)

    const response = await sendMessageToAI(
      history,
      userMsg.text || (userMsg.image ? "Analyze this image" : ""),
      userMsg.image,
    )

    const aiMsg: Message = {
      id: (Date.now() + 1).toString(),
      text: response.text,
      sender: "ai",
      timestamp: new Date(),
      actionType: (response.action?.type as Message["actionType"]) || "none",
      actionData: response.action?.data as Message["actionData"],
    }

    setHistory((prev) => [...prev, aiMsg])

    if (response.action && response.action.type !== "none") {
      onAction(response.action)
    }

    setIsTyping(false)
  }

  const toggleRecording = () => {
    if (!isRecording) {
      setIsRecording(true)
      setTimeout(() => {
        setIsRecording(false)
        setInputText("I just did 3 sets of leg press at 100kg")
      }, 2000)
    }
  }

  return (
    <Flex direction="column" h="full" bg="gray.50" position="relative">
      <ContextWidget
        mode={widgetMode}
        toggleMode={() =>
          setWidgetMode((m) => (m === "gym" ? "kitchen" : "gym"))
        }
        stats={stats}
        exerciseLogs={exerciseLogs}
        mealLogs={mealLogs}
        onQuickLog={(text) => handleSend(text)}
      />

      <Box flex={1} overflowY="auto" p={4} pb={32}>
        <VStack gap={3} align="stretch">
          {history.map((msg) => (
            <Flex
              key={msg.id}
              direction="column"
              align={msg.sender === "user" ? "flex-end" : "flex-start"}
            >
              <Box
                maxW="85%"
                bg={msg.sender === "user" ? "blue.500" : "white"}
                color={msg.sender === "user" ? "white" : "gray.800"}
                borderRadius="2xl"
                borderTopRightRadius={msg.sender === "user" ? "sm" : "2xl"}
                borderTopLeftRadius={msg.sender === "user" ? "2xl" : "sm"}
                p={3}
                border={msg.sender === "ai" ? "1px" : "none"}
                borderColor="gray.200"
              >
                {msg.image && (
                  <Box mb={2} borderRadius="lg" overflow="hidden">
                    <img
                      src={msg.image}
                      alt="Upload"
                      style={{ maxHeight: "150px", objectFit: "cover" }}
                    />
                  </Box>
                )}
                <Text fontSize="sm" whiteSpace="pre-wrap">
                  {msg.text}
                </Text>
              </Box>

              {msg.actionType &&
                msg.actionType !== "none" &&
                msg.actionData && (
                  <ActionCard
                    type={msg.actionType}
                    data={msg.actionData}
                    stats={stats}
                  />
                )}

              <Text fontSize="xs" color="gray.400" mt={1} px={1}>
                {msg.timestamp.toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </Text>
            </Flex>
          ))}

          {isTyping && (
            <Flex align="flex-start">
              <Box
                bg="white"
                borderRadius="2xl"
                borderTopLeftRadius="sm"
                p={3}
                border="1px"
                borderColor="gray.200"
              >
                <Flex gap={1}>
                  <Box
                    w={2}
                    h={2}
                    bg="gray.400"
                    borderRadius="full"
                    animation="bounce 1s infinite"
                  />
                  <Box
                    w={2}
                    h={2}
                    bg="gray.400"
                    borderRadius="full"
                    animation="bounce 1s infinite 0.1s"
                  />
                  <Box
                    w={2}
                    h={2}
                    bg="gray.400"
                    borderRadius="full"
                    animation="bounce 1s infinite 0.2s"
                  />
                </Flex>
              </Box>
            </Flex>
          )}
          <div ref={messagesEndRef} />
        </VStack>
      </Box>

      <Box
        position="absolute"
        bottom={16}
        left={0}
        right={0}
        bg="white"
        borderTop="1px"
        borderColor="gray.200"
        p={3}
      >
        {selectedImage && (
          <Flex
            mb={2}
            bg="gray.50"
            p={2}
            borderRadius="lg"
            align="center"
            gap={2}
          >
            <img
              src={selectedImage}
              alt="Preview"
              style={{
                width: "40px",
                height: "40px",
                objectFit: "cover",
                borderRadius: "8px",
              }}
            />
            <Text fontSize="xs" color="gray.500">
              Image attached
            </Text>
            <IconButton
              aria-label="Remove image"
              size="xs"
              variant="ghost"
              onClick={() => setSelectedImage(null)}
            >
              <FiX />
            </IconButton>
          </Flex>
        )}

        <Flex gap={2} align="center">
          <input
            type="file"
            accept="image/*"
            ref={fileInputRef}
            style={{ display: "none" }}
            onChange={handleImageSelect}
          />

          <IconButton
            aria-label="Attach photo"
            variant="ghost"
            onClick={() => fileInputRef.current?.click()}
          >
            <FiCamera />
          </IconButton>

          <Input
            flex={1}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder={isRecording ? "Listening..." : "Message..."}
            bg={isRecording ? "red.50" : "gray.100"}
            border="none"
            borderRadius="full"
          />

          <IconButton
            aria-label="Voice input"
            variant="ghost"
            color={isRecording ? "red.500" : "gray.500"}
            onClick={toggleRecording}
          >
            <FiMic />
          </IconButton>

          <IconButton
            aria-label="Send"
            colorPalette="blue"
            borderRadius="full"
            disabled={!inputText && !selectedImage}
            onClick={() => handleSend()}
          >
            <FiSend />
          </IconButton>
        </Flex>
      </Box>
    </Flex>
  )
}
