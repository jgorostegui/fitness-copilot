# Requirements Document

## Introduction

This feature adds voice input support to Fitness Copilot, allowing users to log food and exercises by speaking instead of typing. The voice input integrates with the existing Chat interface and Brain service, providing the same functionality as text input but through speech.

## Glossary

- **Speech-to-Text (STT)**: Converting spoken audio input to text for processing
- **Brain Service**: The backend service that interprets natural language and decides actions (log food, log exercise, etc.)
- **Web Speech API**: Browser-native API for speech recognition (no external service required)
- **Chat Interface**: The conversational UI where users interact with the fitness assistant

## Requirements

### Requirement 1

**User Story:** As a user, I want to log food and exercises using voice input, so that I can track without typing.

#### Acceptance Criteria

1. WHEN the user taps the microphone button in chat THEN the system SHALL start recording audio and provide visual feedback
2. WHEN the user stops recording (tap again or auto-stop on silence) THEN the system SHALL transcribe the audio to text
3. WHEN transcription completes THEN the system SHALL process the text through the existing Brain service (same as typed input)
4. IF speech-to-text fails or is unsupported THEN the system SHALL display a friendly error message
5. WHILE audio is being recorded THEN the system SHALL display a recording indicator (pulsing icon, different color)

### Requirement 2

**User Story:** As a user, I want my voice input to work the same as text input, so that I get consistent behavior.

#### Acceptance Criteria

1. WHEN voice input is transcribed THEN the system SHALL send it to the same chat endpoint as typed messages
2. WHEN the Brain service processes voice-transcribed text THEN the system SHALL return the same response format as text input
3. WHEN voice input triggers a food or exercise log THEN the system SHALL display the same confirmation UI as text input

