# Fitness Copilot Architecture

This document explains the architecture of the Fitness Copilot application: how the frontend, backend, domain model, and AI services fit together into a coherent system.

---

## High‑Level Architecture

At a high level, Fitness Copilot is organized into four logical areas:

- **Clients** – mobile‑first web app used by end users, plus potential future external clients.
- **API layer** – a thin HTTP layer that exposes versioned REST endpoints.
- **Application / service layer** – orchestrates use cases such as onboarding, logging, summaries, chat handling, and vision flows.
- **Domain & data layer** – the fitness and nutrition model (users, plans, logs, chat history) stored in a relational database.
- **AI services layer** – Gemini LLM/vision capabilities used by chat and vision services.

### Mermaid diagram

```mermaid
flowchart TB
  subgraph Clients["Clients"]
    WebApp["Mobile Web App (React)"]
    ExtClients["Future External Clients"]
  end

  subgraph API["HTTP API Layer"]
    Auth["Auth & Profile Endpoints"]
    Plans["Plans & Programs Endpoints"]
    Logs["Logs & Summary Endpoints"]
    Chat["Chat & Upload Endpoints"]
  end

  subgraph AppLayer["Application / Service Layer"]
    MonitorSvc["Monitor & Summary Service"]
    ChatBrain["Chat Brain Service"]
    VisionOrch["Vision Orchestrator"]
    DemoSvc["Demo Persona / Onboarding Service"]
  end

  subgraph Domain["Domain & Data Layer"]
    Model["Fitness Domain Model (Users, Plans, Logs, Chat)"]
    DB[("Relational Database")]
  end

  subgraph AI["AI Services"]
    Gemini["Gemini LLM + Vision"]
  end

  Clients --> API
  API --> AppLayer
  AppLayer --> Domain
  Domain --> DB

  ChatBrain --> Gemini
  VisionOrch --> Gemini
```

The rest of this document explains each area and how data flows through the system.

---

## Clients

### Mobile Web App

The primary client is a mobile‑first single‑page application that exposes:

- **Monitor view** – daily progress gauges, meal logs, and exercise logs.
- **Workout view** – current training routine and adherence.
- **Nutrition view** – meal plans, logged meals, and remaining targets.
- **Chat view** – conversation with the fitness assistant, including image attachments.
- **Profile view** – basic profile information, theme, and reset/logout actions.

This client:

- communicates exclusively over HTTPS with JSON payloads,
- stores a short‑lived access token for authenticated requests,
- reacts to backend state changes (e.g., logs created via chat) by refetching or invalidating cached queries.

### External Clients (future‑facing)

The architecture allows for additional clients in the future (native apps, partner integrations, command‑line tools) by:

- keeping the API layer stateless and documented by OpenAPI,
- separating presentation concerns from domain and persistence concerns,
- treating the current web app as “just another client” of the HTTP API.

---

## Application / Service Layer

The application layer contains the core services that implement Fitness Copilot’s use cases.

### Monitor & Summary Service

Responsibilities:

- Load training programs, routines, and meal plans for the current (or simulated) day.
- Load today’s meal and exercise logs.
- Compute daily metrics:
  - calories consumed and remaining,
  - protein consumed and remaining,
  - number of workouts completed.
- Provide this data to:
  - the Monitor view,
  - the chat assistant (for contextual responses),
  - vision flows (for goal‑aware advice).

This service treats the domain model as the single source of truth and never talks to AI services directly.

### Chat Brain Service

The Brain is responsible for interpreting chat messages and proposing structured actions. It:

- receives:
  - free‑form text,
  - optional attachment metadata,
  - user and context identifiers.
- applies a two‑tier approach:
  - **Tier 1** – deterministic parsing:
    - food keyword detection and simple macros lookup,
    - exercise keyword detection and pattern extraction for sets/reps/weight,
    - reset command handling.
  - **Tier 2** – AI‑assisted flows:
    - presently focused on vision; text flows can be expanded later.
- returns:
  - assistant message text,
  - an action type (log food, log exercise, reset, or none),
  - structured action data used to create logs.

Crucially, the Brain **does not write to the database**. It suggests actions that the application layer applies under validation, guaranteeing that all changes to the Monitor backbone follow the same rules regardless of whether they came from chat or manual inputs.

### Vision Orchestrator

The vision orchestration component:

- accepts image identifiers and user identifiers from the API layer,
- builds a **user context** including:
  - profile (goal, weight, height, activity),
  - actual daily progress (logs),
  - today’s plan (scheduled meals and exercises),
  - allowed exercises and relevant chat history,
- calls the AI services layer to:
  - classify images as gym equipment or food,
  - produce structured analyses for gym machines or food plates,
- converts these analyses into proposed logging actions and rich assistant messages.

Examples:

- A gym machine photo becomes:
  - an identified exercise name from the allowed set,
  - plan‑aligned sets/reps/weight (when available),
  - form cues and goal‑specific guidance,
  - a “log exercise” action.

- A meal photo becomes:
  - an estimated meal description,
  - estimated macros,
  - goal‑specific feedback,
  - a “log food” action.

### Demo Persona / Onboarding Service

This service supports a smooth demo experience:

- Creates or reuses preconfigured personas for common goals (cut, bulk, maintain).
- Seeds:
  - baseline profile attributes (weight, height, activity level, goal),
  - a training program and routines,
  - weekly meal plans.
- Drives the onboarding flow:
  - pre‑fills an onboarding form with persona data,
  - persists updates when the user confirms,
  - toggles the onboarding flag so the main app is shown thereafter.

---

## Domain & Data Layer

The domain layer models the core fitness and nutrition concepts; the data layer persists them in a relational database. Together, they provide the “Monitor backbone.”

Key aggregates and entities include:

- **User and profile**
  - identity and authentication details,
  - physical attributes (sex, age, height, weight, body fat),
  - goal method (various cut/gain settings or maintenance),
  - activity level,
  - selected training program,
  - protein and fat per‑kg settings,
  - onboarding completion flag and simulated day.

- **Training programs and routines**
  - programs define an overall structure (name, description, days per week, difficulty),
  - routines define exercises per day (exercise name, machine hints, sets, reps, target load),
  - designed to be loaded from CSV so they remain easy to inspect and modify.

- **Meal plans**
  - weekly plans mapped to days of week,
  - each entry includes meal type (breakfast, lunch, dinner, snack), item name, calories, and macros.

- **Meal and exercise logs**
  - meal logs capture what was actually eaten (name, type, macros, simulated day, timestamp),
  - exercise logs capture what was actually performed (exercise, sets, reps, weight, simulated day, timestamp).

- **Chat messages and attachments**
  - chat messages store conversational history, actions, and attachment metadata,
  - attachments store binary image data linked back to users and messages.

- **Derived metrics and summaries**
  - derived structure for body metrics (BMI, lean mass estimates),
  - energy metrics (BMR, TDEE, daily deficits, calorie targets),
  - energy availability and weekly projections,
  - responses for daily summaries and combined “logs + summary” views.

The data layer enforces:

- non‑negative constraints on calorie and macro values,
- sensible ranges for weight, height, and body fat,
- referential integrity between users, programs, routines, plans, logs, and chat history.

---

## AI Services Layer

The AI services layer wraps calls to Gemini and keeps them at the edges of the system:

- **Configuration**
  - LLM usage can be toggled on or off via configuration,
  - the model name and API key are provided externally,
  - when disabled, deterministic fallbacks are used so the app remains functional.

- **LLM interface**
  - a provider abstraction accepts:
    - text prompts for future flows,
    - multimodal prompts for vision,
    - structured user context (profile, plan, progress).
  - returns:
    - structured analyses for gym equipment and food,
    - coaching text aligned with the user’s goal and current progress,
    - error or fallback messages when analysis is not possible.

The architecture ensures:

- AI does not directly mutate state,
- all mutations flow through explicit actions and the domain model,
- AI is an enhancement rather than a dependency for core functionality.

---

## End‑to‑End Flows

### Chat‑driven logging

1. The user sends a text message or a text + attachment message in the chat view.
2. The client posts the message (and attachment identifiers) to the chat endpoints.
3. The backend:
   - stores the user’s chat message,
   - calls the Brain service with the message and context,
   - receives assistant text plus a proposed action (log food, log exercise, reset, or none).
4. The application layer:
   - stores the assistant’s chat message,
   - applies the action:
     - creates meal or exercise logs with validated values, or
     - clears today’s logs on reset.
5. On the next Monitor refresh (or via cache invalidation), the new logs and metrics are visible in the dashboard.

### Vision‑driven logging

1. The user attaches a photo of a machine or meal in the chat.
2. The client uploads the image, gets an attachment identifier, and sends a chat message referring to that attachment.
3. The backend:
   - associates the attachment with the user and message,
   - builds a user context (profile, plan, progress, chat history),
   - calls the vision orchestrator, which delegates to Gemini.
4. The AI returns a structured analysis; the Brain turns it into:
   - a natural‑language explanation,
   - a log action with structured payload.
5. The application layer persists the assistant message and applies the action as logs, which the Monitor then reflects.

Across all these flows, the architecture preserves a clean separation:

- the client handles UX and interaction,
- the API layer validates and delegates,
- the application layer orchestrates behavior and interprets AI suggestions,
- the domain and data layer define and enforce truth,
- the AI services propose actions but never bypass the domain model,
- explicit contracts and clear layering keep changes aligned with the intended behavior. 
