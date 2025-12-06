import { act, renderHook } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import {
  isSpeechRecognitionSupported,
  useSpeechRecognition,
} from "./useSpeechRecognition"

// Mock SpeechRecognition class
let mockRecognitionInstance: MockSpeechRecognition | null = null

class MockSpeechRecognition {
  continuous = false
  interimResults = false
  lang = "en-US"
  maxAlternatives = 1

  onstart: ((ev: Event) => void) | null = null
  onresult: ((ev: unknown) => void) | null = null
  onerror: ((ev: unknown) => void) | null = null
  onend: ((ev: Event) => void) | null = null

  constructor() {
    mockRecognitionInstance = this
  }

  start() {
    // Simulate async start
    setTimeout(() => this.onstart?.(new Event("start")), 0)
  }

  stop() {
    // Simulate async end
    setTimeout(() => this.onend?.(new Event("end")), 0)
  }

  abort() {}
}

describe("useSpeechRecognition", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRecognitionInstance = null

    // Setup global mock - use the class directly as constructor
    Object.defineProperty(window, "SpeechRecognition", {
      value: MockSpeechRecognition,
      writable: true,
      configurable: true,
    })
    Object.defineProperty(window, "webkitSpeechRecognition", {
      value: undefined,
      writable: true,
      configurable: true,
    })
  })

  describe("isSpeechRecognitionSupported", () => {
    it("returns true when SpeechRecognition is available", () => {
      expect(isSpeechRecognitionSupported()).toBe(true)
    })

    it("returns true when webkitSpeechRecognition is available", () => {
      Object.defineProperty(window, "SpeechRecognition", {
        value: undefined,
        writable: true,
        configurable: true,
      })
      Object.defineProperty(window, "webkitSpeechRecognition", {
        value: vi.fn(() => mockRecognition),
        writable: true,
        configurable: true,
      })
      expect(isSpeechRecognitionSupported()).toBe(true)
    })

    /**
     * **Feature: voice-input, Property 4: Unsupported browser shows error**
     * **Validates: Requirements 1.4**
     */
    it("returns false when neither API is available", () => {
      Object.defineProperty(window, "SpeechRecognition", {
        value: undefined,
        writable: true,
        configurable: true,
      })
      Object.defineProperty(window, "webkitSpeechRecognition", {
        value: undefined,
        writable: true,
        configurable: true,
      })
      expect(isSpeechRecognitionSupported()).toBe(false)
    })
  })

  describe("hook initialization", () => {
    it("starts with isRecording false", () => {
      const onTranscript = vi.fn()
      const { result } = renderHook(() =>
        useSpeechRecognition({ onTranscript }),
      )

      expect(result.current.isRecording).toBe(false)
      expect(result.current.error).toBeNull()
    })

    it("reports isSupported correctly", () => {
      const onTranscript = vi.fn()
      const { result } = renderHook(() =>
        useSpeechRecognition({ onTranscript }),
      )

      expect(result.current.isSupported).toBe(true)
    })
  })

  /**
   * **Feature: voice-input, Property 1: Recording state reflects UI**
   * **Validates: Requirements 1.1, 1.5**
   *
   * For any sequence of start/stop recording calls, the isRecording state
   * should accurately reflect whether recording is active.
   */
  describe("Property 1: Recording state reflects UI", () => {
    it("isRecording becomes true after startRecording", async () => {
      const onTranscript = vi.fn()
      const { result } = renderHook(() =>
        useSpeechRecognition({ onTranscript }),
      )

      act(() => {
        result.current.startRecording()
      })

      // Wait for async onstart callback
      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 10))
      })

      expect(result.current.isRecording).toBe(true)
    })

    it("isRecording becomes false after stopRecording", async () => {
      const onTranscript = vi.fn()
      const { result } = renderHook(() =>
        useSpeechRecognition({ onTranscript }),
      )

      // Start recording
      act(() => {
        result.current.startRecording()
      })
      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 10))
      })

      // Stop recording
      act(() => {
        result.current.stopRecording()
      })
      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 10))
      })

      expect(result.current.isRecording).toBe(false)
    })

    it("recording state is consistent across multiple start/stop cycles", async () => {
      const onTranscript = vi.fn()
      const { result } = renderHook(() =>
        useSpeechRecognition({ onTranscript }),
      )

      // Cycle 1: start -> stop
      act(() => {
        result.current.startRecording()
      })
      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 10))
      })
      expect(result.current.isRecording).toBe(true)

      act(() => {
        result.current.stopRecording()
      })
      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 10))
      })
      expect(result.current.isRecording).toBe(false)

      // Cycle 2: start -> stop again
      act(() => {
        result.current.startRecording()
      })
      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 10))
      })
      expect(result.current.isRecording).toBe(true)

      act(() => {
        result.current.stopRecording()
      })
      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 10))
      })
      expect(result.current.isRecording).toBe(false)
    })
  })

  /**
   * **Feature: voice-input, Property 4: Unsupported browser shows error**
   * **Validates: Requirements 1.4**
   */
  describe("Property 4: Unsupported browser handling", () => {
    it("sets error when trying to record on unsupported browser", () => {
      // Remove speech recognition support
      Object.defineProperty(window, "SpeechRecognition", {
        value: undefined,
        writable: true,
        configurable: true,
      })
      Object.defineProperty(window, "webkitSpeechRecognition", {
        value: undefined,
        writable: true,
        configurable: true,
      })

      const onTranscript = vi.fn()
      const onError = vi.fn()
      const { result } = renderHook(() =>
        useSpeechRecognition({ onTranscript, onError }),
      )

      act(() => {
        result.current.startRecording()
      })

      expect(result.current.isSupported).toBe(false)
      expect(result.current.error).toBe(
        "Voice input is not supported in this browser",
      )
      expect(onError).toHaveBeenCalledWith(
        "Voice input is not supported in this browser",
      )
      expect(result.current.isRecording).toBe(false)
    })
  })

  describe("transcript handling", () => {
    it("calls onTranscript with final transcript when recording stops", async () => {
      const onTranscript = vi.fn()
      const { result } = renderHook(() =>
        useSpeechRecognition({ onTranscript }),
      )

      // Start recording
      act(() => {
        result.current.startRecording()
      })
      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 10))
      })

      // Simulate speech result
      act(() => {
        mockRecognitionInstance?.onresult?.({
          resultIndex: 0,
          results: {
            length: 1,
            0: {
              isFinal: true,
              0: { transcript: "I ate a banana", confidence: 0.9 },
              length: 1,
            },
          },
        })
      })

      // Stop recording
      act(() => {
        result.current.stopRecording()
      })
      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 10))
      })

      expect(onTranscript).toHaveBeenCalledWith("I ate a banana")
    })
  })

  describe("error handling", () => {
    it("handles permission denied error", async () => {
      const onTranscript = vi.fn()
      const onError = vi.fn()
      const { result } = renderHook(() =>
        useSpeechRecognition({ onTranscript, onError }),
      )

      act(() => {
        result.current.startRecording()
      })
      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 10))
      })

      // Simulate error
      act(() => {
        mockRecognitionInstance?.onerror?.({
          error: "not-allowed",
          message: "",
        })
      })

      expect(onError).toHaveBeenCalledWith(
        "Microphone access denied. Please allow microphone access.",
      )
      expect(result.current.error).toBe(
        "Microphone access denied. Please allow microphone access.",
      )
    })

    it("handles no-speech error", async () => {
      const onTranscript = vi.fn()
      const onError = vi.fn()
      const { result } = renderHook(() =>
        useSpeechRecognition({ onTranscript, onError }),
      )

      act(() => {
        result.current.startRecording()
      })
      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 10))
      })

      act(() => {
        mockRecognitionInstance?.onerror?.({ error: "no-speech", message: "" })
      })

      expect(onError).toHaveBeenCalledWith(
        "No speech detected. Please try again.",
      )
    })
  })
})

/**
 * **Feature: voice-input, Property 3: Voice input uses same message flow as text**
 * **Validates: Requirements 1.3, 2.1, 2.2, 2.3**
 *
 * For any transcribed text from voice input, the system SHALL call the
 * onTranscript callback with the same text that would be sent via typed input.
 */
describe("Property 3: Voice input uses same message flow as text", () => {
  it("onTranscript receives the exact transcribed text", async () => {
    const onTranscript = vi.fn()
    const { result } = renderHook(() => useSpeechRecognition({ onTranscript }))

    // Start recording
    act(() => {
      result.current.startRecording()
    })
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 10))
    })

    // Simulate various transcripts
    const testTranscripts = [
      "I ate a banana",
      "Did 3 sets of bench press at 80kg",
      "How am I doing today?",
    ]

    for (const transcript of testTranscripts) {
      onTranscript.mockClear()

      // Simulate speech result
      act(() => {
        mockRecognitionInstance?.onresult?.({
          resultIndex: 0,
          results: {
            length: 1,
            0: {
              isFinal: true,
              0: { transcript, confidence: 0.9 },
              length: 1,
            },
          },
        })
      })

      // Trigger end to send transcript
      act(() => {
        mockRecognitionInstance?.onend?.(new Event("end"))
      })
      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 10))
      })

      // Verify exact transcript is passed
      expect(onTranscript).toHaveBeenCalledWith(transcript)

      // Restart for next iteration
      act(() => {
        result.current.startRecording()
      })
      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 10))
      })
    }
  })

  it("empty transcripts are not sent", async () => {
    const onTranscript = vi.fn()
    const { result } = renderHook(() => useSpeechRecognition({ onTranscript }))

    // Start recording
    act(() => {
      result.current.startRecording()
    })
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 10))
    })

    // Stop without any speech (no onresult called)
    act(() => {
      result.current.stopRecording()
    })
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 10))
    })

    // onTranscript should not be called for empty transcript
    expect(onTranscript).not.toHaveBeenCalled()
  })
})
