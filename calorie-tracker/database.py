import secrets
import aiosqlite
from passlib.hash import bcrypt

DB_PATH = "calories.db"

FOODS_SEED = [
    ("Apple", 95, 0.5, 25, 0.3, 182, "piece"),
    ("Banana", 105, 1.3, 27, 0.4, 118, "piece"),
    ("Orange", 62, 1.2, 15, 0.2, 131, "piece"),
    ("Strawberries (100g)", 32, 0.7, 8, 0.3, 100, "g"),
    ("Blueberries (100g)", 57, 0.7, 14, 0.3, 100, "g"),
    ("Grapes (100g)", 69, 0.7, 18, 0.2, 100, "g"),
    ("Watermelon (100g)", 30, 0.6, 8, 0.2, 100, "g"),
    ("Mango", 202, 2.8, 50, 0.8, 336, "piece"),
    ("Pineapple (100g)", 50, 0.5, 13, 0.1, 100, "g"),
    ("Avocado", 240, 3, 12.8, 22, 201, "piece"),
    ("Chicken Breast (100g)", 165, 31, 0, 3.6, 100, "g"),
    ("Chicken Thigh (100g)", 209, 26, 0, 11, 100, "g"),
    ("Ground Beef 80/20 (100g)", 254, 17, 0, 20, 100, "g"),
    ("Ground Beef 93/7 (100g)", 176, 21, 0, 10, 100, "g"),
    ("Salmon (100g)", 208, 20, 0, 13, 100, "g"),
    ("Tuna Canned (100g)", 132, 29, 0, 0.8, 100, "g"),
    ("Shrimp (100g)", 99, 21, 0, 1.4, 100, "g"),
    ("Egg (1 large)", 78, 6, 0.6, 5, 50, "piece"),
    ("Egg Whites (100g)", 52, 11, 0.7, 0.2, 100, "g"),
    ("Milk Whole (1 cup)", 149, 8, 12, 8, 244, "cup"),
    ("Milk 2% (1 cup)", 122, 8, 12, 5, 244, "cup"),
    ("Greek Yogurt Plain (200g)", 146, 20, 8, 4, 200, "g"),
    ("Cheddar Cheese (30g)", 120, 7, 0.4, 10, 30, "g"),
    ("Cottage Cheese (100g)", 98, 11, 3.4, 4.3, 100, "g"),
    ("White Rice Cooked (1 cup)", 206, 4.3, 45, 0.4, 200, "cup"),
    ("Brown Rice Cooked (1 cup)", 218, 5, 46, 1.6, 200, "cup"),
    ("Pasta Cooked (1 cup)", 220, 8, 43, 1.3, 200, "cup"),
    ("White Bread (1 slice)", 79, 2.5, 15, 0.9, 30, "slice"),
    ("Whole Wheat Bread (1 slice)", 81, 4, 14, 1.1, 30, "slice"),
    ("Oatmeal Cooked (1 cup)", 154, 5.4, 27, 2.6, 234, "cup"),
    ("Quinoa Cooked (1 cup)", 222, 8, 39, 3.6, 185, "cup"),
    ("Potato Baked (medium)", 161, 4.3, 37, 0.2, 173, "piece"),
    ("Sweet Potato Baked (medium)", 103, 2.3, 24, 0.2, 114, "piece"),
    ("Broccoli (100g)", 34, 2.8, 7, 0.4, 100, "g"),
    ("Spinach (100g)", 23, 2.9, 3.6, 0.4, 100, "g"),
    ("Kale (100g)", 49, 4.3, 9, 0.9, 100, "g"),
    ("Carrot (medium)", 25, 0.6, 6, 0.1, 61, "piece"),
    ("Tomato (medium)", 22, 1.1, 4.8, 0.2, 123, "piece"),
    ("Bell Pepper (medium)", 31, 1, 7, 0.3, 119, "piece"),
    ("Cucumber (100g)", 15, 0.7, 3.6, 0.1, 100, "g"),
    ("Lettuce (100g)", 5, 0.5, 1, 0.1, 100, "g"),
    ("Onion (medium)", 44, 1.2, 10, 0.1, 110, "piece"),
    ("Garlic (1 clove)", 4, 0.2, 1, 0, 3, "piece"),
    ("Mushrooms (100g)", 22, 3.1, 3.3, 0.3, 100, "g"),
    ("Almonds (30g)", 173, 6, 6, 15, 30, "g"),
    ("Walnuts (30g)", 185, 4.3, 3.9, 18.5, 30, "g"),
    ("Peanuts (30g)", 166, 7.5, 4.6, 14, 30, "g"),
    ("Cashews (30g)", 163, 5.2, 9, 13, 30, "g"),
    ("Peanut Butter (2 tbsp)", 188, 8, 6, 16, 32, "tbsp"),
    ("Olive Oil (1 tbsp)", 119, 0, 0, 13.5, 15, "tbsp"),
    ("Butter (1 tbsp)", 102, 0.1, 0, 11.5, 14, "tbsp"),
    ("Hummus (100g)", 166, 7.9, 14, 10, 100, "g"),
    ("Black Beans Cooked (1 cup)", 227, 15, 41, 0.9, 200, "cup"),
    ("Lentils Cooked (1 cup)", 230, 18, 40, 0.8, 200, "cup"),
    ("Chickpeas Cooked (1 cup)", 269, 14.5, 45, 4.3, 200, "cup"),
    ("Tofu Firm (100g)", 76, 8, 1.9, 4.8, 100, "g"),
    ("Edamame (100g)", 122, 11, 9, 5, 100, "g"),
    ("Pizza Cheese Slice", 285, 12, 36, 10, 107, "slice"),
    ("Hamburger (single patty)", 354, 16, 25, 20, 180, "piece"),
    ("Hot Dog", 290, 11, 18, 19, 98, "piece"),
    ("French Fries medium", 365, 3.4, 39, 22, 150, "serving"),
    ("Nachos (100g)", 306, 7, 34, 17, 100, "g"),
    ("Tacos (2 tacos)", 312, 16, 26, 17, 200, "serving"),
    ("Sushi Roll (6 pcs)", 250, 9, 38, 7, 200, "serving"),
    ("Ramen Noodles Packaged", 380, 8, 54, 14, 85, "package"),
    ("Burrito", 450, 18, 50, 18, 350, "piece"),
    ("Sandwich Turkey", 290, 18, 33, 9, 200, "piece"),
    ("Caesar Salad", 330, 7, 14, 28, 250, "serving"),
    ("Greek Salad", 240, 6, 11, 19, 250, "serving"),
    ("Apple Juice (1 cup)", 114, 0.2, 28, 0.3, 240, "cup"),
    ("Orange Juice (1 cup)", 112, 1.7, 26, 0.5, 240, "cup"),
    ("Coffee Black", 2, 0.1, 0, 0, 240, "cup"),
    ("Coffee with Milk (1 cup)", 30, 1.5, 3, 1.5, 240, "cup"),
    ("Green Tea", 2, 0, 0, 0, 240, "cup"),
    ("Soda Can (12oz)", 140, 0, 39, 0, 355, "can"),
    ("Diet Soda Can", 0, 0, 0, 0, 355, "can"),
    ("Beer Regular (12oz)", 153, 1.6, 13, 0, 355, "bottle"),
    ("Wine Red (5oz)", 125, 0.1, 4, 0, 148, "glass"),
    ("Chocolate Bar Milk", 250, 3, 28, 14, 50, "bar"),
    ("Chocolate Dark (30g)", 170, 2, 13, 12, 30, "g"),
    ("Ice Cream Vanilla (1 cup)", 273, 4.6, 31, 15, 200, "cup"),
    ("Cookies Chocolate Chip (2)", 160, 2, 22, 8, 30, "serving"),
    ("Brownie", 230, 3, 30, 12, 70, "piece"),
    ("Cake Vanilla Slice", 260, 2, 35, 13, 100, "slice"),
    ("Donut Glazed", 260, 3.5, 30, 15, 85, "piece"),
    ("Granola Bar", 140, 3, 22, 5, 35, "bar"),
    ("Protein Bar", 250, 20, 30, 8, 70, "bar"),
    ("Trail Mix (100g)", 462, 15, 43, 29, 100, "g"),
    ("Bacon (2 slices)", 86, 6, 0.2, 6.7, 20, "serving"),
    ("Sausage Link", 170, 7, 2, 15, 75, "piece"),
    ("Ham Sliced (30g)", 40, 6, 0.5, 1.5, 30, "g"),
    ("Turkey Breast Sliced (30g)", 30, 5, 0.3, 0.6, 30, "g"),
    ("Tuna Salad (100g)", 190, 16, 5, 12, 100, "g"),
    ("Chicken Salad (100g)", 180, 18, 4, 10, 100, "g"),
    ("Egg Salad (100g)", 220, 11, 2, 18, 100, "g"),
]


SERVING_SIZES = [
    # (unit, grams)
    ("g (100g)", 100),
    ("cup (240ml)", 240),
    ("piece", 0),
    ("slice", 0),
    ("tbsp (15ml)", 15),
    ("tsp (5ml)", 5),
    ("oz (28g)", 28),
    ("serving", 0),
]


async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    return db


async def init_db():
    db = await get_db()
    await db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            calories REAL NOT NULL,
            protein REAL DEFAULT 0,
            carbs REAL DEFAULT 0,
            fat REAL DEFAULT 0,
            meal_type TEXT DEFAULT 'snack',
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            calorie_target REAL DEFAULT 2000,
            protein_target REAL DEFAULT 50,
            carbs_target REAL DEFAULT 250,
            fat_target REAL DEFAULT 65,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            calories REAL NOT NULL,
            protein REAL DEFAULT 0,
            carbs REAL DEFAULT 0,
            fat REAL DEFAULT 0,
            serving_size_g REAL DEFAULT 100,
            serving_unit TEXT DEFAULT 'g'
        );
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            age INTEGER DEFAULT 30,
            weight REAL DEFAULT 70,
            height REAL DEFAULT 170,
            gender TEXT DEFAULT 'male',
            activity_level TEXT DEFAULT 'moderate',
            goal_type TEXT DEFAULT 'maintain',
            tdee REAL DEFAULT 2000,
            onboarded INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS favourite_foods (
            user_id INTEGER NOT NULL,
            food_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, food_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (food_id) REFERENCES foods(id)
        );
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            meal_type TEXT NOT NULL,
            label TEXT NOT NULL,
            time TEXT NOT NULL DEFAULT '12:00',
            enabled INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    await db.commit()

    # Migrate: add serving columns if they don't exist
    try:
        await db.execute("ALTER TABLE foods ADD COLUMN serving_size_g REAL DEFAULT 100")
        await db.commit()
    except Exception:
        pass
    try:
        await db.execute("ALTER TABLE foods ADD COLUMN serving_unit TEXT DEFAULT 'g'")
        await db.commit()
    except Exception:
        pass
    try:
        await db.execute("ALTER TABLE user_profile ADD COLUMN tdee REAL DEFAULT 2000")
        await db.commit()
    except Exception:
        pass
    try:
        await db.execute("ALTER TABLE user_profile ADD COLUMN onboarded INTEGER DEFAULT 0")
        await db.commit()
    except Exception:
        pass
    try:
        await db.execute("ALTER TABLE user_profile ADD COLUMN avatar_url TEXT DEFAULT NULL")
        await db.commit()
    except Exception:
        pass

    # Seed default reminders for all users (ensures each user has all types)
    reminder_defaults = [
        ("breakfast", "☀️ Breakfast", "08:00"),
        ("lunch", "🌿 Lunch", "12:30"),
        ("dinner", "🌙 Dinner", "19:00"),
        ("snack", "🍪 Snack", "15:30"),
        ("general", "📝 Log meals", "20:00"),
        ("water", "💧 Drink water", "10:00"),
    ]
    all_users = await db.execute_fetchall("SELECT id FROM users")
    for u in all_users:
        existing_types = {
            r["meal_type"]
            for r in await db.execute_fetchall(
                "SELECT meal_type FROM reminders WHERE user_id = ?", (u["id"],)
            )
        }
        for mt, label, t in reminder_defaults:
            if mt not in existing_types:
                await db.execute(
                    "INSERT INTO reminders (user_id, meal_type, label, time, enabled) VALUES (?, ?, ?, ?, 1)",
                    (u["id"], mt, label, t),
                )
    await db.commit()

    # Seed foods
    count = await db.execute_fetchall("SELECT COUNT(*) as cnt FROM foods")
    if count[0]["cnt"] == 0:
        for row in FOODS_SEED:
            name, cal, pro, carb, fat, *extra = row
            sg = extra[0] if extra else 100
            su = extra[1] if len(extra) > 1 else "g"
            await db.execute(
                "INSERT OR IGNORE INTO foods (name, calories, protein, carbs, fat, serving_size_g, serving_unit) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (name, cal, pro, carb, fat, sg, su),
            )
        await db.commit()
    else:
        # Update existing foods that have NULL serving columns
        await db.execute("UPDATE foods SET serving_size_g=100, serving_unit='g' WHERE serving_size_g IS NULL")
        await db.commit()

    await db.close()


async def get_food_by_id(food_id: int) -> dict | None:
    db = await get_db()
    row = await db.execute_fetchall("SELECT * FROM foods WHERE id = ?", (food_id,))
    await db.close()
    return dict(row[0]) if row else None


async def create_user(username: str, password: str) -> dict | None:
    db = await get_db()
    existing = await db.execute_fetchall("SELECT id FROM users WHERE username = ?", (username,))
    if existing:
        await db.close()
        return None
    pw_hash = bcrypt.hash(password)
    await db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pw_hash))
    await db.commit()
    row = await db.execute_fetchall("SELECT id, username FROM users WHERE username = ?", (username,))
    await db.close()
    return dict(row[0]) if row else None


async def authenticate_user(username: str, password: str) -> dict | None:
    db = await get_db()
    row = await db.execute_fetchall("SELECT * FROM users WHERE username = ?", (username,))
    if not row:
        await db.close()
        return None
    user = dict(row[0])
    if not bcrypt.verify(password, user["password_hash"]):
        await db.close()
        return None
    await db.close()
    return user


async def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    db = await get_db()
    await db.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
    await db.commit()
    await db.close()
    return token


async def get_user_by_token(token: str) -> dict | None:
    db = await get_db()
    row = await db.execute_fetchall(
        "SELECT u.id, u.username FROM sessions s JOIN users u ON s.user_id = u.id WHERE s.token = ?",
        (token,),
    )
    await db.close()
    return dict(row[0]) if row else None


async def delete_session(token: str):
    db = await get_db()
    await db.execute("DELETE FROM sessions WHERE token = ?", (token,))
    await db.commit()
    await db.close()


async def get_or_create_goals(user_id: int) -> dict:
    db = await get_db()
    row = await db.execute_fetchall("SELECT * FROM goals WHERE user_id = ?", (user_id,))
    if row:
        await db.close()
        return dict(row[0])
    await db.execute("INSERT INTO goals (user_id) VALUES (?)", (user_id,))
    await db.commit()
    row = await db.execute_fetchall("SELECT * FROM goals WHERE user_id = ?", (user_id,))
    await db.close()
    return dict(row[0])


async def update_goals(user_id: int, calorie_target: float, protein_target: float, carbs_target: float, fat_target: float):
    db = await get_db()
    await db.execute(
        "UPDATE goals SET calorie_target=?, protein_target=?, carbs_target=?, fat_target=? WHERE user_id=?",
        (calorie_target, protein_target, carbs_target, fat_target, user_id),
    )
    await db.commit()
    await db.close()


async def search_foods(q: str, limit: int = 8):
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT * FROM foods WHERE name LIKE ? ORDER BY name LIMIT ?",
        (f"%{q}%", limit),
    )
    await db.close()
    return [dict(r) for r in rows]


async def update_profile_avatar(user_id: int, avatar_url: str):
    db = await get_db()
    await db.execute("UPDATE user_profile SET avatar_url = ? WHERE user_id = ?", (avatar_url, user_id))
    await db.commit()
    await db.close()


async def create_profile(user_id: int, age: int, weight: float, height: float, gender: str, activity_level: str, goal_type: str):
    db = await get_db()
    await db.execute(
        "INSERT OR REPLACE INTO user_profile (user_id, age, weight, height, gender, activity_level, goal_type, onboarded) VALUES (?, ?, ?, ?, ?, ?, ?, 1)",
        (user_id, age, weight, height, gender, activity_level, goal_type),
    )
    await db.commit()
    await db.close()


async def get_profile(user_id: int) -> dict | None:
    db = await get_db()
    row = await db.execute_fetchall("SELECT * FROM user_profile WHERE user_id = ?", (user_id,))
    await db.close()
    return dict(row[0]) if row else None


async def add_favourite_food(user_id: int, food_id: int):
    db = await get_db()
    await db.execute(
        "INSERT OR IGNORE INTO favourite_foods (user_id, food_id) VALUES (?, ?)",
        (user_id, food_id),
    )
    await db.commit()
    await db.close()


async def remove_favourite_food(user_id: int, food_id: int):
    db = await get_db()
    await db.execute(
        "DELETE FROM favourite_foods WHERE user_id = ? AND food_id = ?",
        (user_id, food_id),
    )
    await db.commit()
    await db.close()


async def get_favourite_foods(user_id: int, limit: int = 5) -> list[dict]:
    db = await get_db()
    rows = await db.execute_fetchall(
        """SELECT f.*, ff.created_at as faved_at
           FROM favourite_foods ff JOIN foods f ON ff.food_id = f.id
           WHERE ff.user_id = ?
           ORDER BY ff.created_at DESC LIMIT ?""",
        (user_id, limit),
    )
    await db.close()
    return [dict(r) for r in rows]


async def is_favourite(user_id: int, food_id: int) -> bool:
    db = await get_db()
    row = await db.execute_fetchall(
        "SELECT 1 FROM favourite_foods WHERE user_id = ? AND food_id = ?",
        (user_id, food_id),
    )
    await db.close()
    return len(row) > 0


async def get_reminders(user_id: int) -> list[dict]:
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT * FROM reminders WHERE user_id = ? ORDER BY id", (user_id,)
    )
    await db.close()
    return [dict(r) for r in rows]


async def save_reminder(reminder_id: int, user_id: int, time: str, enabled: int):
    db = await get_db()
    await db.execute(
        "UPDATE reminders SET time = ?, enabled = ? WHERE id = ? AND user_id = ?",
        (time, enabled, reminder_id, user_id),
    )
    await db.commit()
    await db.close()


async def get_recent_foods(user_id: int, limit: int = 5) -> list[dict]:
    db = await get_db()
    rows = await db.execute_fetchall(
        """SELECT f.*, MAX(m.created_at) as last_used
           FROM meals m JOIN foods f ON m.name = f.name
           WHERE m.user_id = ?
           GROUP BY f.id
           ORDER BY last_used DESC LIMIT ?""",
        (user_id, limit),
    )
    await db.close()
    return [dict(r) for r in rows]
