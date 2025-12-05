import { describe, expect, it } from "vitest"
import { sendMessageToAI } from "./mockAiService"

describe("mockAiService", () => {
  it("returns food logging action for banana message", async () => {
    const result = await sendMessageToAI([], "I ate a banana")

    expect(result.action?.type).toBe("log_food")
    expect(result.action?.data?.name).toBe("Banana")
    expect(result.action?.data?.calories).toBe(105)
  })

  it("returns food logging action for protein shake", async () => {
    const result = await sendMessageToAI([], "I had a protein shake")

    expect(result.action?.type).toBe("log_food")
    expect(result.action?.data?.name).toBe("Protein Shake")
    expect(result.action?.data?.protein).toBe(24)
  })

  it("returns exercise logging action for leg press", async () => {
    const result = await sendMessageToAI(
      [],
      "I did 3 sets of leg press at 100kg",
    )

    expect(result.action?.type).toBe("log_exercise")
    expect(result.action?.data?.name).toBe("Leg Press")
    expect(result.action?.data?.sets).toBe(3)
    expect(result.action?.data?.weight).toBe(100)
  })

  it("returns exercise logging action for squat", async () => {
    const result = await sendMessageToAI([], "I did squats")

    expect(result.action?.type).toBe("log_exercise")
    expect(result.action?.data?.name).toBe("Barbell Squat")
  })

  it("returns vision response for image input", async () => {
    const result = await sendMessageToAI([], "Analyze this", "base64image")

    expect(result.text).toContain("Leg Press Machine")
    expect(result.action?.type).toBe("none")
  })

  it("returns default response for unknown input", async () => {
    const result = await sendMessageToAI([], "hello there")

    expect(result.text).toContain("fitness copilot")
    expect(result.action?.type).toBe("none")
  })

  it("parses reps from message", async () => {
    const result = await sendMessageToAI([], "I did 5 reps of deadlift")

    expect(result.action?.type).toBe("log_exercise")
    expect(result.action?.data?.reps).toBe(5)
  })

  it("returns coffee with low calories", async () => {
    const result = await sendMessageToAI([], "I drank coffee")

    expect(result.action?.type).toBe("log_food")
    expect(result.action?.data?.name).toBe("Coffee")
    expect(result.action?.data?.calories).toBe(5)
  })
})
