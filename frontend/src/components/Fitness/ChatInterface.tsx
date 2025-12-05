import {
  Box,
  Flex,
  Heading,
  IconButton,
  Input,
  Spinner,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useEffect, useRef, useState } from "react"
import { FiCamera, FiMic, FiSend } from "react-icons/fi"
import type {
  ChatMessagePublic,
  ExerciseLogPublic,
  MealLogPublic,
} from "@/client/types.gen"
import { ActionCard } from "@/components/Fitness/ActionCard"
import { AuthenticatedImage } from "@/components/Fitness/AuthenticatedImage"
import { ContextWidget } from "@/components/Fitness/ContextWidget"
import { DaySelector } from "@/components/Fitness/DaySelector"
import {
  isVisionResponse,
  VisionResponseCard,
} from "@/components/Fitness/VisionResponseCard"
import { useChat } from "@/hooks/useChat"
import { useImageUpload } from "@/hooks/useImageUpload"
import { useLogs } from "@/hooks/useLogs"
import { useSummary } from "@/hooks/useSummary"
import { useTrainingRoutine } from "@/hooks/useTrainingRoutine"
import type { DailyStats, ExerciseLog, MealLog } from "@/types/fitness"

// Convert API exercise log to local type
const mapExerciseLog = (log: ExerciseLogPublic): ExerciseLog => ({
  id: log.id,
  name: log.exerciseName,
  sets: log.sets,
  reps: log.reps,
  weight: log.weightKg,
  time: log.loggedAt,
})

// Convert API meal log to local type
const mapMealLog = (log: MealLogPublic): MealLog => ({
  id: log.id,
  name: log.mealName,
  calories: log.calories,
  protein: log.proteinG,
  time: log.loggedAt,
  type: log.mealType as MealLog["type"],
})

export function ChatInterface() {
  const [inputText, setInputText] = useState("")
  const [isRecording, setIsRecording] = useState(false)
  const [widgetMode, setWidgetMode] = useState<"gym" | "kitchen">("gym")
  const fileInputRef = useRef<HTMLInputElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const recordingTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Use API hooks
  const { messages, isLoading, sendMessage, isSending } = useChat()
  const { uploadImage, isUploading } = useImageUpload()
  const { mealLogs: apiMealLogs, exerciseLogs: apiExerciseLogs } = useLogs()
  const { summary } = useSummary()
  const { trainingRoutine } = useTrainingRoutine()

  // Map API logs to local types
  const mealLogs = apiMealLogs.map(mapMealLog)
  const exerciseLogs = apiExerciseLogs.map(mapExerciseLog)

  // Build stats from summary
  const stats: DailyStats = {
    caloriesConsumed: summary?.caloriesConsumed ?? 0,
    caloriesTarget: summary?.caloriesTarget ?? 2000,
    proteinConsumed: summary?.proteinConsumed ?? 0,
    proteinTarget: summary?.proteinTarget ?? 150,
    workoutsCompleted: summary?.workoutsCompleted ?? 0,
  }

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [])

  // Update widget mode based on last message action
  useEffect(() => {
    const lastMsg = messages[messages.length - 1]
    if (
      lastMsg?.actionType === "log_food" ||
      lastMsg?.actionType === "propose_food"
    ) {
      setWidgetMode("kitchen")
    } else if (
      lastMsg?.actionType === "log_exercise" ||
      lastMsg?.actionType === "propose_exercise"
    ) {
      setWidgetMode("gym")
    }
  }, [messages])

  const handleImageSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || isSending || isUploading) return

    // Reset file input so same file can be selected again
    e.target.value = ""

    try {
      const attachmentId = await uploadImage(file)
      sendMessage({
        content: "Analyze this image",
        attachment_type: "image",
        attachment_url: attachmentId,
      })
    } catch (error) {
      console.error("Image upload failed:", error)
    }
  }

  const handleSend = async (textOverride?: string) => {
    const textToSend = textOverride || inputText
    if (!textToSend.trim() || isSending) return

    sendMessage({
      content: textToSend,
      attachment_type: "none",
    })

    setInputText("")
  }

  const startRecording = () => {
    if (isSending) return
    setIsRecording(true)
    recordingTimeoutRef.current = setTimeout(() => {}, 500)
  }

  const stopRecording = () => {
    if (!isRecording) return
    setIsRecording(false)

    if (recordingTimeoutRef.current) {
      clearTimeout(recordingTimeoutRef.current)
      recordingTimeoutRef.current = null
    }

    sendMessage({
      content: "I just did 3 sets of leg press at 100kg",
      attachment_type: "audio",
      attachment_url: "mock://voice-recording",
    })
  }

  const renderMessage = (msg: ChatMessagePublic) => {
    const isUser = msg.role === "user"
    const timestamp = new Date(msg.createdAt)

    return (
      <Flex
        key={msg.id}
        direction="column"
        align={isUser ? "flex-end" : "flex-start"}
      >
        <Box
          maxW="85%"
          bg={isUser ? "blue.500" : "white"}
          color={isUser ? "white" : "gray.800"}
          borderRadius="2xl"
          borderTopRightRadius={isUser ? "sm" : "2xl"}
          borderTopLeftRadius={isUser ? "2xl" : "sm"}
          p={3}
          border={!isUser ? "1px" : "none"}
          borderColor="gray.200"
        >
          {msg.attachmentUrl && msg.attachmentType === "image" && (
            <Box mb={2} borderRadius="lg" overflow="hidden">
              {msg.attachmentUrl.startsWith("mock://") ? (
                <Flex
                  bg={isUser ? "blue.400" : "gray.100"}
                  p={4}
                  align="center"
                  justify="center"
                  borderRadius="lg"
                  minH="80px"
                >
                  <Text fontSize="2xl">📷</Text>
                  <Text
                    fontSize="sm"
                    color={isUser ? "blue.100" : "gray.500"}
                    ml={2}
                  >
                    Image attached
                  </Text>
                </Flex>
              ) : msg.attachmentUrl.startsWith("http") ? (
                <img
                  src={msg.attachmentUrl}
                  alt="User attachment"
                  style={{
                    maxHeight: "150px",
                    maxWidth: "100%",
                    objectFit: "cover",
                    borderRadius: "8px",
                  }}
                />
              ) : (
                <AuthenticatedImage attachmentId={msg.attachmentUrl} />
              )}
            </Box>
          )}
          <Text fontSize="sm" whiteSpace="pre-wrap">
            {msg.content}
          </Text>
        </Box>

        {msg.actionType &&
          msg.actionType !== "none" &&
          msg.actionData &&
          (isVisionResponse(
            msg.actionType,
            msg.actionData as Record<string, unknown>,
          ) ? (
            <VisionResponseCard
              messageId={msg.id}
              actionType={
                msg.actionType as
                  | "log_exercise"
                  | "log_food"
                  | "propose_exercise"
                  | "propose_food"
              }
              actionData={msg.actionData as Record<string, unknown>}
              isTracked={
                (msg.actionData as Record<string, unknown>).isTracked === true
              }
            />
          ) : (
            <ActionCard
              type={msg.actionType}
              data={msg.actionData as Record<string, unknown>}
              stats={stats}
            />
          ))}

        <Text fontSize="xs" color="gray.400" mt={1} px={1}>
          {timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </Text>
      </Flex>
    )
  }

  if (isLoading) {
    return (
      <Flex h="full" align="center" justify="center" bg="gray.50">
        <Spinner size="lg" color="blue.500" />
      </Flex>
    )
  }

  return (
    <Flex direction="column" h="full" bg="gray.50" position="relative">
      {/* Header with Day Selector */}
      <Box bg="white" borderBottom="1px" borderColor="gray.200" px={4} py={3}>
        <Flex justify="space-between" align="center">
          <Heading size="md">Chat</Heading>
          <DaySelector />
        </Flex>
      </Box>

      <ContextWidget
        mode={widgetMode}
        toggleMode={() =>
          setWidgetMode((m) => (m === "gym" ? "kitchen" : "gym"))
        }
        stats={stats}
        exerciseLogs={exerciseLogs}
        mealLogs={mealLogs}
        trainingRoutine={trainingRoutine}
        onQuickLog={(text) => handleSend(text)}
      />

      <Box flex={1} overflowY="auto" p={4} pb={20}>
        <VStack gap={3} align="stretch">
          {messages.length === 0 && (
            <Flex direction="column" align="center" justify="center" py={8}>
              <Text fontSize="4xl" mb={2}>
                🤖
              </Text>
              <Text color="gray.500" textAlign="center">
                Hi! I'm your fitness copilot.
                <br />
                Tell me what you ate or what exercise you did!
              </Text>
            </Flex>
          )}

          {messages.map(renderMessage)}

          {isSending && (
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
        bottom={0}
        left={0}
        right={0}
        bg="white"
        borderTop="1px"
        borderColor="gray.200"
        p={3}
        pb={4}
      >
        {isUploading && (
          <Flex mb={2} align="center" gap={2}>
            <Spinner size="xs" color="blue.500" />
            <Text fontSize="xs" color="gray.500">
              Uploading image...
            </Text>
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
            bg={isRecording ? "red.100" : undefined}
            onMouseDown={startRecording}
            onMouseUp={stopRecording}
            onMouseLeave={() => isRecording && stopRecording()}
            onTouchStart={startRecording}
            onTouchEnd={stopRecording}
          >
            <FiMic />
          </IconButton>

          <IconButton
            aria-label="Send"
            colorPalette="blue"
            borderRadius="full"
            disabled={!inputText || isSending || isUploading}
            onClick={() => handleSend()}
          >
            <FiSend />
          </IconButton>
        </Flex>
      </Box>
    </Flex>
  )
}
