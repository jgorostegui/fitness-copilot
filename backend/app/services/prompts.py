"""
Prompt templates for the Fitness Copilot Brain service.

This module contains all LLM prompts used by the Brain service for:
- Exercise extraction from natural language
- Food extraction from natural language
- General fitness coaching responses

Prompts are designed to be clear, structured, and produce consistent JSON output.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.context import UserContext


@dataclass
class ExerciseExtractionContext:
    """Context for exercise extraction prompts."""

    user_message: str
    scheduled_exercises: list[str]
    is_rest_day: bool


def build_exercise_extraction_prompt(ctx: ExerciseExtractionContext) -> str:
    """
    Build a prompt for extracting exercise information from natural language.

    The prompt instructs the LLM to:
    1. Identify if the message is about logging an exercise
    2. Extract the exercise name, sets, reps, and weight
    3. Return structured JSON output

    Args:
        ctx: Context containing user message and today's scheduled exercises

    Returns:
        Formatted prompt string for the LLM
    """
    # Build the exercises context section
    if ctx.is_rest_day:
        exercises_section = "TODAY'S SCHEDULE: Rest day - no exercises scheduled."
    elif ctx.scheduled_exercises:
        exercises_list = ", ".join(ctx.scheduled_exercises)
        exercises_section = f"TODAY'S SCHEDULED EXERCISES: {exercises_list}"
    else:
        exercises_section = "TODAY'S SCHEDULE: No training plan available."

    return f"""You are an exercise logging assistant. Your task is to extract exercise information from the user's message.

{exercises_section}

USER MESSAGE: "{ctx.user_message}"

TASK: Analyze the message and extract exercise logging information.

RULES:
1. Only extract if the user is clearly reporting they DID an exercise (past tense: "did", "finished", "completed", "just did")
2. Match the exercise name to one from today's scheduled exercises when possible
3. Use proper exercise naming (e.g., "Incline Dumbbell Press", "Romanian Deadlift", "Barbell Row")
4. Extract sets, reps, and weight if mentioned
5. Convert pounds (lbs) to kilograms (kg) if weight is in lbs (multiply by 0.453592)

OUTPUT FORMAT: Return ONLY a valid JSON object with these fields:
- exercise_name: string or null (the exercise name, null if not an exercise log)
- sets: integer (default 1 if not mentioned)
- reps: integer (default 10 if not mentioned)
- weight_kg: number (default 0 if not mentioned)

EXAMPLES:
- "I did 3 sets of bench press at 80kg" → {{"exercise_name": "Bench Press", "sets": 3, "reps": 10, "weight_kg": 80}}
- "Just finished incline dumbbell press" → {{"exercise_name": "Incline Dumbbell Press", "sets": 1, "reps": 10, "weight_kg": 0}}
- "Did Romanian deadlifts 4x8 at 60kg" → {{"exercise_name": "Romanian Deadlift", "sets": 4, "reps": 8, "weight_kg": 60}}
- "What's for lunch?" → {{"exercise_name": null}}
- "How many calories in a banana?" → {{"exercise_name": null}}

JSON:"""


def build_system_prompt(context: UserContext) -> str:
    """
    Build the system prompt for general LLM responses.

    This prompt provides the LLM with full user context including:
    - User profile (goal, weight, height, activity level)
    - Today's progress (calories, protein, exercises)
    - Today's meal and training plans
    - Completed exercise logs

    Args:
        context: UserContext with all user data

    Returns:
        Formatted system prompt string
    """
    # Format scheduled meals
    if context.scheduled_meals:
        meals_list = [
            f"  - {m['meal_type']}: {m['item_name']} ({m['calories']} kcal, {m['protein_g']}g protein)"
            for m in context.scheduled_meals
        ]
        meals_str = "\n".join(meals_list)
    else:
        meals_str = "  No meal plan for today"

    # Format scheduled exercises with completion status
    if context.scheduled_exercises:
        exercises_list = []
        for e in context.scheduled_exercises:
            exercise_name = e["name"]
            target_sets = e["sets"]
            target_reps = e["reps"]
            target_weight = e["target_weight"]

            # Find completed sets for this exercise
            completed_sets = sum(
                c["sets"]
                for c in context.completed_exercises
                if c["name"].lower() == exercise_name.lower()
            )

            status = (
                f"({completed_sets}/{target_sets} sets done)"
                if completed_sets > 0
                else "(not started)"
            )
            exercises_list.append(
                f"  - {exercise_name}: {target_sets}x{target_reps} @ {target_weight}kg {status}"
            )
        exercises_str = "\n".join(exercises_list)
    else:
        exercises_str = "  Rest day - no exercises scheduled"

    # Format completed exercises (actual logs)
    if context.completed_exercises:
        completed_list = [
            f"  - {c['name']}: {c['sets']} sets x {c['reps']} reps @ {c['weight_kg']}kg"
            for c in context.completed_exercises
        ]
        completed_str = "\n".join(completed_list)
    else:
        completed_str = "  No exercises logged yet"

    # Calculate progress percentages
    cal_pct = (
        int((context.calories_consumed / context.calories_target) * 100)
        if context.calories_target > 0
        else 0
    )
    protein_pct = (
        int((context.protein_consumed / context.protein_target) * 100)
        if context.protein_target > 0
        else 0
    )

    return f"""You are a friendly, knowledgeable fitness coach assistant for the Fitness Copilot app.
You help users with nutrition, exercise, and fitness questions.

## User Profile
- Goal: {context.goal_method.replace('_', ' ').title()}
- Weight: {context.weight_kg}kg
- Height: {context.height_cm}cm
- Activity Level: {context.activity_level.replace('_', ' ').title()}
- Sex: {context.sex}

## Today's Progress ({context.simulated_day_name})
- Calories: {context.calories_consumed}/{context.calories_target} kcal ({cal_pct}%)
- Protein: {context.protein_consumed:.0f}/{context.protein_target:.0f}g ({protein_pct}%)
- Exercises completed: {context.workouts_completed}

## Today's Meal Plan
{meals_str}

## Today's Training Plan
{exercises_str}

## Completed Exercise Logs
{completed_str}

## Guidelines
- Be encouraging and supportive
- Give personalized advice based on the user's goal ({context.goal_method})
- Reference their current progress when relevant
- Keep responses concise but helpful (2-3 sentences max)
- If they mention food or exercise, suggest they log it with specific phrases like "I ate..." or "I did..."
- Don't make up information about their logs - only reference what's shown above
- DO NOT use markdown formatting (no **bold**, *italic*, or bullet points). Use plain text only.
- Use emojis sparingly for friendliness
"""


def build_fallback_system_prompt() -> str:
    """Build a minimal system prompt when no user context is available."""
    return """You are a friendly fitness coach assistant. Help the user with their fitness questions.
Keep responses concise and helpful."""
