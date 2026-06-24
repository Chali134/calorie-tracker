# Calorie Tracker

A brutalist calorie & exercise tracker built with **FastAPI**, **HTMX**, and **Tailwind CSS**. Works as a **Progressive Web App** on iOS and Android. Pure black background, sharp corners, flat orange accent — zero gradients, zero shadows.

## Features

- **Daily dashboard** — animated progress ring (eaten % of goal), macronutrient breakdown, 7-day bar chart
- **Meal logging** — bottom sheet modal with searchable food database, servings, meal types (breakfast/lunch/dinner/snack)
- **Exercise tracking** — 100 exercises across 7 muscle groups, log sets/reps/weight, auto-calorie burn estimate, complete/delete workouts
- **Muscle group accordion** — today's exercises grouped by muscle group, expand/collapse like meals
- **Activity tab** — date picker to browse past meals & workouts, weekly calorie intake + burned charts, stats grid (weight, avg intake, streak, BMI)
- **Profile tab** — user card with photo upload, today's macro progress bars with fill % (calories, protein, carbs, fat), quick stats row, workout planner notes per day
- **Workout planner** — save daily workout notes/plans, date picker per day, persisted in DB
- **Reminders** — configurable meal logging reminders with toggles and time pickers, browser notifications
- **Water tracker** — 8-drop visual tracker stored in localStorage
- **Onboarding** — age, weight, height, gender, activity level, goal type → auto-calculates TDEE & macro targets
- **Food database** — 100+ seeded foods with serving sizes, favourites, recent foods
- **TDEE calculator** — Mifflin-St Jeor with activity multiplier, goal adjustment (cut/maintain/bulk)
- **Live updates** — HTMX-powered, no page reloads on any CRUD
- **PWA ready** — manifest, Apple touch icon, add to home screen
- **User auth** — sign up, login, session cookies, logout

## Quick Start

```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Open http://localhost:8000 — sign up, complete onboarding, start tracking.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| Database | SQLite (via aiosqlite) |
| Templating | Jinja2 |
| Frontend | HTMX 2.0 + Tailwind CSS |
| Font | Urbanist (Google Fonts) |
| PWA | Manifest + Service Worker |

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Dashboard |
| GET | `/login` | Login page |
| POST | `/login` | Authenticate |
| GET | `/signup` | Sign up page |
| POST | `/signup` | Create user |
| POST | `/logout` | Sign out |
| GET | `/onboarding` | Onboarding form |
| POST | `/onboarding` | Save profile + TDEE |
| GET | `/meals` | Today's meals (HTMX) |
| POST | `/meals` | Add a meal |
| DELETE | `/meals/{id}` | Delete a meal |
| GET | `/foods/search` | Search food database |
| POST | `/favourites/{id}` | Toggle favourite |
| GET | `/activity` | Activity tab (HTMX) |
| GET | `/day/{date}` | Day detail (meals + workouts) |
| GET | `/training` | Exercise browser (HTMX) |
| POST | `/workouts` | Log a workout |
| DELETE | `/workouts/{id}` | Remove workout |
| POST | `/workouts/{id}/complete` | Toggle complete |
| GET | `/note` | Get workout note for date |
| POST | `/note` | Save workout note |
| POST | `/reminders/{id}` | Update reminder |
| POST | `/profile/photo` | Upload avatar |
| GET | `/export` | Export meal data as CSV |

## Project Structure

```
├── main.py                    # FastAPI routes
├── database.py                # SQLite setup + queries + seed data
├── models.py                  # Pydantic schemas
├── tdee.py                    # TDEE calculation
├── requirements.txt
├── templates/
│   ├── base.html              # Base layout + PWA meta
│   ├── index.html             # Full app (all tabs + nav + modals)
│   ├── login.html / signup.html
│   ├── onboarding.html
│   └── partials/
│       ├── dashboard_content.html
│       ├── activity_content.html
│       ├── training_content.html
│       ├── day_detail.html
│       ├── food_results.html
│       ├── reminders_list.html
│       └── note_input.html
└── static/
    ├── css/style.css           # Complete brutalist styles
    ├── manifest.json
    ├── icon.png
    └── uploads/                # Avatar storage
```
