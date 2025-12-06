# Implementation Plan

- [x] 1. Create useSpeechRecognition hook
  - [x] 1.1 Create `frontend/src/hooks/useSpeechRecognition.ts` with SpeechRecognition wrapper
    - Implement startRecording, stopRecording functions
    - Handle onresult, onerror, onend events
    - Check for browser support (window.SpeechRecognition || window.webkitSpeechRecognition)
    - Return isRecording, isSupported, error state
    - _Requirements: 1.1, 1.2, 1.4_
  - [x] 1.2 Write property test for recording state
    - **Property 1: Recording state reflects UI**
    - **Validates: Requirements 1.1, 1.5**
  - [x] 1.3 Write property test for unsupported browser handling
    - **Property 4: Unsupported browser shows error**
    - **Validates: Requirements 1.4**

- [x] 2. Integrate voice input into ChatInterface
  - [x] 2.1 Replace placeholder recording logic with useSpeechRecognition hook
    - Import and use the new hook
    - Wire onTranscript callback to sendMessage
    - Update mic button handlers (onClick instead of mouseDown/mouseUp)
    - _Requirements: 1.3, 2.1_
  - [x] 2.2 Update UI for recording state
    - Show pulsing animation on mic button when recording
    - Change input placeholder to "Listening..."
    - Add visual feedback (red background on mic button)
    - _Requirements: 1.5_
  - [x] 2.3 Handle errors and unsupported browsers
    - Show tooltip on mic button if unsupported
    - Display toast for errors (permission denied, no speech, etc.)
    - _Requirements: 1.4_
  - [x] 2.4 Write property test for voice-to-message flow
    - **Property 3: Voice input uses same message flow as text**
    - **Validates: Requirements 1.3, 2.1, 2.2, 2.3**

- [x] 3. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Add TypeScript declarations for Web Speech API
  - [x] 4.1 Create type declarations for SpeechRecognition
    - Add `frontend/src/types/speech-recognition.d.ts`
    - Declare SpeechRecognition, SpeechRecognitionEvent, SpeechRecognitionResult interfaces
    - _Requirements: 1.1_

- [x] 5. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

