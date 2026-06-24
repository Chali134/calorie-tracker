import aiosqlite
from datetime import date

DB_PATH = "calories.db"


async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    db = await get_db()
    await db.executescript("""
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            calories REAL NOT NULL,
            protein REAL DEFAULT 0,
            carbs REAL DEFAULT 0,
            fat REAL DEFAULT 0,
            meal_type TEXT DEFAULT 'snack',
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            calorie_target REAL DEFAULT 2000,
            protein_target REAL DEFAULT 50,
            carbs_target REAL DEFAULT 250,
            fat_target REAL DEFAULT 65
        );
        INSERT OR IGNORE INTO goals (id) VALUES (1);
    """)
    await db.commit()
    await db.close()
