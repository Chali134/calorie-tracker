# Calorie Tracker

A clean, immersive calorie tracking web app built with **FastAPI**, **HTMX**, and **Tailwind CSS**. Works as a **Progressive Web App** on iOS and Android.

## Features

- **Daily dashboard** — animated progress ring, macro breakdown
- **Add meals** — bottom sheet modal with calories, protein, carbs, fat, and meal type
- **Live updates** — HTMX-powered, no page reloads
- **Macro tracking** — protein, carbs, and fat with daily goals
- **PWA ready** — add to home screen on iOS/Android via Safari/Chrome
- **Minimal design** — iOS-native feel with system fonts and smooth animations

## Quick Start

```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Open http://localhost:8000

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| Database | SQLite (via aiosqlite) |
| Templating | Jinja2 |
| Frontend | HTMX 2.0 + Tailwind CSS |
| PWA | Manifest + Service Worker |

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Dashboard |
| GET | `/meals` | Today's meals (HTMX fragment) |
| POST | `/meals` | Add a meal |
| DELETE | `/meals/{id}` | Delete a meal |

## Project Structure

```
├── main.py              # FastAPI routes
├── database.py          # SQLite setup
├── models.py            # Pydantic schemas
├── templates/
│   ├── base.html        # Base layout + PWA meta
│   ├── index.html       # Dashboard
│   └── partials/
│       └── meal_list.html  # HTMX fragment
└── static/
    ├── css/style.css
    ├── manifest.json
    └── sw.js
```
