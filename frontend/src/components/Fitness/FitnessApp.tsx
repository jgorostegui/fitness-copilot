import { Box } from "@chakra-ui/react"
import { useState } from "react"
import { useFitnessStore } from "@/hooks/useFitnessStore"
import { Onboarding } from "./Onboarding"
import { Dashboard } from "./Dashboard"
import { ChatInterface } from "./ChatInterface"
import { Profile } from "./Profile"
import { PlanViewer } from "./PlanViewer"
import { BottomNav } from "./BottomNav"

type Tab = "monitor" | "workout" | "chat" | "nutrition" | "profile"

export const FitnessApp = () => {
  const [activeTab, setActiveTab] = useState<Tab>("monitor")
  const {
    profile,
    setProfile,
    resetProfile,
    stats,
    mealLogs,
    exerciseLogs,
    addMealLog,
    addExerciseLog,
    chatHistory,
    setChatHistory,
    handleChatAction,
  } = useFitnessStore()

  if (!profile) {
    return <Onboarding onComplete={setProfile} />
  }

  const themeClass = profile.theme === "dark" ? "dark" : ""

  return (
    <Box
      h="100vh"
      w="full"
      bg={profile.theme === "dark" ? "gray.900" : "gray.50"}
      color={profile.theme === "dark" ? "white" : "gray.900"}
      position="relative"
      overflow="hidden"
      className={themeClass}
    >
      <Box h="full" pb={16}>
        {activeTab === "monitor" && (
          <Dashboard
            stats={stats}
            mealLogs={mealLogs}
            exerciseLogs={exerciseLogs}
            profile={profile}
          />
        )}
        {activeTab === "workout" && (
          <PlanViewer
            mode="workout"
            mealLogs={mealLogs}
            exerciseLogs={exerciseLogs}
            onAddMeal={addMealLog}
            onAddExercise={addExerciseLog}
          />
        )}
        {activeTab === "chat" && (
          <ChatInterface
            history={chatHistory}
            setHistory={setChatHistory}
            onAction={handleChatAction}
            stats={stats}
            profile={profile}
            mealLogs={mealLogs}
            exerciseLogs={exerciseLogs}
          />
        )}
        {activeTab === "nutrition" && (
          <PlanViewer
            mode="nutrition"
            mealLogs={mealLogs}
            exerciseLogs={exerciseLogs}
            onAddMeal={addMealLog}
            onAddExercise={addExerciseLog}
          />
        )}
        {activeTab === "profile" && (
          <Profile
            profile={profile}
            onUpdate={setProfile}
            onReset={resetProfile}
          />
        )}
      </Box>
      <BottomNav activeTab={activeTab} onTabChange={setActiveTab} />
    </Box>
  )
}
