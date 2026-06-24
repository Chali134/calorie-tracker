from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from datetime import date

from database import init_db, get_db
from models import MealCreate, Goals

BASE_DIR = Path(__file__).parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


async def get_goals() -> Goals:
    db = await get_db()
    row = await db.execute_fetchall("SELECT * FROM goals WHERE id = 1")
    await db.close()
    if row:
        r = row[0]
        return Goals(
            calorie_target=r["calorie_target"],
            protein_target=r["protein_target"],
            carbs_target=r["carbs_target"],
            fat_target=r["fat_target"],
        )
    return Goals()


async def get_today_meals(d: str | None = None) -> list[dict]:
    if d is None:
        d = date.today().isoformat()
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT * FROM meals WHERE date = ? ORDER BY created_at DESC", (d,)
    )
    await db.close()
    return [dict(r) for r in rows]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, d: str | None = None):
    if d is None:
        d = date.today().isoformat()
    meals = await get_today_meals(d)
    goals = await get_goals()
    total_cal = sum(m["calories"] for m in meals)
    total_pro = sum(m["protein"] for m in meals)
    total_carb = sum(m["carbs"] for m in meals)
    total_fat = sum(m["fat"] for m in meals)
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "meals": meals,
            "goals": goals,
            "total_calories": total_cal,
            "total_protein": total_pro,
            "total_carbs": total_carb,
            "total_fat": total_fat,
            "selected_date": d,
        },
    )


@app.get("/meals", response_class=HTMLResponse)
async def meal_list(request: Request, d: str | None = None):
    if d is None:
        d = date.today().isoformat()
    meals = await get_today_meals(d)
    goals = await get_goals()
    total_cal = sum(m["calories"] for m in meals)
    total_pro = sum(m["protein"] for m in meals)
    total_carb = sum(m["carbs"] for m in meals)
    total_fat = sum(m["fat"] for m in meals)
    return templates.TemplateResponse(
        request,
        "partials/meal_list.html",
        {
            "request": request,
            "meals": meals,
            "goals": goals,
            "total_calories": total_cal,
            "total_protein": total_pro,
            "total_carbs": total_carb,
            "total_fat": total_fat,
            "selected_date": d,
        },
    )


@app.post("/meals")
async def add_meal(
    request: Request,
    name: str = Form(...),
    calories: float = Form(...),
    protein: float = Form(0),
    carbs: float = Form(0),
    fat: float = Form(0),
    meal_type: str = Form("snack"),
    d: str | None = Form(None),
):
    if d is None:
        d = date.today().isoformat()
    meal = MealCreate(name=name, calories=calories, protein=protein, carbs=carbs, fat=fat, meal_type=meal_type, date=d)
    db = await get_db()
    await db.execute(
        "INSERT INTO meals (name, calories, protein, carbs, fat, meal_type, date) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (meal.name, meal.calories, meal.protein, meal.carbs, meal.fat, meal.meal_type, meal.date),
    )
    await db.commit()
    await db.close()
    meals = await get_today_meals(d)
    goals = await get_goals()
    total_cal = sum(m["calories"] for m in meals)
    total_pro = sum(m["protein"] for m in meals)
    total_carb = sum(m["carbs"] for m in meals)
    total_fat = sum(m["fat"] for m in meals)
    return templates.TemplateResponse(
        request,
        "partials/meal_list.html",
        {
            "request": request,
            "meals": meals,
            "goals": goals,
            "total_calories": total_cal,
            "total_protein": total_pro,
            "total_carbs": total_carb,
            "total_fat": total_fat,
            "selected_date": d,
        },
    )


@app.delete("/meals/{meal_id}")
async def delete_meal(request: Request, meal_id: int):
    db = await get_db()
    await db.execute("DELETE FROM meals WHERE id = ?", (meal_id,))
    await db.commit()
    await db.close()
    d = date.today().isoformat()
    meals = await get_today_meals(d)
    goals = await get_goals()
    total_cal = sum(m["calories"] for m in meals)
    total_pro = sum(m["protein"] for m in meals)
    total_carb = sum(m["carbs"] for m in meals)
    total_fat = sum(m["fat"] for m in meals)
    return templates.TemplateResponse(
        request,
        "partials/meal_list.html",
        {
            "request": request,
            "meals": meals,
            "goals": goals,
            "total_calories": total_cal,
            "total_protein": total_pro,
            "total_carbs": total_carb,
            "total_fat": total_fat,
            "selected_date": d,
        },
    )
