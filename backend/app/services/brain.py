"""
Brain Service for Fitness Copilot.

The Brain interprets natural language and decides actions.
Uses a two-tier approach:
1. Tier 1 - Simple keyword matching: Fast, deterministic, works offline
2. Tier 2 - LLM extraction: For unknown foods or complex exercise descriptions
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.models import ChatActionType, ChatAttachmentType

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
    FOOD_DB: dict[str, FoodMacros] = {
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
    EXERCISE_MAP: dict[str, str] = {
        "bench": "Bench Press",
        "squat": "Barbell Squat",
        "deadlift": "Deadlift",
        "overhead press": "Overhead Press",
        "press": "Overhead Press",
        "row": "Barbell Row",
        "curl": "Bicep Curl",
        "pullup": "Pull-up",
        "pull-up": "Pull-up",
        "dip": "Dips",
        "leg press": "Leg Press",
        "legpress": "Leg Press",
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
        "dip",
        "leg press",
        "legpress",
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

    def _parse_food(self, content: str) -> BrainResponse | None:
        """
        Parse food from message content using simple keyword matching.

        Tier 1: Check known foods with simple `in` check
        Tier 2: Try LLM for unknown foods (if enabled) - not implemented yet

        Returns BrainResponse if food found, None otherwise.
        """
        lower = content.lower()

        # Tier 1: Check known foods with simple `in` check
        for food_name, macros in self.FOOD_DB.items():
            if food_name in lower:
                return BrainResponse(
                    content=f"✅ Logged {food_name}: {macros.calories} kcal, {macros.protein}g protein",
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

    def _parse_exercise(self, content: str) -> BrainResponse | None:
        """
        Parse exercise from message content using simple keyword matching.

        Tier 1: Find exercise name via keyword matching
        Tier 2: Extract sets/reps/weight (or use defaults)

        Returns BrainResponse if exercise found, None otherwise.
        """
        lower = content.lower()

        # Tier 1: Find exercise name
        exercise_name = None
        for keyword, name in self.EXERCISE_MAP.items():
            if keyword in lower:
                exercise_name = name
                break

        if not exercise_name:
            return None

        # Tier 2: Extract sets/reps/weight
        sets, reps, weight = self._extract_exercise_values(content)

        weight_str = f" @ {weight}kg" if weight > 0 else ""
        return BrainResponse(
            content=f"💪 Logged {exercise_name}: {sets}x{reps}{weight_str}",
            action_type=ChatActionType.LOG_EXERCISE,
            action_data={
                "exercise_name": exercise_name,
                "sets": sets,
                "reps": reps,
                "weight_kg": weight,
            },
        )

    def process_message(
        self,
        content: str,
        attachment_type: ChatAttachmentType = ChatAttachmentType.NONE,
    ) -> BrainResponse:
        """
        Process a chat message and return a response (sync version for text).

        This is the main entry point for the Brain service for text messages.
        For image attachments, use process_message_async instead.

        Args:
            content: The message content
            attachment_type: Type of attachment (image, audio, none)

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
            food_response = self._parse_food(content)
            if food_response:
                return food_response

        # Try exercise parsing if exercise keywords present
        if self._has_exercise_keywords(content):
            exercise_response = self._parse_exercise(content)
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
        """Handle image attachment with vision analysis."""
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
            cues_text = "\n".join(f"• {cue}" for cue in ga.form_cues)
            weight_str = (
                f" @ {ga.suggested_weight_kg}kg" if ga.suggested_weight_kg > 0 else ""
            )

            # Add goal-specific advice if available
            advice = (
                f"\n\n💡 {ga.goal_specific_advice}" if ga.goal_specific_advice else ""
            )
            plan_note = " (from today's plan)" if ga.in_todays_plan else ""

            return BrainResponse(
                content=f"🏋️ {ga.exercise_name}{plan_note}\n\n{cues_text}\n\n💪 Logged: {ga.suggested_sets}x{ga.suggested_reps}{weight_str}{advice}",
                action_type=ChatActionType.LOG_EXERCISE,
                action_data={
                    "exercise_name": ga.exercise_name,
                    "sets": ga.suggested_sets,
                    "reps": ga.suggested_reps,
                    "weight_kg": ga.suggested_weight_kg,
                    "form_cues": ga.form_cues,
                },
            )

        if result.category == ImageCategory.FOOD and result.food_analysis:
            fa = result.food_analysis

            # Add goal-specific advice and progress context
            advice = (
                f"\n\n💡 {fa.goal_specific_advice}" if fa.goal_specific_advice else ""
            )

            return BrainResponse(
                content=f"🍽️ {fa.meal_name}\n\n📊 {fa.calories} kcal | {fa.protein_g}g protein | {fa.carbs_g}g carbs | {fa.fat_g}g fat\n\n✅ Logged to today's meals!{advice}",
                action_type=ChatActionType.LOG_FOOD,
                action_data={
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
        """Return a general helpful response with suggestions."""
        return BrainResponse(
            content=(
                "I can help you log food and exercises! Try:\n"
                "• 'I ate a banana' - to log food\n"
                "• 'Did 3 sets of bench at 60kg' - to log exercise\n"
                "• 'reset' - to clear today's logs"
            ),
            action_type=ChatActionType.NONE,
        )
