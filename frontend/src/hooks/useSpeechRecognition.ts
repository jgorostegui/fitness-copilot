import { useCallback, useEffect, useRef, useState } from "react"
import type {
  SpeechRecognition,
  SpeechRecognitionErrorEvent,
  SpeechRecognitionEvent,
} from "@/types/speech-recognition"

export interface UseSpeechRecognitionOptions {
  onTranscript: (text: string) => void
  onError?: (error: string) => void
  language?: string
}

export interface UseSpeechRecognitionReturn {
  isRecording: boolean
  isSupported: boolean
  startRecording: () => void
  stopRecording: () => void
  error: string | null
}

/**
 * Check if the Web Speech API is supported in the current browser
 */
export function isSpeechRecognitionSupported(): boolean {
  if (typeof window === "undefined") return false
  return !!(window.SpeechRecognition || window.webkitSpeechRecognition)
}

/**
 * Get the SpeechRecognition constructor for the current browser
 */
function getSpeechRecognition(): (new () => SpeechRecognition) | null {
  if (typeof window === "undefined") return null
  return window.SpeechRecognition || window.webkitSpeechRecognition || null
}

/**
 * Hook for speech-to-text functionality using the Web Speech API.
 *
 * Provides a simple interface for recording voice input and converting
 * it to text. The transcribed text is passed to the onTranscript callback.
 *
 * @example
 * ```tsx
 * const { isRecording, isSupported, startRecording, stopRecording } = useSpeechRecognition({
 *   onTranscript: (text) => sendMessage({ content: text }),
 *   onError: (error) => toast.error(error),
 * })
 * ```
 */
export function useSpeechRecognition(
  options: UseSpeechRecognitionOptions,
): UseSpeechRecognitionReturn {
  const { onTranscript, onError, language = "en-US" } = options

  const [isRecording, setIsRecording] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const recognitionRef = useRef<SpeechRecognition | null>(null)
  const transcriptRef = useRef<string>("")

  const isSupported = isSpeechRecognitionSupported()

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort()
        recognitionRef.current = null
      }
    }
  }, [])

  const startRecording = useCallback(() => {
    if (!isSupported) {
      const errorMsg = "Voice input is not supported in this browser"
      setError(errorMsg)
      onError?.(errorMsg)
      return
    }

    if (isRecording) return

    setError(null)
    transcriptRef.current = ""

    const SpeechRecognitionClass = getSpeechRecognition()
    if (!SpeechRecognitionClass) return

    const recognition = new SpeechRecognitionClass()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = language

    recognition.onstart = () => {
      setIsRecording(true)
    }

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let finalTranscript = ""

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        if (result.isFinal) {
          finalTranscript += result[0].transcript
        }
      }

      if (finalTranscript) {
        transcriptRef.current += finalTranscript
      }
    }

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      let errorMsg: string

      switch (event.error) {
        case "not-allowed":
          errorMsg = "Microphone access denied. Please allow microphone access."
          break
        case "no-speech":
          errorMsg = "No speech detected. Please try again."
          break
        case "network":
          errorMsg = "Network error. Please check your connection."
          break
        case "aborted":
          // User aborted, not an error
          return
        default:
          errorMsg = `Voice recognition error: ${event.error}`
      }

      setError(errorMsg)
      onError?.(errorMsg)
      setIsRecording(false)
    }

    recognition.onend = () => {
      setIsRecording(false)

      // Send transcript if we have one
      const transcript = transcriptRef.current.trim()
      if (transcript) {
        onTranscript(transcript)
        transcriptRef.current = ""
      }
    }

    recognitionRef.current = recognition

    try {
      recognition.start()
    } catch {
      const errorMsg = "Failed to start voice recognition"
      setError(errorMsg)
      onError?.(errorMsg)
    }
  }, [isSupported, isRecording, language, onTranscript, onError])

  const stopRecording = useCallback(() => {
    if (recognitionRef.current && isRecording) {
      recognitionRef.current.stop()
    }
  }, [isRecording])

  return {
    isRecording,
    isSupported,
    startRecording,
    stopRecording,
    error,
  }
}
