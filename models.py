from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class MealCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    calories: float = Field(..., gt=0, le=10000)
    protein: float = Field(default=0, ge=0, le=1000)
    carbs: float = Field(default=0, ge=0, le=1000)
    fat: float = Field(default=0, ge=0, le=1000)
    meal_type: str = Field(default="snack", pattern="^(breakfast|lunch|dinner|snack)$")
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
