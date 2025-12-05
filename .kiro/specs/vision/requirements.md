# Requirements Document: Vision (Slices 4 & 6)

## Introduction

This feature enables the Fitness Copilot to process images sent via chat and intelligently classify them as either gym equipment or food, then take appropriate action. Using Google's Gemini multimodal capabilities, the system analyzes images to:

1. **Gym Equipment**: Identify the machine/exercise, provide form cues, and suggest logging based on the user's training plan
2. **Food/Meals**: Estimate nutritional content (calories, macros) and log the meal

The vision system integrates seamlessly with the existing BrainService, replacing the current hardcoded image responses with actual AI-powered analysis.

## Glossary

- **Vision_Service**: The backend service responsible for processing images using Google Gemini's multimodal API
- **Image_Classification**: The process of determining whether an image contains gym equipment or food
- **Gym_Machine_Analysis**: The process of identifying gym equipment and providing exercise guidance
- **Food_Analysis**: The process of estimating nutritional content from food images
- **Form_Cues**: Brief instructions on proper exercise technique
- **Macro_Estimation**: Calculation of protein, carbohydrates, and fat content from food images
- **Demo_Images**: Pre-configured sample images (leg-press.jpg, salad-chicken-breasts.jpg) for demonstration purposes
- **BrainService**: The existing service that routes chat messages to appropriate handlers

## Requirements

### Requirement 1: Image Classification

**User Story:** As a user, I want to send any fitness-related image and have the system automatically determine whether it's gym equipment or food, so that I get the appropriate response without specifying the image type.

#### Acceptance Criteria

1. WHEN a user sends an image attachment via chat THEN the Vision_Service SHALL classify the image as either "gym_equipment", "food", or "unknown"
2. WHEN the Vision_Service classifies an image as "gym_equipment" THEN the system SHALL route to the Gym_Machine_Analysis flow
3. WHEN the Vision_Service classifies an image as "food" THEN the system SHALL route to the Food_Analysis flow
4. WHEN the Vision_Service classifies an image as "unknown" THEN the system SHALL return a helpful message asking the user to describe what they're showing
5. WHEN the Vision_Service fails to process an image THEN the system SHALL return a graceful error message without crashing

### Requirement 2: Gym Machine Analysis

**User Story:** As a gym user, I want to photograph a machine and receive exercise instructions plus a logging suggestion based on my training plan, so that I can learn proper form and track my workout efficiently.

#### Acceptance Criteria

1. WHEN the Vision_Service analyzes a gym equipment image THEN the system SHALL identify the exercise name from the user's allowed exercises list
2. WHEN the Vision_Service identifies gym equipment THEN the system SHALL provide 2-3 form cues tailored to the user's goal (strength vs hypertrophy)
3. WHEN the identified exercise is in today's training plan THEN the system SHALL use the planned sets, reps, and weight values
4. WHEN the identified exercise is NOT in today's training plan THEN the system SHALL suggest reasonable defaults based on the user's goal
5. WHEN the Vision_Service returns gym equipment analysis THEN the BrainService SHALL return action_type=LOG_EXERCISE with the suggested values in action_data
6. WHEN a demo image (leg-press.jpg) is processed THEN the system SHALL return consistent, predictable results for demonstration purposes

### Requirement 3: Food Analysis

**User Story:** As a user tracking nutrition, I want to photograph my meal and have the system estimate its nutritional content with advice based on my goal, so that I can track my diet without manual data entry.

#### Acceptance Criteria

1. WHEN the Vision_Service analyzes a food image THEN the system SHALL estimate the meal name or description
2. WHEN the Vision_Service analyzes a food image THEN the system SHALL estimate calories (kcal)
3. WHEN the Vision_Service analyzes a food image THEN the system SHALL estimate protein, carbohydrates, and fat in grams
4. WHEN the user's goal is CUTTING THEN the system SHALL provide conservative estimates and warn about high-calorie items
5. WHEN the user's goal is BULKING THEN the system SHALL celebrate protein and carbs and suggest additions if needed
6. WHEN the Vision_Service returns food analysis THEN the BrainService SHALL return action_type=LOG_FOOD with the estimated values in action_data
7. WHEN a demo image (salad-chicken-breasts.jpg) is processed THEN the system SHALL return consistent, predictable results for demonstration purposes

### Requirement 4: Vision Service Integration with Context

**User Story:** As a developer, I want the vision processing to integrate cleanly with the existing BrainService architecture and inject relevant context, so that the AI provides personalized responses.

#### Acceptance Criteria

1. WHEN the BrainService receives an image attachment THEN the system SHALL call the Vision_Service instead of returning a hardcoded response
2. WHEN the Vision_Service is called THEN the system SHALL receive user context including profile, today's progress, training plan, and recent chat history
3. WHEN the Vision_Service processes an image THEN the system SHALL inject the context into the LLM prompt
4. WHEN the Vision_Service processes an image THEN the system SHALL accept both URL strings and base64-encoded image data
5. WHEN the LLM API is unavailable THEN the system SHALL fall back to a helpful error message without blocking the chat flow
6. WHEN processing images THEN the system SHALL complete within 30 seconds or return a timeout error

### Requirement 5: Frontend Image Flow

**User Story:** As a user, I want to attach any image in the chat interface and see the AI's analysis displayed as a rich response, so that I understand what was detected and logged.

#### Acceptance Criteria

1. WHEN a user clicks the camera button in the Oracle chat THEN the frontend SHALL open a file picker for image selection
2. WHEN a user selects an image THEN the frontend SHALL upload it via POST /upload/image and receive an attachment_id
3. WHEN sending a chat message with an image THEN the frontend SHALL include the attachment_id in the attachment_url field
4. WHEN the assistant responds with gym equipment analysis THEN the frontend SHALL display the exercise name, form cues, and suggested log values
5. WHEN the assistant responds with food analysis THEN the frontend SHALL display the meal name and estimated macros
6. WHEN the assistant response includes action_type=LOG_EXERCISE or LOG_FOOD THEN the frontend SHALL show an ActionCard indicating what was logged
7. WHEN the user sends an image THEN the frontend SHALL show a loading indicator until the response arrives

### Requirement 6: Demo Mode Support

**User Story:** As a presenter, I want reliable demo images that produce consistent results, so that I can demonstrate the vision feature predictably.

#### Acceptance Criteria

1. WHEN processing the demo image "leg-press.jpg" THEN the system SHALL return "Leg Press" as the exercise name with appropriate form cues
2. WHEN processing the demo image "salad-chicken-breasts.jpg" THEN the system SHALL return a chicken salad description with reasonable macro estimates
3. WHEN demo images are processed THEN the system SHALL use the same LLM flow as user-uploaded images (no special hardcoding)

### Requirement 7: LLM Toggle for Testing

**User Story:** As a developer or tester, I want to easily switch between LLM-enabled and LLM-disabled modes, so that I can test both the AI-powered flow and the fallback behavior.

#### Acceptance Criteria

1. WHEN the LLM_ENABLED environment variable is set to false THEN the Vision_Service SHALL return a fallback response asking the user to describe the image
2. WHEN the LLM_ENABLED environment variable is set to true THEN the Vision_Service SHALL process images using Google Gemini
3. WHEN testing without LLM THEN the system SHALL still accept image attachments and return valid ChatMessage responses
4. WHEN switching between LLM modes THEN the system SHALL require only an environment variable change (no code changes)

### Requirement 8: Frontend Testing Strategy

**User Story:** As a frontend developer, I want to test the image flow without depending on live LLM calls, so that tests are fast and deterministic.

#### Acceptance Criteria

1. WHEN running frontend unit tests THEN the tests SHALL mock API responses without hitting the backend
2. WHEN running frontend E2E tests in CI THEN the tests SHALL run against backend with LLM_ENABLED=false for deterministic results
3. WHEN running frontend E2E tests locally with LLM THEN the developer SHALL be able to set LLM_ENABLED=true to test real AI responses
4. WHEN the backend returns a vision response THEN the frontend SHALL render it identically regardless of whether it came from LLM or fallback
