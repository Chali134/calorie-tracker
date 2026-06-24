from pydantic import BaseModel, Field
from datetime import date


class MealCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    calories: float = Field(..., gt=0, le=10000)
    protein: float = Field(default=0, ge=0, le=1000)
    carbs: float = Field(default=0, ge=0, le=1000)
    fat: float = Field(default=0, ge=0, le=1000)
    meal_type: str = Field(default="snack", pattern="^(breakfast|lunch|dinner|snack)$")
    servings: float = Field(default=1, gt=0, le=100)
    date: str = Field(default_factory=lambda: date.today().isoformat())


class MealResponse(BaseModel):
    id: int
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    meal_type: str
    date: str
    servings: float = 1


class Goals(BaseModel):
    calorie_target: float = 2000
    protein_target: float = 50
    carbs_target: float = 250
    fat_target: float = 65


class DailySummary(BaseModel):
    total_calories: float = 0
    total_protein: float = 0
    total_carbs: float = 0
    total_fat: float = 0
    meals: list[MealResponse] = []
    goals: Goals = Goals()


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, pattern="^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    username: str
    password: str


class OnboardingData(BaseModel):
    age: int = Field(..., ge=10, le=120)
    weight: float = Field(..., ge=20, le=500)
    height: float = Field(..., ge=50, le=300)
    gender: str = Field(..., pattern="^(male|female)$")
    activity_level: str = Field(..., pattern="^(sedentary|light|moderate|active|very_active)$")
    goal_type: str = Field(..., pattern="^(lose|maintain|gain)$")


class FoodResponse(BaseModel):
    id: int
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    serving_size_g: float = 100
    serving_unit: str = "g"
    is_favourite: bool = False
