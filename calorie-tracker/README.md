# CalTrack — Brutalist Calorie & Workout Tracker

A **Progressive Web App** for tracking daily calories, macronutrients, and workouts — built with **FastAPI**, **HTMX**, and **Tailwind CSS**. Features a distinctive **New Brutalism** design: pure black background, sharp corners, flat orange accent, zero gradients or shadows.

## Features

### 🍽️ Meal Tracking
- **Dashboard** — animated SVG ring showing eaten % of daily goal, macronutrient breakdown (protein/carbs/fat), 7-day intake bar chart
- **Bottom-sheet modal** — searchable 100+ food database with serving sizes, meal types (breakfast/lunch/dinner/snack)
- **Favourites & Recent** — star foods for quick access, recently-used foods shown first
- **Meal accordion** — meals grouped by type, expand/collapse with animated chevron

### 🏋️ Exercise Tracking
- **100 exercises** across 7 muscle groups (Chest, Back, Legs, Shoulders, Arms, Core, Cardio)
- **Log workouts** — sets, reps, weight; auto-calculated calorie burn (`cal_per_hour / 30 × sets`)
- **Muscle group accordion** — today's exercises grouped by muscle with totals
- **Complete/delete** — mark sets done, remove log entries
- **Filter by muscle** — quick-filter buttons for the exercise browser

### 📊 Activity & Progress
- **Day picker** — browse past/future dates, view meals + workouts for any day
- **7-day intake chart** — bars with value labels, goal line, today highlighted
- **7-day burned chart** — green bars showing calories burned via workouts
- **Stats grid** — weight, average intake, streak, BMI with label/description

### 👤 Profile
- **User card** — avatar upload, username, goal type, activity level
- **Quick stats** — meals logged, calories burned, exercises done, streak
- **Macro progress bars** — today's calories, protein, carbs, fat with fill percentage
- **Workout planner notes** — daily textarea notes persisted per date, date picker
- **Settings** — reminders modal, CSV export, sign out
- **Credits** — built by Theo, free for everyone

### 🔔 Reminders
- 6 configurable defaults (breakfast, lunch, dinner, snack, general log, water)
- Enable/disable toggle per reminder, time picker
- Browser Notification API + in-app toast, checks every 30s

### 💧 Water Tracker
- 8-drop visual tracker stored in `localStorage`
- Click to fill/unfill drops

### 🧮 TDEE Calculator
- **Mifflin-St Jeor equation** with gender-specific formulas
- Activity multipliers (sedentary → very active)
- Goal adjustments (lose ×0.8, maintain ×1.0, gain ×1.15)
- Macro split: 30% protein / 40% carbs / 30% fat

### 📱 PWA Ready
- Add to home screen (standalone mode, no browser chrome)
- Offline-capable service worker
- iOS `viewport-fit=cover` notch support
- Portrait orientation lock
- Dark theme (`#080808` background)

## Quick Start

```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Open **http://localhost:8000** — sign up, complete onboarding (age/weight/height/activity/goal), and start tracking.

**Database**: Creates `calories.db` automatically on first run. Delete it to reset all data.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.10+) |
| Database | SQLite (aiosqlite, WAL mode) |
| Templating | Jinja2 |
| Frontend | HTMX 2.0 |
| Styling | Tailwind CSS (CDN) + custom stylesheet |
| Font | Urbanist (Google Fonts, 300–800) |
| Auth | bcrypt hashing, session cookies |
| PWA | Manifest JSON + Service Worker |
| Icons | Y2K-style inline SVGs (stroke-width: 3) |

## Architecture

### HTMX-Driven SPA
- **No JSON API** — all CRUD returns HTML partials
- `hx-target` / `hx-swap` for live DOM updates
- Tab switching calls `htmx.ajax()` to refresh tab content
- Modals (add meal, reminders) submit via `hx-post` and replace partials
- Auto-refresh: after workout changes, dashboard content refreshes automatically

### Session Flow
```
/signup → POST /signup → session cookie → /onboarding → POST /onboarding → /
/login  → POST /login  → session cookie → /
                                    /logout → delete session → redirect /login
```

### Data Flow per Request
```
Browser → HTMX → FastAPI route → database.py (async SQLite) → Jinja2 partial → HTMX swaps DOM
```

## API Routes

### Auth
| Method | Path | Description |
|---|---|---|
| GET | `/login` | Login page |
| POST | `/login` | Authenticate, set session cookie |
| GET | `/signup` | Registration page |
| POST | `/signup` | Create user (≥3 char name, ≥6 char pass) |
| POST | `/logout` | Clear session, redirect to `/login` |

### Onboarding
| Method | Path | Description |
|---|---|---|
| GET | `/onboarding` | Profile setup form |
| POST | `/onboarding` | Save profile, calculate TDEE/macros, redirect to `/` |

### Dashboard
| Method | Path | Description |
|---|---|---|
| GET | `/` | Main SPA shell (`index.html`) with all tab data |
| GET | `/meals` | HTMX partial: today's meals dashboard |
| POST | `/meals` | Add a meal (`name`, `calories`, `protein`, `carbs`, `fat`, `meal_type`, `servings`) |
| DELETE | `/meals/{id}` | Delete a meal |

### Food Database
| Method | Path | Description |
|---|---|---|
| GET | `/foods/search` | Search foods (`q` query, `compact` 0/1) |
| POST | `/favourites/{food_id}` | Toggle favourite food (returns `★` or `☆`) |

### Exercise / Workouts
| Method | Path | Description |
|---|---|---|
| GET | `/training` | HTMX partial: exercise browser + today's workouts |
| POST | `/workouts` | Log workout (`exercise_id`, `sets`, `reps`, `weight_kg`) |
| DELETE | `/workouts/{id}` | Remove a workout |
| POST | `/workouts/{id}/complete` | Toggle completion |

### Activity
| Method | Path | Description |
|---|---|---|
| GET | `/day/{date}` | HTMX partial: meals + workouts for specific date |

### Workout Notes
| Method | Path | Description |
|---|---|---|
| GET | `/note` | HTMX partial: get note for date (`d` param) |
| POST | `/note` | HTMX partial: save/update note (`d`, `content`) |

### Reminders
| Method | Path | Description |
|---|---|---|
| POST | `/reminders/{id}` | Update reminder time/enabled |

### Profile
| Method | Path | Description |
|---|---|---|
| POST | `/profile/photo` | Upload avatar image |
| GET | `/export` | Download meal data as CSV |

## Database Schema

### Tables

| Table | Key Columns | Notes |
|---|---|---|
| `users` | `id`, `username` (UNIQUE), `password_hash`, `created_at` | bcrypt hashed passwords |
| `sessions` | `token` (PK), `user_id` (FK), `created_at` | 43-char url-safe tokens |
| `meals` | `id`, `user_id` (FK), `name`, `calories`, `protein`, `carbs`, `fat`, `meal_type`, `date` (ISO) | Per-user, per-date meal log |
| `goals` | `user_id` (UNIQUE FK), `calorie_target`, `protein_target`, `carbs_target`, `fat_target` | Auto-created on signup |
| `foods` | `id`, `name` (UNIQUE), `calories`, `protein`, `carbs`, `fat`, `serving_size_g`, `serving_unit` | 104 seeded foods |
| `user_profile` | `user_id` (UNIQUE FK), `age`, `weight`, `height`, `gender`, `activity_level`, `goal_type`, `tdee`, `onboarded`, `avatar_url` | Created during onboarding |
| `favourite_foods` | `user_id` (FK), `food_id` (FK) — composite PK | Quick-access favourites |
| `reminders` | `id`, `user_id` (FK), `meal_type`, `label`, `time`, `enabled` | 6 per user on signup |
| `exercises` | `id`, `name` (UNIQUE), `muscle_group`, `calories_per_hour` | 107 seeded exercises |
| `workouts` | `id`, `user_id` (FK), `exercise_id` (FK), `date` (ISO), `sets`, `reps`, `weight_kg`, `completed` | Per-set workout log |
| `workout_notes` | `user_id` (FK), `date`, `content`, `created_at`, `updated_at` | UNIQUE(user_id, date) upsert |

### Calorie Burn Formula
```
calories_burned = calories_per_hour / 30 * sets
```
(Each set ≈ 2 minutes = 1/30th hour)

### Net Calories
```
remaining = daily_goal - calories_eaten + calories_burned
```

## Project Structure

```
calorie-tracker/
├── main.py                  # FastAPI app: routes, auth, HTMX handlers
├── database.py              # SQLite: schema, seed data, all queries
├── models.py                # Pydantic validation models
├── tdee.py                  # Mifflin-St Jeor TDEE + macro calculator
├── requirements.txt         # Python dependencies
├── README.md
│
├── templates/
│   ├── base.html            # Base layout: PWA meta, fonts, Tailwind config
│   ├── index.html           # SPA shell: all 4 tabs, bottom nav, modals, JS
│   ├── login.html           # Login form
│   ├── signup.html          # Registration form
│   ├── onboarding.html      # Profile setup with TDEE (age/gender/height/weight/activity/goal)
│   └── partials/
│       ├── dashboard_content.html   # Daily ring, 3 metric cards, week chart, meal accordion
│       ├── activity_content.html    # Date picker, day detail, stats, intake + burned charts
│       ├── training_content.html    # Muscle filter, exercise grid, workout accordion
│       ├── day_detail.html          # Meals + workouts for a specific date
│       ├── food_results.html        # Food search results (compact card / dropdown)
│       ├── reminders_list.html      # Reminder rows with time picker + toggle
│       └── note_input.html          # Workout planner textarea + save
│
└── static/
    ├── css/
    │   └── style.css        # Complete brutalist stylesheet (15 easing vars, 15+ keyframes, 60+ selectors)
    ├── logo.svg             # CT monogram logo + apple-touch-icon
    ├── favicon.svg          # SVG favicon
    ├── manifest.json        # PWA manifest
    ├── sw.js                # Service worker (cache-first)
    └── uploads/             # Avatar images
```

## Design System

### New Brutalism — Rules
| Property | Value |
|---|---|
| Background | `#080808` (page), `#1A1A1A` (cards) |
| Borders | `2px solid #2A2A2A`, **zero** border-radius |
| Accent | `#FF6B3D` (flat orange, no gradient) |
| Shadows | **None** — flat design |
| Blur/Glass | **None** — no backdrop-filter |
| Border radius | **Zero** everywhere |

### Color Palette
```
Brand:   #FF6B3D (default), #D85A30 (dark), #2A1812 (bg)
Green:   #2ECC71 (default), #1EA85E (dark), #122A1A (bg)
Gold:    #F0B429 (default), #D49525 (dark), #2A2210 (bg)
Purple:  #A78BFA (default), #8B6FE8 (dark), #1E1A2E (bg)
Surface: #141414, #1A1A1A (card), #222222 (hover), #2A2A2A (border)
Gray:    50→900 (#141414 → #F5F5F5)
```

### Typography
- **Font**: Urbanist (sans-serif, 300–800 weight)
- **Scale**: `[9px]` labels → `[26px]` headings → `56px` ring percentage
- **Style**: Uppercase tracking-wider labels, font-black for emphasis

### Bottom Navigation
- **Fixed** at bottom center (88% width, max 360px, `margin: 0 auto`)
- **5 items**: Home · Activity · **+** · Training · Profile
- **+ button**: 44×44 orange square, center position
- **Active state**: Solid orange 44×44 square behind icon
- **Icons**: Y2K-style chunky SVGs (`stroke-width: 3`)

### Animations
- 15+ CSS keyframes with spring/expo easing variables
- Staggered card entrances (`.stagger-cards`, `.profile-stat`, `.settings-row`)
- Smooth tab transitions (slide, fade)
- Hover lifts, active press scales, accordion rotates

## PWA Details

| Feature | Implementation |
|---|---|
| Manifest | SVG icon, dark colors, standalone display |
| Service Worker | Cache-first for `/`, CSS, manifest |
| iOS Support | `apple-mobile-web-app-capable`, `black-translucent` status bar |
| Notch | `viewport-fit=cover`, `env(safe-area-inset-bottom)` |
| Theme Color | `#080808` |
| Orientation | `portrait` locked |

## TDEE Calculation

Based on the **Mifflin-St Jeor** equation:

```
Male:   BMR = 10 × weight_kg + 6.25 × height_cm - 5 × age + 5
Female: BMR = 10 × weight_kg + 6.25 × height_cm - 5 × age - 161
```

| Activity Level | Multiplier |
|---|---|
| Sedentary (desk job, no exercise) | ×1.2 |
| Light (1–3 days/week) | ×1.375 |
| Moderate (3–5 days/week) | ×1.55 |
| Active (6–7 days/week) | ×1.725 |
| Very Active (daily + physical job) | ×1.9 |

| Goal | Adjustment |
|---|---|
| Lose weight | ×0.8 |
| Maintain | ×1.0 |
| Gain weight | ×1.15 |

**Macro split**: Protein 30% (4 cal/g), Carbs 40% (4 cal/g), Fat 30% (9 cal/g)

## Development

```bash
# Install
pip install -r requirements.txt

# Run with hot reload
python -m uvicorn main:app --reload --port 8000

# Delete database to reset (will be recreated with seed data)
del calories.db
```

### Adding to Home Screen
- **iOS**: Safari → Share → Add to Home Screen
- **Android**: Chrome → Menu → Add to Home Screen

### Important Notes
- First-time setup: run the app, sign up, complete onboarding — TDEE and goals are auto-calculated
- Deleting `calories.db` is required to pick up new table columns after migrations
- All training HTMX calls target `#training-root` with `outerHTML` swap
- Dashboard auto-refreshes after any workout change via HTMX event listener
- The bottom nav is placed **outside** the `max-w-md` container in HTML to prevent layout shift

## Credits

Built by **Theo**. Free for everyone.
Instagram: [@theodoesgame](https://www.instagram.com/theodoesgame/)

