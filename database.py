import aiosqlite

DB_PATH = "calories.db"

FOODS_SEED = [
    ("Apple", 95, 0.5, 25, 0.3),
    ("Banana", 105, 1.3, 27, 0.4),
    ("Orange", 62, 1.2, 15, 0.2),
    ("Strawberries (100g)", 32, 0.7, 8, 0.3),
    ("Blueberries (100g)", 57, 0.7, 14, 0.3),
    ("Grapes (100g)", 69, 0.7, 18, 0.2),
    ("Watermelon (100g)", 30, 0.6, 8, 0.2),
    ("Mango", 202, 2.8, 50, 0.8),
    ("Pineapple (100g)", 50, 0.5, 13, 0.1),
    ("Avocado", 240, 3, 12.8, 22),
    ("Chicken Breast (100g)", 165, 31, 0, 3.6),
    ("Chicken Thigh (100g)", 209, 26, 0, 11),
    ("Ground Beef 80/20 (100g)", 254, 17, 0, 20),
    ("Ground Beef 93/7 (100g)", 176, 21, 0, 10),
    ("Salmon (100g)", 208, 20, 0, 13),
    ("Tuna Canned (100g)", 132, 29, 0, 0.8),
    ("Shrimp (100g)", 99, 21, 0, 1.4),
    ("Egg (1 large)", 78, 6, 0.6, 5),
    ("Egg Whites (100g)", 52, 11, 0.7, 0.2),
    ("Milk Whole (1 cup)", 149, 8, 12, 8),
    ("Milk 2% (1 cup)", 122, 8, 12, 5),
    ("Greek Yogurt Plain (200g)", 146, 20, 8, 4),
    ("Cheddar Cheese (30g)", 120, 7, 0.4, 10),
    ("Cottage Cheese (100g)", 98, 11, 3.4, 4.3),
    ("White Rice Cooked (1 cup)", 206, 4.3, 45, 0.4),
    ("Brown Rice Cooked (1 cup)", 218, 5, 46, 1.6),
    ("Pasta Cooked (1 cup)", 220, 8, 43, 1.3),
    ("White Bread (1 slice)", 79, 2.5, 15, 0.9),
    ("Whole Wheat Bread (1 slice)", 81, 4, 14, 1.1),
    ("Oatmeal Cooked (1 cup)", 154, 5.4, 27, 2.6),
    ("Quinoa Cooked (1 cup)", 222, 8, 39, 3.6),
    ("Potato Baked (medium)", 161, 4.3, 37, 0.2),
    ("Sweet Potato Baked (medium)", 103, 2.3, 24, 0.2),
    ("Broccoli (100g)", 34, 2.8, 7, 0.4),
    ("Spinach (100g)", 23, 2.9, 3.6, 0.4),
    ("Kale (100g)", 49, 4.3, 9, 0.9),
    ("Carrot (medium)", 25, 0.6, 6, 0.1),
    ("Tomato (medium)", 22, 1.1, 4.8, 0.2),
    ("Bell Pepper (medium)", 31, 1, 7, 0.3),
    ("Cucumber (100g)", 15, 0.7, 3.6, 0.1),
    ("Lettuce (100g)", 5, 0.5, 1, 0.1),
    ("Onion (medium)", 44, 1.2, 10, 0.1),
    ("Garlic (1 clove)", 4, 0.2, 1, 0),
    ("Mushrooms (100g)", 22, 3.1, 3.3, 0.3),
    ("Almonds (30g)", 173, 6, 6, 15),
    ("Walnuts (30g)", 185, 4.3, 3.9, 18.5),
    ("Peanuts (30g)", 166, 7.5, 4.6, 14),
    ("Cashews (30g)", 163, 5.2, 9, 13),
    ("Peanut Butter (2 tbsp)", 188, 8, 6, 16),
    ("Olive Oil (1 tbsp)", 119, 0, 0, 13.5),
    ("Butter (1 tbsp)", 102, 0.1, 0, 11.5),
    ("Hummus (100g)", 166, 7.9, 14, 10),
    ("Black Beans Cooked (1 cup)", 227, 15, 41, 0.9),
    ("Lentils Cooked (1 cup)", 230, 18, 40, 0.8),
    ("Chickpeas Cooked (1 cup)", 269, 14.5, 45, 4.3),
    ("Tofu Firm (100g)", 76, 8, 1.9, 4.8),
    ("Edamame (100g)", 122, 11, 9, 5),
    ("Pizza Cheese Slice", 285, 12, 36, 10),
    ("Hamburger (single patty)", 354, 16, 25, 20),
    ("Hot Dog", 290, 11, 18, 19),
    ("French Fries medium", 365, 3.4, 39, 22),
    ("Nachos (100g)", 306, 7, 34, 17),
    ("Tacos (2 tacos)", 312, 16, 26, 17),
    ("Sushi Roll (6 pcs)", 250, 9, 38, 7),
    ("Ramen Noodles Packaged", 380, 8, 54, 14),
    ("Burrito", 450, 18, 50, 18),
    ("Sandwich Turkey", 290, 18, 33, 9),
    ("Caesar Salad", 330, 7, 14, 28),
    ("Greek Salad", 240, 6, 11, 19),
    ("Apple Juice (1 cup)", 114, 0.2, 28, 0.3),
    ("Orange Juice (1 cup)", 112, 1.7, 26, 0.5),
    ("Coffee Black", 2, 0.1, 0, 0),
    ("Coffee with Milk (1 cup)", 30, 1.5, 3, 1.5),
    ("Green Tea", 2, 0, 0, 0),
    ("Soda Can (12oz)", 140, 0, 39, 0),
    ("Diet Soda Can", 0, 0, 0, 0),
    ("Beer Regular (12oz)", 153, 1.6, 13, 0),
    ("Wine Red (5oz)", 125, 0.1, 4, 0),
    ("Chocolate Bar Milk", 250, 3, 28, 14),
    ("Chocolate Dark (30g)", 170, 2, 13, 12),
    ("Ice Cream Vanilla (1 cup)", 273, 4.6, 31, 15),
    ("Cookies Chocolate Chip (2)", 160, 2, 22, 8),
    ("Brownie", 230, 3, 30, 12),
    ("Cake Vanilla Slice", 260, 2, 35, 13),
    ("Donut Glazed", 260, 3.5, 30, 15),
    ("Granola Bar", 140, 3, 22, 5),
    ("Protein Bar", 250, 20, 30, 8),
    ("Trail Mix (100g)", 462, 15, 43, 29),
    ("Bacon (2 slices)", 86, 6, 0.2, 6.7),
    ("Sausage Link", 170, 7, 2, 15),
    ("Ham Sliced (30g)", 40, 6, 0.5, 1.5),
    ("Turkey Breast Sliced (30g)", 30, 5, 0.3, 0.6),
    ("Tuna Salad (100g)", 190, 16, 5, 12),
    ("Chicken Salad (100g)", 180, 18, 4, 10),
    ("Egg Salad (100g)", 220, 11, 2, 18),
]


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
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            calories REAL NOT NULL,
            protein REAL DEFAULT 0,
            carbs REAL DEFAULT 0,
            fat REAL DEFAULT 0
        );
        INSERT OR IGNORE INTO goals (id) VALUES (1);
    """)
    await db.commit()
    count = await db.execute_fetchall("SELECT COUNT(*) as cnt FROM foods")
    if count[0]["cnt"] == 0:
        for name, cal, pro, carb, fat in FOODS_SEED:
            await db.execute(
                "INSERT OR IGNORE INTO foods (name, calories, protein, carbs, fat) VALUES (?, ?, ?, ?, ?)",
                (name, cal, pro, carb, fat),
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
