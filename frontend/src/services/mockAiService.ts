import type { Message } from "@/types/fitness"

export const sendMessageToAI = async (
  _history: Message[],
  newMessage: string,
  image?: string,
): Promise<{ text: string; action?: { type: string; data?: Record<string, unknown> } }> => {
  await new Promise((resolve) => setTimeout(resolve, 1200))

  const lowerMsg = newMessage.toLowerCase()

  if (image) {
    return {
      text: "Visual analysis complete.\n\nIdentified: **Leg Press Machine**.\n\n**Protocol:**\n1. Adjust seat so knees are at 90°.\n2. Place feet shoulder-width apart.\n3. Do not lock knees at the top.\n\nThis matches your 'Leg Day' routine.",
      action: { type: "none" },
    }
  }

  if (
    lowerMsg.includes("ate") ||
    lowerMsg.includes("food") ||
    lowerMsg.includes("meal") ||
    lowerMsg.includes("banana") ||
    lowerMsg.includes("yogurt") ||
    lowerMsg.includes("chicken") ||
    lowerMsg.includes("shake") ||
    lowerMsg.includes("coffee") ||
    lowerMsg.includes("eggs") ||
    lowerMsg.includes("rice") ||
    lowerMsg.includes("apple")
  ) {
    const foodMap: Record<string, { name: string; calories: number; protein: number }> = {
      banana: { name: "Banana", calories: 105, protein: 1 },
      shake: { name: "Protein Shake", calories: 130, protein: 24 },
      coffee: { name: "Coffee", calories: 5, protein: 0 },
      eggs: { name: "Eggs", calories: 140, protein: 12 },
      rice: { name: "Rice", calories: 200, protein: 4 },
      chicken: { name: "Chicken Breast", calories: 165, protein: 31 },
      apple: { name: "Apple", calories: 95, protein: 0 },
      yogurt: { name: "Greek Yogurt", calories: 100, protein: 17 },
    }

    let matched = { name: "Food Item", calories: 200, protein: 10 }
    for (const [key, value] of Object.entries(foodMap)) {
      if (lowerMsg.includes(key)) {
        matched = value
        break
      }
    }

    return {
      text: `Logged: **${matched.name}**\n\n${matched.calories} kcal • ${matched.protein}g protein`,
      action: {
        type: "log_food",
        data: matched,
      },
    }
  }

  if (
    lowerMsg.includes("set") ||
    lowerMsg.includes("rep") ||
    lowerMsg.includes("gym") ||
    lowerMsg.includes("lift") ||
    lowerMsg.includes("press") ||
    lowerMsg.includes("squat") ||
    lowerMsg.includes("deadlift")
  ) {
    const exerciseMap: Record<string, string> = {
      press: "Leg Press",
      squat: "Barbell Squat",
      deadlift: "Romanian Deadlift",
    }

    let exerciseName = "Exercise"
    for (const [key, value] of Object.entries(exerciseMap)) {
      if (lowerMsg.includes(key)) {
        exerciseName = value
        break
      }
    }

    const setsMatch = lowerMsg.match(/(\d+)\s*set/)
    const repsMatch = lowerMsg.match(/(\d+)\s*rep/)
    const weightMatch = lowerMsg.match(/(\d+)\s*kg/)

    return {
      text: `Logged: **${exerciseName}**\n\nGood volume. Ensure 2-3 min rest before next set.`,
      action: {
        type: "log_exercise",
        data: {
          name: exerciseName,
          sets: setsMatch ? Number.parseInt(setsMatch[1]) : 3,
          reps: repsMatch ? Number.parseInt(repsMatch[1]) : 10,
          weight: weightMatch ? Number.parseInt(weightMatch[1]) : 0,
        },
      },
    }
  }

  return {
    text: "I'm your fitness copilot.\n\nTry:\n- \"I ate a banana\"\n- \"I did 3 sets of leg press at 100kg\"\n- Or upload a photo of gym equipment.",
    action: { type: "none" },
  }
}
