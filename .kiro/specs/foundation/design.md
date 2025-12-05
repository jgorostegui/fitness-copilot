# Design Document: Foundation

## Overview

The Foundation feature provides the backend infrastructure for the Fitness Copilot application. It implements a multi-tenant REST API that manages user profiles, meal plans, training programs, and daily activity logs. The design integrates with an existing React frontend located in `.kiro/frontend-frankenstein-fitness-copilot/`.

The system follows a "strict backbone" philosophy where CSV-defined meal plans and training programs serve as the source of truth, while daily logs track actual user behavior. This separation enables AI features to suggest changes while maintaining data integrity.

## Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│  (Onboarding, Dashboard, ChatInterface, Profile, Plan)  │
└────────────────────┬────────────────────────────────────┘
                     │ REST API (JSON)
┌────────────────────▼────────────────────────────────────┐
│                  FastAPI Backend                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Profile    │  │    Plans     │  │     Logs     │  │
│  │   Routes     │  │   Routes     │  │    Routes    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                  │                  │          │
│  ┌──────▼──────────────────▼──────────────────▼───────┐ │
│  │              CRUD Operations Layer                  │ │
│  └──────┬──────────────────┬──────────────────┬───────┘ │
│         │                  │                  │          │
│  ┌──────▼──────────────────▼──────────────────▼───────┐ │
│  │            SQLModel ORM (Pydantic + SQL)            │ │
│  └──────┬──────────────────┬──────────────────┬───────┘ │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼─────────┐
│                   PostgreSQL Database                    │
│  Tables: users, training_programs, training_routines,   │
│          meal_plans, meal_logs, exercise_logs            │
└──────────────────────────────────────────────────────────┘
          ▲
          │ CSV Import on Startup
┌─────────┴─────────┐
│  CSV Data Files   │
│  - meal_plans.csv │
│  - routines.csv   │
└───────────────────┘
```

### Technology Stack

- **Framework**: FastAPI (async Python web framework)
- **ORM**: SQLModel (combines Pydantic and SQLAlchemy)
- **Database**: PostgreSQL
- **Validation**: Pydantic v2
- **Authentication**: JWT tokens (leveraging existing template auth)
- **Testing**: pytest with property-based testing using Hypothesis

## Components and Interfaces

### 1. Data Models

#### User Profile Model

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import Enum

class GoalMethod(str, Enum):
    MAINTENANCE = "maintenance"
    VERY_SLOW_CUT = "very_slow_cut"  # -0.2 kg/week
    SLOW_CUT = "slow_cut"  # -0.25 kg/week
    STANDARD_CUT = "standard_cut"  # -0.5 kg/week
    AGGRESSIVE_CUT = "aggressive_cut"  # -0.75 kg/week
    VERY_AGGRESSIVE_CUT = "very_aggressive_cut"  # -1.0 kg/week
    SLOW_GAIN = "slow_gain"  # +0.25 kg/week
    MODERATE_GAIN = "moderate_gain"  # +0.5 kg/week
    CUSTOM = "custom"

class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"  # 1.20 multiplier, < 5,000 steps
    LIGHTLY_ACTIVE = "lightly_active"  # 1.375, 5,000-7,500 steps
    MODERATELY_ACTIVE = "moderately_active"  # 1.55, 7,500-10,000 steps
    VERY_ACTIVE = "very_active"  # 1.725, 10,000-12,500 steps
    SUPER_ACTIVE = "super_active"  # 1.90, > 12,500 steps

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    
    # Basic profile
    age: int | None = Field(default=None, ge=18, le=100)
    sex: str | None = Field(default=None, max_length=10)  # "male" or "female"
    weight_kg: float | None = Field(default=None, ge=30, le=300)
    height_cm: int | None = Field(default=None, ge=100, le=250)
    
    # Body composition (optional)
    body_fat_percentage: float | None = Field(default=None, ge=3, le=50)
    
    # Goals
    goal_method: GoalMethod | None = None
    goal_weight_kg: float | None = Field(default=None, ge=30, le=300)
    custom_kg_per_week: float | None = None  # For custom goals
    custom_kcal_per_day: int | None = None  # Alternative to kg/week
    
    # Activity
    activity_level: ActivityLevel | None = None
    
    # Training program
    selected_program_id: int | None = Field(default=None, foreign_key="training_programs.id")
    
    # Macronutrient preferences
    protein_g_per_kg: float = Field(default=2.0, ge=1.0, le=4.0)
    fat_rest_g_per_kg: float = Field(default=0.7, ge=0.5, le=1.5)
    fat_train_g_per_kg: float = Field(default=0.8, ge=0.5, le=1.5)
    tef_factor: float = Field(default=0.10, ge=0.05, le=0.15)  # Thermic Effect of Food
    
    onboarding_complete: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

#### Training Program Model

```python
class TrainingProgram(SQLModel, table=True):
    __tablename__ = "training_programs"
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    days_per_week: int = Field(ge=3, le=6)
    difficulty: str = Field(max_length=20)  # "beginner", "intermediate", "advanced"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

#### Training Routine Model

```python
class TrainingRoutine(SQLModel, table=True):
    __tablename__ = "training_routines"
    
    id: int | None = Field(default=None, primary_key=True)
    program_id: int = Field(foreign_key="training_programs.id")
    day_of_week: int = Field(ge=0, le=6)  # 0=Monday, 6=Sunday
    exercise_name: str = Field(max_length=100)
    machine_hint: str | None = Field(default=None, max_length=200)
    sets: int = Field(gt=0)
    reps: int = Field(gt=0)
    target_load_kg: float = Field(ge=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

#### Meal Plan Model

```python
class MealPlan(SQLModel, table=True):
    __tablename__ = "meal_plans"
    
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    day_of_week: int = Field(ge=0, le=6)
    meal_type: str = Field(max_length=20)  # "breakfast", "lunch", "dinner", "snack"
    item_name: str = Field(max_length=200)
    calories: int = Field(ge=0)
    protein_g: float = Field(ge=0)
    carbs_g: float = Field(ge=0)
    fat_g: float = Field(ge=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

#### Exercise Log Model

```python
class ExerciseLog(SQLModel, table=True):
    __tablename__ = "exercise_logs"
    
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    exercise_name: str = Field(max_length=100)
    sets: int = Field(ge=0)
    reps: int = Field(ge=0)
    weight_kg: float = Field(ge=0)
    logged_at: datetime = Field(default_factory=datetime.utcnow, index=True)
```

#### Meal Log Model

```python
class MealLog(SQLModel, table=True):
    __tablename__ = "meal_logs"
    
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    meal_name: str = Field(max_length=200)
    meal_type: str = Field(max_length=20)
    calories: int = Field(ge=0)
    protein_g: float = Field(ge=0)
    carbs_g: float = Field(ge=0)
    fat_g: float = Field(ge=0)
    logged_at: datetime = Field(default_factory=datetime.utcnow, index=True)
```

#### Calculated Metrics (Response Models Only)

These are not stored in the database but calculated on-demand:

```python
class BodyMetrics(BaseModel):
    """Calculated body composition metrics"""
    weight_kg: float
    height_cm: int
    bmi: float
    bmi_status: str  # "underweight", "normal", "overweight", "obese"
    ffm_kg: float | None  # Fat-free mass (if body_fat_percentage available)
    fat_mass_kg: float | None  # Fat mass (if body_fat_percentage available)

class EnergyMetrics(BaseModel):
    """Calculated energy expenditure metrics"""
    bmr: int  # Basal Metabolic Rate
    bmr_equation: str  # "mifflin_st_jeor" or "katch_mcardle"
    activity_multiplier: float
    neat: int  # Non-Exercise Activity Thermogenesis
    base_tdee: int  # Total Daily Energy Expenditure (no exercise)
    daily_deficit: int  # Target deficit in kcal
    estimated_daily_calories: int  # Target intake
    
class EnergyAvailability(BaseModel):
    """Energy Availability metrics"""
    ea_kcal_per_kg_ffm: float | None
    ea_status: str  # "optimal", "functional", "low_ea", "need_bf"
    
class WeeklySummary(BaseModel):
    """Weekly projection metrics"""
    weekly_deficit_kcal: int
    expected_loss_kg_per_week: float
    monthly_loss_kg: float
    total_to_goal_kg: float | None
```

### 2. API Endpoints

#### Profile Endpoints

```python
# GET /api/v1/profile/me
# Response: UserProfilePublic
{
  "id": 1,
  "email": "user@example.com",
  "age": 36,
  "sex": "male",
  "weight": 92.5,
  "height": 186,
  "bodyFat": 17.5,
  "plan": "standard_cut",
  "goalWeight": 85,
  "activityLevel": "sedentary",
  "onboardingComplete": true,
  "selectedProgramId": 2,
  "proteinGPerKg": 2.5,
  "fatRestGPerKg": 0.7,
  "fatTrainGPerKg": 0.8
}

# PUT /api/v1/profile/me
# Request: UserProfileUpdate
{
  "age": 36,
  "sex": "male",
  "weight": 92.5,
  "height": 186,
  "bodyFat": 17.5,
  "goalMethod": "standard_cut",
  "goalWeight": 85,
  "activityLevel": "sedentary"
}
# Response: UserProfilePublic

# GET /api/v1/profile/me/metrics
# Response: ProfileMetrics (includes calculated values)
{
  "bodyMetrics": {
    "weightKg": 92.5,
    "heightCm": 186,
    "bmi": 26.7,
    "bmiStatus": "overweight",
    "ffmKg": 76.3,
    "fatMassKg": 16.2
  },
  "energyMetrics": {
    "bmr": 2031,
    "bmrEquation": "katch_mcardle",
    "activityMultiplier": 1.20,
    "neat": 406,
    "baseTdee": 2437,
    "dailyDeficit": 550,
    "estimatedDailyCalories": 1887
  },
  "energyAvailability": {
    "eaKcalPerKgFfm": 24.7,
    "eaStatus": "low_ea"
  },
  "weeklySummary": {
    "weeklyDeficitKcal": 3850,
    "expectedLossKgPerWeek": 0.5,
    "monthlyLossKg": 2.2,
    "totalToGoalKg": 7.5
  }
}
```

#### Training Program Endpoints

```python
# GET /api/v1/programs
# Response: List[TrainingProgramPublic]
[
  {
    "id": 1,
    "name": "Beginner Full Body",
    "description": "3-day full body routine for beginners",
    "daysPerWeek": 3,
    "difficulty": "beginner"
  },
  ...
]

# POST /api/v1/programs/{program_id}/select
# Response: UserProfilePublic (with updated selectedProgramId)
```

#### Plan Endpoints

```python
# GET /api/v1/plans/meal/today
# Response: List[MealPlanPublic]
[
  {
    "id": 1,
    "mealType": "breakfast",
    "itemName": "Oatmeal with berries",
    "calories": 350,
    "protein": 12,
    "carbs": 55,
    "fat": 8
  },
  ...
]

# GET /api/v1/plans/training/today
# Response: List[TrainingRoutinePublic]
[
  {
    "id": 1,
    "exerciseName": "Squat",
    "machineHint": "Barbell or Smith Machine",
    "sets": 3,
    "reps": 10,
    "targetLoad": 60
  },
  ...
]
```

#### Log Endpoints

```python
# GET /api/v1/logs/today
# Response: DailyLogsResponse
{
  "mealLogs": [
    {
      "id": "123",
      "name": "Banana",
      "calories": 105,
      "protein": 1.3,
      "carbs": 27,
      "fat": 0.4,
      "time": "2024-01-15T08:30:00Z",
      "type": "snack"
    }
  ],
  "exerciseLogs": [
    {
      "id": "456",
      "name": "Bench Press",
      "sets": 3,
      "reps": 10,
      "weight": 60,
      "time": "2024-01-15T10:00:00Z"
    }
  ]
}

# POST /api/v1/logs/meal
# Request: MealLogCreate
{
  "mealName": "Banana",
  "mealType": "snack",
  "calories": 105,
  "protein": 1.3,
  "carbs": 27,
  "fat": 0.4
}
# Response: MealLogPublic

# POST /api/v1/logs/exercise
# Request: ExerciseLogCreate
{
  "exerciseName": "Bench Press",
  "sets": 3,
  "reps": 10,
  "weight": 60
}
# Response: ExerciseLogPublic
```

#### Summary Endpoint

```python
# GET /api/v1/summary/today
# Response: DailySummary
{
  "caloriesConsumed": 1450,
  "caloriesTarget": 2000,
  "proteinConsumed": 95,
  "proteinTarget": 150,
  "workoutsCompleted": 1,
  "caloriesRemaining": 550,
  "proteinRemaining": 55
}
```

### 3. CSV Import Service

```python
class CSVImportService:
    """Service for loading CSV data into database on startup"""
    
    async def load_training_programs(self, csv_path: str) -> None:
        """Load predefined training programs and routines from CSV"""
        pass
    
    async def load_default_meal_plans(self, csv_path: str) -> None:
        """Load default meal plan templates from CSV"""
        pass
```

CSV Format for Training Programs:
```csv
program_id,program_name,description,days_per_week,difficulty,day_of_week,exercise_name,machine_hint,sets,reps,target_load_kg
1,Beginner Full Body,3-day full body routine,3,beginner,0,Squat,Barbell,3,10,40
1,Beginner Full Body,3-day full body routine,3,beginner,0,Bench Press,Barbell,3,10,30
...
```

CSV Format for Meal Plans:
```csv
user_id,day_of_week,meal_type,item_name,calories,protein_g,carbs_g,fat_g
1,0,breakfast,Oatmeal with berries,350,12,55,8
1,0,lunch,Chicken salad,450,40,30,15
...
```

## Data Models

See "Components and Interfaces" section above for detailed model definitions.

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Tenant isolation

*For any* two different users, querying meal plans, training routines, or logs for one user should never return data belonging to the other user.

**Validates: Requirements 1.2, 1.3, 1.4**

### Property 2: Profile validation bounds

*For any* user profile update, if weight is outside the range [30, 300] kg or height is outside [100, 250] cm, the system should reject the update and return a validation error.

**Validates: Requirements 2.2, 2.3**

### Property 3: Goal method enumeration

*For any* user profile update with a goal method, the system should only accept the values "cut", "bulk", or "maintain", rejecting any other value.

**Validates: Requirements 2.4**

### Property 4: Training program availability

*For any* request to list training programs, the system should return between 3 and 6 programs inclusive.

**Validates: Requirements 4.1**

### Property 5: Program selection association

*For any* user who selects a training program, subsequent requests for that user's profile should reflect the selected program ID.

**Validates: Requirements 4.3**

### Property 6: Routine filtering by program

*For any* user with a selected program, requesting today's training routine should return only exercises from that program matching the current day of week.

**Validates: Requirements 4.4, 4.5**

### Property 7: Empty routine for unselected program

*For any* user who has not selected a training program, requesting today's training routine should return an empty list.

**Validates: Requirements 5.5**

### Property 8: Non-negative validation for logs

*For any* meal log or exercise log creation, if any numeric field (calories, protein, sets, reps, weight) is negative, the system should reject the log and return a validation error.

**Validates: Requirements 6.4, 6.5**

### Property 9: Summary calculation accuracy

*For any* user's daily summary, the total calories consumed should equal the sum of all meal log calories for that day, and calories remaining should equal target minus consumed.

**Validates: Requirements 7.1, 7.4**

### Property 10: Log timestamp ordering

*For any* user's daily logs, all returned logs should have timestamps within the current calendar day in the user's timezone.

**Validates: Requirements 6.3**

## Error Handling

### Validation Errors (422)

- Invalid weight/height ranges
- Invalid goal method values
- Negative values for calories, macros, sets, reps, weight
- Missing required fields

Response format:
```json
{
  "detail": [
    {
      "loc": ["body", "weight"],
      "msg": "ensure this value is greater than or equal to 30",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

### Not Found Errors (404)

- Training program not found
- User profile not found
- Log entry not found

### Authentication Errors (401)

- Missing or invalid JWT token
- Expired token

### Authorization Errors (403)

- Attempting to access another user's data

### Server Errors (500)

- Database connection failures
- CSV import failures
- Unexpected exceptions

All errors should be logged with appropriate context for debugging.

## Testing Strategy

### Unit Testing

Unit tests will verify:
- Model validation (Pydantic constraints)
- CRUD operations in isolation
- CSV parsing logic
- Date/time calculations for "today" filtering
- Summary calculation functions

### Property-Based Testing

Property-based tests will use **Hypothesis** (Python's PBT library) to verify the correctness properties defined above. Each property will be implemented as a separate test function.

Configuration:
- Minimum 100 iterations per property test
- Custom generators for valid user data, logs, and plans
- Shrinking enabled to find minimal failing examples

Test tagging format:
```python
# Feature: foundation, Property 1: Tenant isolation
@given(user1=user_strategy(), user2=user_strategy())
def test_tenant_isolation(user1, user2):
    ...
```

### Integration Testing

Integration tests will verify:
- Full request/response cycles through FastAPI
- Database transactions and rollbacks
- Authentication flow with JWT
- CSV import on application startup

### Edge Cases

- User with no selected program
- Empty meal/exercise logs for a day
- Leap year date handling
- Timezone boundary cases (midnight)
- Maximum field lengths
- Concurrent log creation

## Implementation Notes

### Database Migrations

Use Alembic for all schema changes:
```bash
alembic revision --autogenerate -m "Add foundation models"
alembic upgrade head
```

### CSV Loading

CSV files should be loaded on application startup via a lifespan event:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load CSVs
    await csv_service.load_training_programs("data/programs.csv")
    await csv_service.load_default_meal_plans("data/meal_plans.csv")
    yield
    # Shutdown: cleanup if needed
```

### Authentication Integration

Leverage existing FastAPI template authentication:
- Use `get_current_user` dependency for protected endpoints
- User ID from JWT token ensures tenant isolation
- All endpoints except `/login` and `/register` require authentication

### Frontend Integration

The backend should match the TypeScript interfaces defined in `.kiro/frontend-frankenstein-fitness-copilot/types.ts`:
- Use camelCase in JSON responses (configure Pydantic alias generator)
- Date/time fields as ISO 8601 strings
- Numeric IDs as strings in responses (for consistency with frontend)

### Performance Considerations

- Index `user_id` and `logged_at` columns for fast filtering
- Use database-level date functions for "today" queries
- Consider caching training programs (rarely change)
- Paginate logs if user has many entries
