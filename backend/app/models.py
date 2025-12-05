"""
Fitness Copilot data models.
"""

import uuid
from datetime import datetime
from enum import Enum

from pydantic import ConfigDict, EmailStr
from sqlalchemy import JSON, Column, LargeBinary
from sqlmodel import Field, Relationship, SQLModel


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class CamelModel(SQLModel):
    """Base model with camelCase serialization for frontend compatibility."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


# ============================================================================
# Enums
# ============================================================================


class GoalMethod(str, Enum):
    MAINTENANCE = "maintenance"
    VERY_SLOW_CUT = "very_slow_cut"
    SLOW_CUT = "slow_cut"
    STANDARD_CUT = "standard_cut"
    AGGRESSIVE_CUT = "aggressive_cut"
    VERY_AGGRESSIVE_CUT = "very_aggressive_cut"
    SLOW_GAIN = "slow_gain"
    MODERATE_GAIN = "moderate_gain"
    CUSTOM = "custom"


class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    SUPER_ACTIVE = "super_active"


class ChatMessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class ChatActionType(str, Enum):
    LOG_FOOD = "log_food"
    LOG_EXERCISE = "log_exercise"
    PROPOSE_FOOD = "propose_food"  # Preview before tracking (vision)
    PROPOSE_EXERCISE = "propose_exercise"  # Preview before tracking (vision)
    RESET = "reset"
    NONE = "none"


class ChatAttachmentType(str, Enum):
    IMAGE = "image"
    AUDIO = "audio"
    NONE = "none"


# ============================================================================
# Training Program
# ============================================================================


class TrainingProgramBase(SQLModel):
    name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    days_per_week: int = Field(ge=3, le=6)
    difficulty: str = Field(max_length=20)


class TrainingProgram(TrainingProgramBase, table=True):
    __tablename__ = "training_program"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    routines: list["TrainingRoutine"] = Relationship(
        back_populates="program", cascade_delete=True
    )


class TrainingProgramPublic(TrainingProgramBase):
    id: uuid.UUID


class TrainingProgramsPublic(SQLModel):
    data: list[TrainingProgramPublic]
    count: int


# ============================================================================
# Training Routine
# ============================================================================


class TrainingRoutineBase(SQLModel):
    day_of_week: int = Field(ge=0, le=6)
    exercise_name: str = Field(max_length=100)
    machine_hint: str | None = Field(default=None, max_length=200)
    sets: int = Field(gt=0)
    reps: int = Field(gt=0)
    target_load_kg: float = Field(ge=0)


class TrainingRoutine(TrainingRoutineBase, table=True):
    __tablename__ = "training_routine"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    program_id: uuid.UUID = Field(
        foreign_key="training_program.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    program: TrainingProgram | None = Relationship(back_populates="routines")


class TrainingRoutinePublic(TrainingRoutineBase):
    id: uuid.UUID
    program_id: uuid.UUID


class TrainingRoutinesPublic(SQLModel):
    data: list[TrainingRoutinePublic]
    count: int


# ============================================================================
# User
# ============================================================================


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    age: int | None = Field(default=None, ge=18, le=100)
    sex: str | None = Field(default=None, max_length=10)
    weight_kg: float | None = Field(default=None, ge=30, le=300)
    height_cm: int | None = Field(default=None, ge=100, le=250)
    body_fat_percentage: float | None = Field(default=None, ge=3, le=50)
    goal_method: GoalMethod | None = None
    goal_weight_kg: float | None = Field(default=None, ge=30, le=300)
    custom_kg_per_week: float | None = None
    custom_kcal_per_day: int | None = None
    activity_level: ActivityLevel | None = None
    selected_program_id: uuid.UUID | None = Field(
        default=None, foreign_key="training_program.id"
    )
    protein_g_per_kg: float = Field(default=2.0, ge=1.0, le=4.0)
    fat_rest_g_per_kg: float = Field(default=0.7, ge=0.5, le=1.5)
    fat_train_g_per_kg: float = Field(default=0.8, ge=0.5, le=1.5)
    tef_factor: float = Field(default=0.10, ge=0.05, le=0.15)
    onboarding_complete: bool = False
    simulated_day: int = Field(default=0, ge=0, le=6)  # 0=Monday, 6=Sunday


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class UserProfileUpdate(SQLModel):
    age: int | None = Field(default=None, ge=18, le=100)
    sex: str | None = Field(default=None, max_length=10)
    weight_kg: float | None = Field(default=None, ge=30, le=300)
    height_cm: int | None = Field(default=None, ge=100, le=250)
    body_fat_percentage: float | None = Field(default=None, ge=3, le=50)
    goal_method: GoalMethod | None = None
    goal_weight_kg: float | None = Field(default=None, ge=30, le=300)
    custom_kg_per_week: float | None = None
    custom_kcal_per_day: int | None = None
    activity_level: ActivityLevel | None = None
    protein_g_per_kg: float | None = Field(default=None, ge=1.0, le=4.0)
    fat_rest_g_per_kg: float | None = Field(default=None, ge=0.5, le=1.5)
    fat_train_g_per_kg: float | None = Field(default=None, ge=0.5, le=1.5)
    tef_factor: float | None = Field(default=None, ge=0.05, le=0.15)
    onboarding_complete: bool | None = None
    simulated_day: int | None = Field(default=None, ge=0, le=6)  # 0=Monday, 6=Sunday


class UserProfilePublic(CamelModel):
    """Public response model for user profile with camelCase serialization."""

    id: uuid.UUID
    email: EmailStr
    age: int | None = None
    sex: str | None = None
    weight_kg: float | None = None
    height_cm: int | None = None
    body_fat_percentage: float | None = None
    goal_method: GoalMethod | None = None
    goal_weight_kg: float | None = None
    activity_level: ActivityLevel | None = None
    selected_program_id: uuid.UUID | None = None
    protein_g_per_kg: float
    fat_rest_g_per_kg: float
    fat_train_g_per_kg: float
    onboarding_complete: bool
    simulated_day: int = 0  # 0=Monday, 6=Sunday


# ============================================================================
# Meal Plan
# ============================================================================


class MealPlanBase(SQLModel):
    day_of_week: int = Field(ge=0, le=6)
    meal_type: str = Field(max_length=20)
    item_name: str = Field(max_length=200)
    calories: int = Field(ge=0)
    protein_g: float = Field(ge=0)
    carbs_g: float = Field(ge=0)
    fat_g: float = Field(ge=0)


class MealPlan(MealPlanBase, table=True):
    __tablename__ = "meal_plan"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE", index=True
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MealPlanPublic(MealPlanBase):
    id: uuid.UUID


class MealPlansPublic(SQLModel):
    data: list[MealPlanPublic]
    count: int


# ============================================================================
# Meal Log
# ============================================================================


class MealLogBase(SQLModel):
    meal_name: str = Field(max_length=200)
    meal_type: str = Field(max_length=20)
    calories: int = Field(ge=0)
    protein_g: float = Field(ge=0)
    carbs_g: float = Field(ge=0)
    fat_g: float = Field(ge=0)


class MealLogCreate(MealLogBase):
    pass


class MealLog(MealLogBase, table=True):
    __tablename__ = "meal_log"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE", index=True
    )
    simulated_day: int = Field(default=0, ge=0, le=6, index=True)  # 0=Monday, 6=Sunday
    logged_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class MealLogPublic(MealLogBase, CamelModel):
    """Public response model for meal log with camelCase serialization."""

    id: uuid.UUID
    logged_at: datetime


class MealLogsPublic(CamelModel):
    """List response for meal logs with camelCase serialization."""

    data: list[MealLogPublic]
    count: int


# ============================================================================
# Exercise Log
# ============================================================================


class ExerciseLogBase(SQLModel):
    exercise_name: str = Field(max_length=100)
    sets: int = Field(ge=0)
    reps: int = Field(ge=0)
    weight_kg: float = Field(ge=0)


class ExerciseLogCreate(ExerciseLogBase):
    pass


class ExerciseLog(ExerciseLogBase, table=True):
    __tablename__ = "exercise_log"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE", index=True
    )
    simulated_day: int = Field(default=0, ge=0, le=6, index=True)  # 0=Monday, 6=Sunday
    logged_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class ExerciseLogPublic(ExerciseLogBase, CamelModel):
    """Public response model for exercise log with camelCase serialization."""

    id: uuid.UUID
    logged_at: datetime


class ExerciseLogsPublic(CamelModel):
    """List response for exercise logs with camelCase serialization."""

    data: list[ExerciseLogPublic]
    count: int


# ============================================================================
# Response Models
# ============================================================================


class DailyLogsResponse(CamelModel):
    """Combined response for today's logs with camelCase serialization."""

    meal_logs: list[MealLogPublic]
    exercise_logs: list[ExerciseLogPublic]


class DailySummary(CamelModel):
    """Daily progress summary with camelCase serialization."""

    calories_consumed: int
    calories_target: int
    protein_consumed: float
    protein_target: float
    workouts_completed: int
    calories_remaining: int
    protein_remaining: float


class SimulatedDayResponse(CamelModel):
    """Response model for simulated day with camelCase serialization."""

    simulated_day: int  # 0-6 (Monday-Sunday)
    day_name: str  # "Monday", "Tuesday", etc.


class SimulatedDayUpdate(SQLModel):
    """Request model for updating simulated day."""

    simulated_day: int = Field(ge=0, le=6)  # 0=Monday, 6=Sunday


class BodyMetrics(CamelModel):
    """Calculated body composition metrics with camelCase serialization."""

    weight_kg: float
    height_cm: int
    bmi: float
    bmi_status: str
    ffm_kg: float | None = None
    fat_mass_kg: float | None = None


class EnergyMetrics(CamelModel):
    """Calculated energy expenditure metrics with camelCase serialization."""

    bmr: int
    bmr_equation: str
    activity_multiplier: float
    neat: int
    base_tdee: int
    daily_deficit: int
    estimated_daily_calories: int


class EnergyAvailability(CamelModel):
    """Energy Availability metrics with camelCase serialization."""

    ea_kcal_per_kg_ffm: float | None = None
    ea_status: str


class WeeklySummary(CamelModel):
    """Weekly projection metrics with camelCase serialization."""

    weekly_deficit_kcal: int
    expected_loss_kg_per_week: float
    monthly_loss_kg: float
    total_to_goal_kg: float | None = None


class ProfileMetrics(CamelModel):
    """Combined profile metrics response with camelCase serialization."""

    body_metrics: BodyMetrics
    energy_metrics: EnergyMetrics
    energy_availability: EnergyAvailability
    weekly_summary: WeeklySummary


# ============================================================================
# Generic
# ============================================================================


class Message(SQLModel):
    message: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# ============================================================================
# Chat Message
# ============================================================================


class ChatMessageBase(SQLModel):
    content: str = Field(max_length=2000)
    attachment_type: ChatAttachmentType = Field(default=ChatAttachmentType.NONE)
    attachment_url: str | None = Field(default=None, max_length=500)


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a chat message."""

    pass


class ChatMessage(SQLModel, table=True):
    """Chat message model for storing conversation history."""

    __tablename__ = "chat_message"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE", index=True
    )
    role: ChatMessageRole
    content: str = Field(max_length=2000)
    action_type: ChatActionType = Field(default=ChatActionType.NONE)
    action_data: dict | None = Field(default=None, sa_type=JSON)
    attachment_type: ChatAttachmentType = Field(default=ChatAttachmentType.NONE)
    attachment_url: str | None = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class ChatMessagePublic(CamelModel):
    """Public response model for chat message with camelCase serialization."""

    id: uuid.UUID
    role: ChatMessageRole
    content: str
    action_type: ChatActionType
    action_data: dict | None = None
    attachment_type: ChatAttachmentType
    attachment_url: str | None = None
    created_at: datetime


class ChatMessagesPublic(CamelModel):
    """List response for chat messages with camelCase serialization."""

    data: list[ChatMessagePublic]
    count: int


# ============================================================================
# Chat Attachment
# ============================================================================


class ChatAttachment(SQLModel, table=True):
    """Stores uploaded images for chat messages."""

    __tablename__ = "chat_attachment"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE", index=True
    )
    content_type: str = Field(max_length=50)  # e.g., "image/jpeg"
    data: bytes = Field(sa_column=Column(LargeBinary))  # Store raw image bytes
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ImageUploadRequest(SQLModel):
    """Request model for image upload."""

    image_base64: str  # Base64-encoded image data
    content_type: str = "image/jpeg"


class ImageUploadResponse(CamelModel):
    """Response model for image upload."""

    attachment_id: str
