"""
Vision Service for Fitness Copilot.

Analyzes images using Google Gemini Vision to classify and extract
information from gym equipment and food photos.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.context import UserContext

logger = logging.getLogger(__name__)


class ImageCategory(str, Enum):
    """Categories for image classification."""

    GYM_EQUIPMENT = "gym_equipment"
    FOOD = "food"
    UNKNOWN = "unknown"


@dataclass
class GymEquipmentAnalysis:
    """Analysis result for gym equipment images."""

    exercise_name: str
    form_cues: list[str]
    suggested_sets: int
    suggested_reps: int
    suggested_weight_kg: float
    in_todays_plan: bool = False
    goal_specific_advice: str = ""


@dataclass
class FoodAnalysis:
    """Analysis result for food images."""

    meal_name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    goal_specific_advice: str = ""


@dataclass
class VisionResult:
    """Result from vision analysis."""

    category: ImageCategory
    gym_analysis: GymEquipmentAnalysis | None = None
    food_analysis: FoodAnalysis | None = None
    error_message: str | None = None


class VisionService:
    """Service for analyzing images using Google Gemini Vision."""

    def __init__(self) -> None:
        """Initialize the Vision service."""
        self._llm = None

    @property
    def llm(self):
        """Lazy load LLM provider."""
        if self._llm is None:
            from app.llm import get_llm_provider

            self._llm = get_llm_provider()
        return self._llm

    def _build_system_context(self, context: UserContext | None) -> str:
        """Build system context string for prompts."""
        if not context:
            return "No user context available."

        # Format scheduled exercises
        exercises_formatted = (
            "\n".join(
                f"- {e['name']}: {e['sets']}x{e['reps']} @ {e['target_weight']}kg"
                for e in context.scheduled_exercises
            )
            or "No exercises scheduled today."
        )

        # Format scheduled meals
        meals_formatted = (
            "\n".join(
                f"- {m['meal_type'].title()}: {m['item_name']} ({m['calories']} kcal)"
                for m in context.scheduled_meals
            )
            or "No meals scheduled today."
        )

        # Format chat history (last 5 messages)
        history_formatted = (
            "\n".join(
                f"{m['role'].upper()}: {m['content']}"
                for m in context.chat_history[-5:]
            )
            or "No recent messages."
        )

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

        return f"""USER PROFILE:
- Goal: {context.goal_method}
- Weight: {context.weight_kg}kg
- Height: {context.height_cm}cm
- Activity Level: {context.activity_level}
- Sex: {context.sex}

TODAY'S PROGRESS ({context.simulated_day_name}):
- Calories: {context.calories_consumed} / {context.calories_target} kcal ({cal_pct}%)
- Protein: {context.protein_consumed}g / {context.protein_target}g ({protein_pct}%)
- Workouts completed: {context.workouts_completed}

TODAY'S MEAL PLAN:
{meals_formatted}

TODAY'S TRAINING PLAN:
{exercises_formatted}

ALLOWED EXERCISES:
{', '.join(context.allowed_exercises) or 'Any exercise'}

RECENT CONVERSATION:
{history_formatted}"""

    async def analyze_image(
        self,
        image_url: str | None = None,
        image_base64: str | None = None,
        context: UserContext | None = None,
    ) -> VisionResult:
        """
        Analyze an image and return classification + analysis.

        Args:
            image_url: URL to the image (e.g., from demo-images/)
            image_base64: Base64-encoded image data
            context: User context for personalized prompts

        Returns:
            VisionResult with category and appropriate analysis
        """
        if not self.llm:
            return VisionResult(
                category=ImageCategory.UNKNOWN,
                error_message=(
                    "I can see you sent an image! For now, please describe "
                    "what you're showing me and I'll help log it."
                ),
            )

        try:
            # Step 1: Classify the image
            category = await self._classify_image(image_url, image_base64)

            # Step 2: Route to appropriate analyzer with context
            if category == ImageCategory.GYM_EQUIPMENT:
                gym_analysis = await self._analyze_gym_equipment(
                    image_url, image_base64, context
                )
                return VisionResult(category=category, gym_analysis=gym_analysis)

            if category == ImageCategory.FOOD:
                food_analysis = await self._analyze_food(
                    image_url, image_base64, context
                )
                return VisionResult(category=category, food_analysis=food_analysis)

            return VisionResult(
                category=ImageCategory.UNKNOWN,
                error_message=(
                    "I'm not sure what this image shows. Could you describe it? "
                    "I can help log food or exercises."
                ),
            )

        except Exception as e:
            logger.error("Vision analysis error: %s", e)
            return VisionResult(
                category=ImageCategory.UNKNOWN,
                error_message=(
                    "I had trouble analyzing that image. "
                    "Could you describe what you're showing me?"
                ),
            )

    async def _classify_image(
        self,
        image_url: str | None,
        image_base64: str | None,
    ) -> ImageCategory:
        """Classify image as gym_equipment, food, or unknown."""
        prompt = """Analyze this image and classify it into exactly one category:
- "gym_equipment": gym machines, weights, exercise equipment, dumbbells, barbells
- "food": meals, snacks, ingredients, drinks, plates of food
- "unknown": anything else

Respond with ONLY the category name, nothing else."""

        result = await self.llm.analyze_image(prompt, image_url, image_base64)

        if not result:
            return ImageCategory.UNKNOWN

        result_lower = result.lower().strip()

        if "gym" in result_lower or "equipment" in result_lower:
            return ImageCategory.GYM_EQUIPMENT
        if "food" in result_lower:
            return ImageCategory.FOOD
        return ImageCategory.UNKNOWN

    async def _analyze_gym_equipment(
        self,
        image_url: str | None,
        image_base64: str | None,
        context: UserContext | None = None,
    ) -> GymEquipmentAnalysis:
        """Analyze gym equipment image for exercise details."""
        system_context = self._build_system_context(context)

        prompt = f"""Analyze this gym equipment image.

{system_context}

TASK: Identify the exercise and provide guidance.

RULES:
1. If this exercise is in TODAY'S TRAINING PLAN, use those exact sets/reps/weight
2. If not in the plan, suggest reasonable defaults based on the user's goal
3. ONLY use exercise names from the ALLOWED EXERCISES list if provided
4. Provide form cues specific to the user's goal (strength vs hypertrophy)

Respond in JSON format ONLY (no markdown, no explanation):
{{"exercise_name": "Name of exercise", "form_cues": ["Tip 1", "Tip 2"], "suggested_sets": 3, "suggested_reps": 10, "suggested_weight_kg": 0, "in_todays_plan": false, "goal_specific_advice": "Brief advice"}}"""

        result = await self.llm.extract_json_from_image(prompt, image_url, image_base64)

        if result:
            data = result[0] if isinstance(result, list) else result
            return GymEquipmentAnalysis(
                exercise_name=data.get("exercise_name", "Unknown Exercise"),
                form_cues=data.get(
                    "form_cues", ["Maintain proper form", "Control the movement"]
                ),
                suggested_sets=data.get("suggested_sets", 3),
                suggested_reps=data.get("suggested_reps", 10),
                suggested_weight_kg=data.get("suggested_weight_kg", 0),
                in_todays_plan=data.get("in_todays_plan", False),
                goal_specific_advice=data.get("goal_specific_advice", ""),
            )

        # Fallback
        return GymEquipmentAnalysis(
            exercise_name="Unknown Exercise",
            form_cues=["Maintain proper form", "Control the movement"],
            suggested_sets=3,
            suggested_reps=10,
            suggested_weight_kg=0,
            in_todays_plan=False,
            goal_specific_advice="",
        )

    async def _analyze_food(
        self,
        image_url: str | None,
        image_base64: str | None,
        context: UserContext | None = None,
    ) -> FoodAnalysis:
        """Analyze food image for nutritional content."""
        system_context = self._build_system_context(context)

        prompt = f"""Analyze this food image.

{system_context}

TASK: Estimate the nutritional content of this meal.

RULES:
1. Consider the user's goal when giving advice:
   - CUTTING: Be conservative with estimates, warn about high-calorie items
   - BULKING: Celebrate protein and carbs, suggest additions if needed
   - MAINTENANCE: Provide balanced feedback
2. Reference today's progress in your advice
3. Be encouraging but honest

Respond in JSON format ONLY (no markdown, no explanation):
{{"meal_name": "Description", "calories": 500, "protein_g": 30, "carbs_g": 40, "fat_g": 20, "goal_specific_advice": "Brief advice based on goal and progress"}}"""

        result = await self.llm.extract_json_from_image(prompt, image_url, image_base64)

        if result:
            data = result[0] if isinstance(result, list) else result
            return FoodAnalysis(
                meal_name=data.get("meal_name", "Unknown Meal"),
                calories=data.get("calories", 300),
                protein_g=data.get("protein_g", 15),
                carbs_g=data.get("carbs_g", 30),
                fat_g=data.get("fat_g", 10),
                goal_specific_advice=data.get("goal_specific_advice", ""),
            )

        # Fallback
        return FoodAnalysis(
            meal_name="Unknown Meal",
            calories=300,
            protein_g=15,
            carbs_g=30,
            fat_g=10,
            goal_specific_advice="",
        )
