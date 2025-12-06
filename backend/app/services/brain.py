"""
Brain Service for Fitness Copilot.

The Brain interprets natural language and decides actions.
Uses a two-tier approach:
1. Tier 1 - Simple keyword matching: Fast, deterministic, works offline
2. Tier 2 - LLM extraction: For unknown foods or complex exercise descriptions
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.models import ChatActionType, ChatAttachmentType
from app.services.prompts import (
    ExerciseExtractionContext,
    build_exercise_extraction_prompt,
    build_fallback_system_prompt,
    build_system_prompt,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from sqlmodel import Session

    from app.services.context import ContextBuilder, UserContext
    from app.services.vision import VisionService


@dataclass
class FoodMacros:
    """Nutritional information for a food item."""

    calories: int
    protein: float
    carbs: float
    fat: float


@dataclass
class BrainResponse:
    """Response from the Brain service."""

    content: str  # Assistant message text
    action_type: ChatActionType  # log_food, log_exercise, reset, none
    action_data: dict | None = None  # Structured data for the action


class BrainService:
    """
    Brain service for processing chat messages.

    Interprets natural language and routes to appropriate handlers.
    """

    # Food database with macros (simple keyword matching)
    # Includes both complete dishes and simple ingredients
    FOOD_DB: dict[str, FoodMacros] = {
        # Complete dishes (realistic quick add options)
        "grilled chicken salad": FoodMacros(calories=450, protein=42, carbs=18, fat=22),
        "chicken salad": FoodMacros(calories=450, protein=42, carbs=18, fat=22),
        "oatmeal with berries": FoodMacros(calories=320, protein=12, carbs=52, fat=8),
        "oatmeal": FoodMacros(calories=320, protein=12, carbs=52, fat=8),
        "eggs and avocado toast": FoodMacros(
            calories=480, protein=22, carbs=35, fat=28
        ),
        "avocado toast": FoodMacros(calories=480, protein=22, carbs=35, fat=28),
        "rice and grilled chicken": FoodMacros(
            calories=550, protein=45, carbs=55, fat=12
        ),
        "rice and chicken": FoodMacros(calories=550, protein=45, carbs=55, fat=12),
        "protein shake": FoodMacros(calories=200, protein=30, carbs=10, fat=4),
        "shake": FoodMacros(calories=200, protein=30, carbs=10, fat=4),
        # Simple ingredients (for text parsing)
        "banana": FoodMacros(calories=105, protein=1.3, carbs=27, fat=0.4),
        "chicken": FoodMacros(calories=165, protein=31, carbs=0, fat=3.6),
        "rice": FoodMacros(calories=206, protein=4.3, carbs=45, fat=0.4),
        "eggs": FoodMacros(calories=155, protein=13, carbs=1.1, fat=11),
        "oats": FoodMacros(calories=150, protein=5, carbs=27, fat=3),
        "salmon": FoodMacros(calories=208, protein=20, carbs=0, fat=13),
        "broccoli": FoodMacros(calories=55, protein=3.7, carbs=11, fat=0.6),
        "apple": FoodMacros(calories=95, protein=0.5, carbs=25, fat=0.3),
        "bread": FoodMacros(calories=79, protein=2.7, carbs=15, fat=1),
        "milk": FoodMacros(calories=149, protein=8, carbs=12, fat=8),
    }

    # Food keywords that trigger food parsing
    FOOD_KEYWORDS: set[str] = {
        "ate",
        "eaten",
        "had",
        "breakfast",
        "lunch",
        "dinner",
        "snack",
        "eating",
        "eat",
    }

    # Exercise mappings (keyword -> exercise name)
    # IMPORTANT: More specific keywords should be listed - sorting by length handles priority
    # Longer keywords are matched first, so "incline dumbbell press" matches before "press"
    EXERCISE_MAP: dict[str, str] = {
        # Bench variations
        "incline dumbbell press": "Incline Dumbbell Press",
        "incline bench press": "Incline Bench Press",
        "flat bench press": "Bench Press",
        "bench press": "Bench Press",
        "dumbbell press": "Dumbbell Press",
        "incline press": "Incline Dumbbell Press",
        "bench": "Bench Press",
        # Squats
        "barbell squat": "Barbell Squat",
        "squat": "Barbell Squat",
        # Deadlifts
        "romanian deadlift": "Romanian Deadlift",
        "rdl": "Romanian Deadlift",
        "deadlift": "Deadlift",
        # Press variations (order matters - longer first)
        "overhead press": "Overhead Press",
        "shoulder press": "Overhead Press",
        "military press": "Overhead Press",
        "leg press": "Leg Press",
        "legpress": "Leg Press",
        "press": "Overhead Press",  # Fallback for just "press"
        # Rows
        "barbell row": "Barbell Row",
        "row": "Barbell Row",
        # Other
        "bicep curl": "Bicep Curl",
        "curl": "Bicep Curl",
        "pullup": "Pull-up",
        "pull-up": "Pull-up",
        "pull up": "Pull-up",
        "lat pulldown": "Lat Pulldown",
        "pulldown": "Lat Pulldown",
        "dip": "Dips",
        "dips": "Dips",
        "lunge": "Lunges",
        "lunges": "Lunges",
        "calf raise": "Calf Raises",
        "calf": "Calf Raises",
    }

    # Exercise keywords that trigger exercise parsing
    EXERCISE_KEYWORDS: set[str] = {
        "bench",
        "squat",
        "deadlift",
        "press",
        "row",
        "curl",
        "sets",
        "reps",
        "kg",
        "lbs",
        "pullup",
        "pull-up",
        "pull up",
        "pulldown",
        "dip",
        "dips",
        "leg press",
        "legpress",
        "lunge",
        "lunges",
        "calf",
        "rdl",
        "romanian",
        "incline",
        "dumbbell",
        "barbell",
        "military",
        "shoulder",
        "overhead",
    }

    def __init__(self, session: Session | None = None) -> None:
        """Initialize the Brain service."""
        # LLM provider is loaded lazily when needed
        self._llm = None
        self._vision: VisionService | None = None
        self._context_builder: ContextBuilder | None = None
        self._session = session

    @property
    def llm(self):
        """Lazy load LLM provider."""
        if self._llm is None:
            from app.llm import get_llm_provider

            self._llm = get_llm_provider()
        return self._llm

    @property
    def vision(self) -> VisionService:
        """Lazy load Vision service."""
        if self._vision is None:
            from app.services.vision import VisionService

            self._vision = VisionService()
        return self._vision

    @property
    def context_builder(self) -> ContextBuilder:
        """Lazy load Context builder."""
        if self._context_builder is None:
            from app.services.context import ContextBuilder

            self._context_builder = ContextBuilder()
        return self._context_builder

    def _build_context(self, user_id: uuid.UUID) -> UserContext | None:
        """Build context for LLM prompts."""
        if not self._session:
            return None
        return self.context_builder.build_context(self._session, user_id)

    def _has_food_keywords(self, content: str) -> bool:
        """Check if content contains food-related keywords or known food names."""
        lower = content.lower()
        # Check for food keywords
        for keyword in self.FOOD_KEYWORDS:
            if keyword in lower:
                return True
        # Also check for known food names directly
        for food_name in self.FOOD_DB:
            if food_name in lower:
                return True
        return False

    def _parse_food(
        self, content: str, user_id: uuid.UUID | None = None
    ) -> BrainResponse | None:
        """
        Parse food from message content using simple keyword matching.

        Tier 1: Check known foods with simple `in` check (prioritize longer matches)
        Tier 2: Try LLM for unknown foods (if enabled) - not implemented yet

        Returns BrainResponse if food found, None otherwise.
        """
        lower = content.lower()

        # Tier 1: Check known foods, prioritizing longer matches (complete dishes)
        # Sort by length descending to match "grilled chicken salad" before "chicken"
        sorted_foods = sorted(self.FOOD_DB.keys(), key=len, reverse=True)

        for food_name in sorted_foods:
            if food_name in lower:
                macros = self.FOOD_DB[food_name]

                # Build progress feedback if context available
                progress_msg = self._build_food_progress_message(
                    user_id, macros.calories, macros.protein
                )

                return BrainResponse(
                    content=f"✅ Logged {food_name}: {macros.calories} kcal, {macros.protein}g protein{progress_msg}",
                    action_type=ChatActionType.LOG_FOOD,
                    action_data={
                        "food": food_name,
                        "meal_name": food_name.title(),
                        "meal_type": "snack",  # Default meal type
                        "calories": macros.calories,
                        "protein_g": macros.protein,
                        "carbs_g": macros.carbs,
                        "fat_g": macros.fat,
                    },
                )

        # Tier 2: LLM fallback would go here
        # For now, return None to fall through to general response
        return None

    def _build_food_progress_message(
        self,
        user_id: uuid.UUID | None,
        new_calories: int,
        new_protein: float,
    ) -> str:
        """Build progress feedback message for food logging."""
        if not user_id:
            return ""

        context = self._build_context(user_id)
        if not context:
            return ""

        # Calculate new totals (including the food being logged)
        new_cal_total = context.calories_consumed + new_calories

        # Calculate percentages
        cal_pct = (
            int((new_cal_total / context.calories_target) * 100)
            if context.calories_target > 0
            else 0
        )

        # Build encouraging message
        cal_remaining = context.calories_target - new_cal_total

        if cal_remaining > 0:
            return f"\n\n📊 You're at {cal_pct}% of your calorie target ({cal_remaining} kcal remaining)"
        else:
            return f"\n\n📊 You've reached {cal_pct}% of your calorie target"

    def _has_exercise_keywords(self, content: str) -> bool:
        """Check if content contains exercise-related keywords."""
        lower = content.lower()
        for keyword in self.EXERCISE_KEYWORDS:
            if keyword in lower:
                return True
        return False

    def _extract_exercise_values(self, content: str) -> tuple[int, int, float]:
        """
        Extract sets, reps, and weight from message content.

        Uses simple number extraction. Falls back to defaults if not found.

        Returns:
            Tuple of (sets, reps, weight_kg)
        """
        import re

        lower = content.lower()

        # Default values
        sets = 3
        reps = 10
        weight = 0.0

        # Try to extract sets (look for "X sets" or "Xx")
        sets_match = re.search(r"(\d+)\s*(?:sets?|x)", lower)
        if sets_match:
            sets = int(sets_match.group(1))

        # Try to extract reps (look for "X reps" or "xX")
        reps_match = re.search(r"(?:x|for)\s*(\d+)(?:\s*reps?)?", lower)
        if reps_match:
            reps = int(reps_match.group(1))
        else:
            # Alternative: "X reps"
            reps_match = re.search(r"(\d+)\s*reps?", lower)
            if reps_match:
                reps = int(reps_match.group(1))

        # Try to extract weight (look for "X kg" or "X lbs")
        weight_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:kg|kilos?)", lower)
        if weight_match:
            weight = float(weight_match.group(1))
        else:
            # Try lbs and convert to kg
            lbs_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lbs?|pounds?)", lower)
            if lbs_match:
                weight = float(lbs_match.group(1)) * 0.453592

        return sets, reps, weight

    def _parse_exercise(
        self, content: str, user_id: uuid.UUID | None = None
    ) -> BrainResponse | None:
        """
        Parse exercise from message content using simple keyword matching (sync fallback).

        This is only used for sync processing. For async, we use LLM extraction.

        Returns BrainResponse if exercise found, None otherwise.
        """
        lower = content.lower()

        logger.info(f"[BRAIN] Parsing exercise (sync) from: '{content}'")

        # Simple keyword matching as fallback for sync processing
        sorted_keywords = sorted(self.EXERCISE_MAP.keys(), key=len, reverse=True)

        exercise_name = None
        for keyword in sorted_keywords:
            if keyword in lower:
                exercise_name = self.EXERCISE_MAP[keyword]
                logger.info(
                    f"[BRAIN] Matched keyword '{keyword}' -> exercise '{exercise_name}'"
                )
                break

        if not exercise_name:
            logger.info(f"[BRAIN] No exercise keyword matched in: '{content}'")
            return None

        sets, reps, weight = self._extract_exercise_values(content)
        progress_msg = self._build_exercise_progress_message(user_id, exercise_name)

        weight_str = f" @ {weight}kg" if weight > 0 else ""
        return BrainResponse(
            content=f"💪 Logged {exercise_name}: {sets}x{reps}{weight_str}{progress_msg}",
            action_type=ChatActionType.LOG_EXERCISE,
            action_data={
                "exercise_name": exercise_name,
                "sets": sets,
                "reps": reps,
                "weight_kg": weight,
            },
        )

    async def _parse_exercise_with_llm(
        self, content: str, user_id: uuid.UUID | None = None
    ) -> BrainResponse | None:
        """
        Parse exercise from message content using LLM extraction.

        The LLM extracts the exact exercise name, sets, reps, and weight from
        natural language input. This is more accurate than keyword matching.

        Validates that the exercise is in today's scheduled plan before logging.

        Returns BrainResponse if exercise found, None otherwise.
        """
        logger.info(f"[BRAIN] Parsing exercise with LLM from: '{content}'")

        if not self.llm:
            logger.info("[BRAIN] No LLM available, falling back to keyword matching")
            return self._parse_exercise(content, user_id)

        # Build context for today's scheduled exercises
        context = self._build_context(user_id) if user_id else None
        scheduled_exercises = context.scheduled_exercises if context else []
        scheduled_names = [ex.get("name", "") for ex in scheduled_exercises]
        is_rest_day = len(scheduled_names) == 0

        # Build the extraction prompt using the prompts module
        prompt_ctx = ExerciseExtractionContext(
            user_message=content,
            scheduled_exercises=scheduled_names,
            is_rest_day=is_rest_day,
        )
        extraction_prompt = build_exercise_extraction_prompt(prompt_ctx)

        logger.debug(f"[BRAIN] LLM extraction prompt:\n{extraction_prompt}")

        try:
            response = await self.llm.generate(extraction_prompt, timeout_s=10.0)
            logger.info(f"[BRAIN] LLM extraction response: {response}")

            if not response:
                return self._parse_exercise(content, user_id)

            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r"\{[^}]+\}", response, re.DOTALL)
            if not json_match:
                logger.warning(f"[BRAIN] Could not extract JSON from: {response}")
                return self._parse_exercise(content, user_id)

            data = json.loads(json_match.group())
            exercise_name = data.get("exercise_name")

            if not exercise_name:
                logger.info("[BRAIN] LLM determined this is not an exercise log")
                return None

            sets = int(data.get("sets", 1))
            reps = int(data.get("reps", 10))
            weight = float(data.get("weight_kg", 0))

            logger.info(
                f"[BRAIN] LLM extracted: {exercise_name}, {sets}x{reps} @ {weight}kg"
            )

            # Check if exercise is in today's scheduled plan
            is_scheduled = any(
                name.lower() == exercise_name.lower() for name in scheduled_names
            )

            if not is_scheduled:
                # Exercise not in today's plan - don't log it
                logger.info(
                    f"[BRAIN] Exercise '{exercise_name}' not in today's plan: {scheduled_names}"
                )
                if scheduled_names:
                    return BrainResponse(
                        content=f"❌ {exercise_name} is not in today's workout plan.\n\nToday's exercises: {', '.join(scheduled_names)}",
                        action_type=ChatActionType.NONE,
                    )
                else:
                    return BrainResponse(
                        content="❌ Today is a rest day - no exercises scheduled!",
                        action_type=ChatActionType.NONE,
                    )

            progress_msg = self._build_exercise_progress_message(user_id, exercise_name)
            weight_str = f" @ {weight}kg" if weight > 0 else ""

            return BrainResponse(
                content=f"💪 Logged {exercise_name}: {sets}x{reps}{weight_str}{progress_msg}",
                action_type=ChatActionType.LOG_EXERCISE,
                action_data={
                    "exercise_name": exercise_name,
                    "sets": sets,
                    "reps": reps,
                    "weight_kg": weight,
                },
            )

        except Exception as e:
            logger.warning(f"[BRAIN] LLM exercise extraction failed: {e}")
            return self._parse_exercise(content, user_id)

    def _build_exercise_progress_message(
        self,
        user_id: uuid.UUID | None,
        exercise_name: str,
    ) -> str:
        """Build progress feedback message for exercise logging."""
        if not user_id:
            return ""

        context = self._build_context(user_id)
        if not context:
            return ""

        # Check if exercise is in today's training plan
        in_plan = any(
            ex.get("name", "").lower() == exercise_name.lower()
            for ex in context.scheduled_exercises
        )

        # Count completed exercises (including this one)
        total_scheduled = len(context.scheduled_exercises)
        completed = context.workouts_completed + 1  # +1 for current exercise

        if in_plan and total_scheduled > 0:
            remaining = total_scheduled - completed
            if remaining > 0:
                return f"\n\n🎯 Part of today's plan! {remaining} exercises remaining"
            else:
                return "\n\n🎯 Part of today's plan! Great job completing your workout!"
        elif context.scheduled_exercises:
            return f"\n\n💡 Extra work! Today's plan has {total_scheduled} scheduled exercises"
        else:
            return ""

    def process_message(
        self,
        content: str,
        attachment_type: ChatAttachmentType = ChatAttachmentType.NONE,
        user_id: uuid.UUID | None = None,
    ) -> BrainResponse:
        """
        Process a chat message and return a response (sync version for text).

        This is the main entry point for the Brain service for text messages.
        For image attachments, use process_message_async instead.

        Args:
            content: The message content
            attachment_type: Type of attachment (image, audio, none)
            user_id: Optional user ID for context-aware responses

        Returns:
            BrainResponse with content, action_type, and optional action_data
        """
        # Handle audio attachments (placeholder response)
        if attachment_type == ChatAttachmentType.AUDIO:
            return self._handle_audio_attachment()

        # For image attachments, return a message indicating async processing needed
        if attachment_type == ChatAttachmentType.IMAGE:
            return BrainResponse(
                content="Processing image... Please use the async endpoint.",
                action_type=ChatActionType.NONE,
            )

        # Check for reset command
        if "reset" in content.lower():
            return self._handle_reset()

        # Try food parsing if food keywords present
        if self._has_food_keywords(content):
            food_response = self._parse_food(content, user_id)
            if food_response:
                return food_response

        # Try exercise parsing if exercise keywords present
        if self._has_exercise_keywords(content):
            exercise_response = self._parse_exercise(content, user_id)
            if exercise_response:
                return exercise_response

        # Fall back to general response
        return self._general_response()

    def _handle_reset(self) -> BrainResponse:
        """Handle reset command - returns action_type=RESET for the route to process."""
        return BrainResponse(
            content="🔄 Reset complete! All of today's food and exercise logs have been cleared.",
            action_type=ChatActionType.RESET,
        )

    async def _handle_image_attachment(
        self,
        user_id: uuid.UUID | None = None,
        image_base64: str | None = None,
        image_url: str | None = None,
    ) -> BrainResponse:
        """
        Handle image attachment with vision analysis.

        Returns PROPOSE_* action types (not LOG_*) so user can preview before tracking.
        Form tips are stored in hidden_context for on-demand retrieval.
        """
        from app.services.vision import ImageCategory

        # Build context for the prompt
        context = None
        if user_id:
            context = self._build_context(user_id)

        # Analyze image with context
        result = await self.vision.analyze_image(
            image_url=image_url,
            image_base64=image_base64,
            context=context,
        )

        if result.error_message:
            return BrainResponse(
                content=result.error_message,
                action_type=ChatActionType.NONE,
            )

        if result.category == ImageCategory.GYM_EQUIPMENT and result.gym_analysis:
            ga = result.gym_analysis
            weight_str = (
                f" @ {ga.suggested_weight_kg}kg" if ga.suggested_weight_kg > 0 else ""
            )

            # Add goal-specific advice if available
            advice = (
                f"\n\n💡 {ga.goal_specific_advice}" if ga.goal_specific_advice else ""
            )
            plan_note = " (from today's plan)" if ga.in_todays_plan else ""

            # Note: Form tips are hidden initially, stored in hidden_context
            # User can click "Show Form Tips" to reveal them
            return BrainResponse(
                content=f"🏋️ {ga.exercise_name}{plan_note}\n\n💪 Suggested: {ga.suggested_sets}x{ga.suggested_reps}{weight_str}{advice}\n\nClick 'Add to Track' to log this exercise.",
                action_type=ChatActionType.PROPOSE_EXERCISE,
                action_data={
                    "isTracked": False,  # camelCase for frontend consistency
                    "exercise_name": ga.exercise_name,
                    "sets": ga.suggested_sets,
                    "reps": ga.suggested_reps,
                    "weight_kg": ga.suggested_weight_kg,
                    "hiddenContext": {  # camelCase for frontend consistency
                        "formCues": ga.form_cues,
                    },
                },
            )

        if result.category == ImageCategory.FOOD and result.food_analysis:
            fa = result.food_analysis

            # Add goal-specific advice and progress context
            advice = (
                f"\n\n💡 {fa.goal_specific_advice}" if fa.goal_specific_advice else ""
            )

            return BrainResponse(
                content=f"🍽️ {fa.meal_name}\n\n📊 {fa.calories} kcal | {fa.protein_g}g protein | {fa.carbs_g}g carbs | {fa.fat_g}g fat{advice}\n\nClick 'Add to Track' to log this meal.",
                action_type=ChatActionType.PROPOSE_FOOD,
                action_data={
                    "isTracked": False,  # camelCase for frontend consistency
                    "meal_name": fa.meal_name,
                    "meal_type": "snack",
                    "calories": fa.calories,
                    "protein_g": fa.protein_g,
                    "carbs_g": fa.carbs_g,
                    "fat_g": fa.fat_g,
                },
            )

        return BrainResponse(
            content=result.error_message
            or "I couldn't analyze this image. Please describe what you're showing me.",
            action_type=ChatActionType.NONE,
        )

    def _handle_audio_attachment(self) -> BrainResponse:
        """Handle audio attachment with hardcoded response."""
        return BrainResponse(
            content="I heard your voice note! For now, type what you said and I'll log it.",
            action_type=ChatActionType.NONE,
        )

    def _general_response(self) -> BrainResponse:
        """Return a general helpful response with suggestions (fallback when LLM unavailable)."""
        return BrainResponse(
            content=(
                "I can help you log food and exercises! Try:\n"
                "• 'I ate a banana' - to log food\n"
                "• 'Did 3 sets of bench at 60kg' - to log exercise\n"
                "• 'reset' - to clear today's logs"
            ),
            action_type=ChatActionType.NONE,
        )

    async def _llm_response(
        self, content: str, user_id: uuid.UUID | None = None
    ) -> BrainResponse:
        """Generate a response using the LLM with user context."""
        # Check if LLM is available
        if not self.llm:
            return self._general_response()

        # Build context
        context = None
        if user_id:
            context = self._build_context(user_id)

        # Build prompt using prompts module
        if context:
            system_prompt = build_system_prompt(context)
            full_prompt = f"{system_prompt}\n\nUser message: {content}\n\nAssistant:"
        else:
            full_prompt = (
                build_fallback_system_prompt()
                + f"\n\nUser message: {content}\n\nAssistant:"
            )

        # Log the full prompt for debugging
        logger.info(f"LLM request for user {user_id}: '{content[:100]}...'")
        logger.debug(f"Full LLM prompt:\n{full_prompt}")

        try:
            response = await self.llm.generate(full_prompt, timeout_s=15.0)
            logger.info(f"LLM response: '{response[:200] if response else 'None'}...'")
            if response:
                return BrainResponse(
                    content=response.strip(),
                    action_type=ChatActionType.NONE,
                )
        except Exception as e:
            logger.warning(f"LLM response failed: {e}")

        # Fall back to general response if LLM fails
        return self._general_response()

    async def process_message_async(
        self,
        content: str,
        attachment_type: ChatAttachmentType = ChatAttachmentType.NONE,
        user_id: uuid.UUID | None = None,
        image_base64: str | None = None,
        image_url: str | None = None,
    ) -> BrainResponse:
        """
        Process a chat message asynchronously (supports LLM and vision).

        This is the main entry point for the Brain service.

        Args:
            content: The message content
            attachment_type: Type of attachment (image, audio, none)
            user_id: Optional user ID for context-aware responses
            image_base64: Base64-encoded image data (for image attachments)
            image_url: URL to image (for image attachments)

        Returns:
            BrainResponse with content, action_type, and optional action_data
        """
        logger.info("=" * 60)
        logger.info(f"[BRAIN] Processing message: '{content}'")
        logger.info(f"[BRAIN] User ID: {user_id}")
        logger.info(f"[BRAIN] Attachment type: {attachment_type}")

        # Handle audio attachments (placeholder response)
        if attachment_type == ChatAttachmentType.AUDIO:
            return self._handle_audio_attachment()

        # Handle image attachments with vision
        if attachment_type == ChatAttachmentType.IMAGE:
            return await self._handle_image_attachment(
                user_id=user_id,
                image_base64=image_base64,
                image_url=image_url,
            )

        # Check for reset command
        if "reset" in content.lower():
            return self._handle_reset()

        # Try food parsing if food keywords present
        has_food = self._has_food_keywords(content)
        logger.info(f"[BRAIN] Has food keywords: {has_food}")
        if has_food:
            food_response = self._parse_food(content, user_id)
            if food_response:
                logger.info(
                    f"[BRAIN] Food parsed -> action={food_response.action_type}, data={food_response.action_data}"
                )
                return food_response

        # Try exercise parsing with LLM if exercise keywords present
        has_exercise = self._has_exercise_keywords(content)
        logger.info(f"[BRAIN] Has exercise keywords: {has_exercise}")
        if has_exercise:
            exercise_response = await self._parse_exercise_with_llm(content, user_id)
            if exercise_response:
                logger.info(
                    f"[BRAIN] Exercise parsed -> action={exercise_response.action_type}, data={exercise_response.action_data}"
                )
                return exercise_response

        # Use LLM for general conversation with context
        logger.info("[BRAIN] Falling back to LLM response")
        response = await self._llm_response(content, user_id)
        logger.info(
            f"[BRAIN] LLM response -> action={response.action_type}, content='{response.content[:100]}...'"
        )
        return response
