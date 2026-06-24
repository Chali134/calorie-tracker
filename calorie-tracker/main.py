import csv, io
from pathlib import Path
from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from datetime import date, timedelta

from database import (
    init_db, get_db, search_foods,
    create_user, authenticate_user,
    create_session, get_user_by_token,
    delete_session, get_or_create_goals, update_goals,
    create_profile, get_profile,
    update_profile_avatar,
    add_favourite_food, remove_favourite_food,
    get_favourite_foods, is_favourite,
    get_recent_foods,
    get_reminders, save_reminder,
)
from models import MealCreate, Goals
from tdee import calculate_targets

BASE_DIR = Path(__file__).parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


async def get_current_user(request: Request) -> dict | None:
    token = request.cookies.get("session")
    if not token:
        return None
    return await get_user_by_token(token)


def require_user(user: dict | None):
    if not user:
        raise HTTPException(status_code=303, detail="Not authenticated")


async def get_goals_typed(user_id: int) -> Goals:
    g = await get_or_create_goals(user_id)
    return Goals(
        calorie_target=g["calorie_target"],
        protein_target=g["protein_target"],
        carbs_target=g["carbs_target"],
        fat_target=g["fat_target"],
    )


async def get_today_meals(user_id: int, d: str | None = None) -> list[dict]:
    if d is None:
        d = date.today().isoformat()
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT * FROM meals WHERE user_id = ? AND date = ? ORDER BY created_at DESC",
        (user_id, d),
    )
    await db.close()
    return [dict(r) for r in rows]


async def get_week_data(user_id: int) -> list[float]:
    today = date.today()
    db = await get_db()
    week = []
    for i in range(6, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        rows = await db.execute_fetchall(
            "SELECT SUM(calories) as total FROM meals WHERE user_id = ? AND date = ?",
            (user_id, d),
        )
        week.append(rows[0]["total"] or 0)
    await db.close()
    return week


async def get_streak(user_id: int) -> int:
    db = await get_db()
    streak = 0
    d = date.today()
    for i in range(60):
        ds = d.isoformat()
        rows = await db.execute_fetchall(
            "SELECT COUNT(*) as cnt FROM meals WHERE user_id = ? AND date = ?",
            (user_id, ds),
        )
        if rows[0]["cnt"] > 0:
            streak += 1
            d -= timedelta(days=1)
        else:
            break
    await db.close()
    return streak


async def get_avg_calories(user_id: int, days: int = 7) -> float:
    today = date.today()
    start = (today - timedelta(days=days - 1)).isoformat()
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT AVG(daily) as avg FROM (SELECT SUM(calories) as daily FROM meals WHERE user_id = ? AND date >= ? GROUP BY date)",
        (user_id, start),
    )
    await db.close()
    return rows[0]["avg"] or 0


# ── Auth pages ──────────────────────────────────────────────

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user = await get_current_user(request)
    if user:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(request, "login.html", {"request": request})


@app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    user = await authenticate_user(username, password)
    if not user:
        return templates.TemplateResponse(
            request, "login.html",
            {"request": request, "error": "Invalid username or password"},
            status_code=400,
        )
    token = await create_session(user["id"])
    resp = RedirectResponse("/", status_code=302)
    resp.set_cookie(key="session", value=token, httponly=True, max_age=86400 * 30, samesite="lax")
    return resp


@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    user = await get_current_user(request)
    if user:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(request, "signup.html", {"request": request})


@app.post("/signup")
async def signup(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    if len(username) < 3:
        return templates.TemplateResponse(
            request, "signup.html",
            {"request": request, "error": "Username must be at least 3 characters"},
            status_code=400,
        )
    if len(password) < 6:
        return templates.TemplateResponse(
            request, "signup.html",
            {"request": request, "error": "Password must be at least 6 characters"},
            status_code=400,
        )
    user = await create_user(username, password)
    if not user:
        return templates.TemplateResponse(
            request, "signup.html",
            {"request": request, "error": "Username already taken"},
            status_code=400,
        )
    token = await create_session(user["id"])
    resp = RedirectResponse("/onboarding", status_code=302)
    resp.set_cookie(key="session", value=token, httponly=True, max_age=86400 * 30, samesite="lax")
    return resp


@app.post("/logout")
async def logout(request: Request):
    token = request.cookies.get("session")
    if token:
        await delete_session(token)
    resp = RedirectResponse("/login", status_code=302)
    resp.delete_cookie("session")
    return resp


# ── Onboarding ──────────────────────────────────────────────

@app.get("/onboarding", response_class=HTMLResponse)
async def onboarding_page(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    profile = await get_profile(user["id"])
    if profile and profile.get("onboarded"):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(request, "onboarding.html", {
        "request": request,
        "user": user,
    })


@app.post("/onboarding")
async def onboarding_submit(
    request: Request,
    age: int = Form(...),
    weight: float = Form(...),
    height: float = Form(...),
    gender: str = Form(...),
    activity_level: str = Form(...),
    goal_type: str = Form(...),
):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    await create_profile(user["id"], age, weight, height, gender, activity_level, goal_type)

    targets = calculate_targets(weight, height, age, gender, activity_level, goal_type)
    await update_goals(
        user["id"],
        targets["calorie_target"],
        targets["protein_target"],
        targets["carbs_target"],
        targets["fat_target"],
    )

    return RedirectResponse("/", status_code=302)


# ── Protected routes ────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, d: str | None = None):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    profile = await get_profile(user["id"])
    if not profile or not profile.get("onboarded"):
        return RedirectResponse("/onboarding", status_code=302)
    if d is None:
        d = date.today().isoformat()
    meals = await get_today_meals(user["id"], d)
    goals = await get_goals_typed(user["id"])
    total_cal = sum(m["calories"] for m in meals)
    total_pro = sum(m["protein"] for m in meals)
    total_carb = sum(m["carbs"] for m in meals)
    total_fat = sum(m["fat"] for m in meals)
    recent = await get_recent_foods(user["id"], 5)
    favourites = await get_favourite_foods(user["id"], 5)
    reminders = await get_reminders(user["id"])
    avg_calories = await get_avg_calories(user["id"])
    streak = await get_streak(user["id"])
    week_data = await get_week_data(user["id"])
    bmi_val = 0
    bmi_label = ""
    bmi_desc = ""
    if profile:
        h_m = profile["height"] / 100
        bmi_val = round(profile["weight"] / (h_m * h_m), 1)
        if bmi_val < 18.5:
            bmi_label = "Underweight"
            bmi_desc = "Consider gaining weight"
        elif bmi_val < 25:
            bmi_label = "Normal"
            bmi_desc = "Healthy range"
        elif bmi_val < 30:
            bmi_label = "Overweight"
            bmi_desc = "Consider losing weight"
        else:
            bmi_label = "Obese"
            bmi_desc = "Consult a professional"
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "user": user,
            "profile": profile,
            "meals": meals,
            "goals": goals,
            "total_calories": total_cal,
            "total_protein": total_pro,
            "total_carbs": total_carb,
            "total_fat": total_fat,
            "selected_date": d,
            "recent_foods": recent,
            "favourite_foods": favourites,
            "avg_calories": round(avg_calories),
            "streak": streak,
            "week_data": week_data,
            "bmi": bmi_val,
            "bmi_label": bmi_label,
            "bmi_desc": bmi_desc,
            "reminders": reminders,
        },
    )


@app.get("/foods/search", response_class=HTMLResponse)
async def food_search(request: Request, q: str = "", compact: str = "0"):
    user = await get_current_user(request)
    if not user:
        return HTMLResponse("")
    results = await search_foods(q) if q else []
    fav_ids = set()
    for f in results:
        if await is_favourite(user["id"], f["id"]):
            fav_ids.add(f["id"])
    return templates.TemplateResponse(
        request,
        "partials/food_results.html",
        {"request": request, "results": results, "fav_ids": fav_ids, "compact": compact == "1"},
    )


@app.get("/meals", response_class=HTMLResponse)
async def meal_list(request: Request, d: str | None = None):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    if d is None:
        d = date.today().isoformat()
    meals = await get_today_meals(user["id"], d)
    goals = await get_goals_typed(user["id"])
    total_cal = sum(m["calories"] for m in meals)
    total_pro = sum(m["protein"] for m in meals)
    total_carb = sum(m["carbs"] for m in meals)
    total_fat = sum(m["fat"] for m in meals)
    return templates.TemplateResponse(
        request,
        "partials/dashboard_content.html",
        {
            "request": request,
            "user": user,
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
    servings: float = Form(1),
    d: str | None = Form(None),
):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    if d is None:
        d = date.today().isoformat()
    meal = MealCreate(name=name, calories=calories, protein=protein, carbs=carbs, fat=fat, meal_type=meal_type, servings=servings, date=d)
    db = await get_db()
    await db.execute(
        "INSERT INTO meals (user_id, name, calories, protein, carbs, fat, meal_type, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (user["id"], meal.name, meal.calories, meal.protein, meal.carbs, meal.fat, meal.meal_type, meal.date),
    )
    await db.commit()
    await db.close()
    meals = await get_today_meals(user["id"], d)
    goals = await get_goals_typed(user["id"])
    total_cal = sum(m["calories"] for m in meals)
    total_pro = sum(m["protein"] for m in meals)
    total_carb = sum(m["carbs"] for m in meals)
    total_fat = sum(m["fat"] for m in meals)
    return templates.TemplateResponse(
        request,
        "partials/dashboard_content.html",
        {
            "request": request,
            "user": user,
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
    user = await get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    db = await get_db()
    rows = await db.execute_fetchall("SELECT date FROM meals WHERE id = ? AND user_id = ?", (meal_id, user["id"]))
    d = date.today().isoformat()
    if rows:
        d = rows[0]["date"]
    await db.execute("DELETE FROM meals WHERE id = ? AND user_id = ?", (meal_id, user["id"]))
    await db.commit()
    await db.close()
    meals = await get_today_meals(user["id"], d)
    goals = await get_goals_typed(user["id"])
    total_cal = sum(m["calories"] for m in meals)
    total_pro = sum(m["protein"] for m in meals)
    total_carb = sum(m["carbs"] for m in meals)
    total_fat = sum(m["fat"] for m in meals)
    return templates.TemplateResponse(
        request,
        "partials/dashboard_content.html",
        {
            "request": request,
            "user": user,
            "meals": meals,
            "goals": goals,
            "total_calories": total_cal,
            "total_protein": total_pro,
            "total_carbs": total_carb,
            "total_fat": total_fat,
            "selected_date": d,
        },
    )


@app.get("/export")
async def export_data(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT date, meal_type, name, calories, protein, carbs, fat FROM meals WHERE user_id = ? ORDER BY date DESC, created_at DESC",
        (user["id"],),
    )
    await db.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Meal Type", "Food", "Calories", "Protein (g)", "Carbs (g)", "Fat (g)"])
    for r in rows:
        writer.writerow([r["date"], r["meal_type"], r["name"], r["calories"], r["protein"], r["carbs"], r["fat"]])
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=calorie_tracker_export.csv"},
    )


@app.post("/profile/photo")
async def upload_photo(request: Request, photo: UploadFile = File(...)):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    if not photo.content_type or not photo.content_type.startswith("image/"):
        return HTMLResponse("Invalid file type", status_code=400)
    ext = Path(photo.filename).suffix if photo.filename else ".jpg"
    filename = f"avatar_{user['id']}{ext}"
    upload_dir = BASE_DIR / "static" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    content = await photo.read()
    with open(upload_dir / filename, "wb") as f:
        f.write(content)
    avatar_url = f"/static/uploads/{filename}"
    await update_profile_avatar(user["id"], avatar_url)
    return RedirectResponse("/", status_code=302)


@app.post("/reminders/{reminder_id}")
async def update_reminder(
    request: Request,
    reminder_id: int,
    time: str = Form(...),
    enabled: int = Form(0),
):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    await save_reminder(reminder_id, user["id"], time, enabled)
    reminders = await get_reminders(user["id"])
    return templates.TemplateResponse(
        request, "partials/reminders_list.html",
        {"request": request, "reminders": reminders},
    )


@app.post("/favourites/{food_id}")
async def toggle_favourite(request: Request, food_id: int):
    user = await get_current_user(request)
    if not user:
        return HTMLResponse("", status_code=401)
    if await is_favourite(user["id"], food_id):
        await remove_favourite_food(user["id"], food_id)
        return HTMLResponse("☆")
    else:
        await add_favourite_food(user["id"], food_id)
        return HTMLResponse("★")
