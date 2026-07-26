import sqlite3
from datetime import datetime, date
from typing import Any
from config import DB_PATH

def connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            telegram_id INTEGER PRIMARY KEY,
            first_name TEXT,
            username TEXT,
            age INTEGER,
            gender TEXT,
            height_cm REAL,
            weight_kg REAL,
            target_weight_kg REAL,
            activity TEXT,
            goal TEXT,
            calories_target INTEGER,
            protein_target INTEGER,
            fat_target INTEGER,
            carbs_target INTEGER,
            water_target INTEGER,
            profile_completed INTEGER DEFAULT 0,
            reminders_enabled INTEGER DEFAULT 1,
            created_at TEXT,
            updated_at TEXT
        );

        CREATE TABLE IF NOT EXISTS food_entries(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            calories REAL DEFAULT 0,
            protein_g REAL DEFAULT 0,
            fat_g REAL DEFAULT 0,
            carbs_g REAL DEFAULT 0,
            source TEXT DEFAULT 'text',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS water_entries(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            amount_ml INTEGER NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS weight_entries(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            weight_kg REAL NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS achievements(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(telegram_id, code)
        );

        CREATE TABLE IF NOT EXISTS favorite_meals(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            normalized_title TEXT NOT NULL,
            title TEXT NOT NULL,
            calories REAL DEFAULT 0,
            protein_g REAL DEFAULT 0,
            fat_g REAL DEFAULT 0,
            carbs_g REAL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(telegram_id, normalized_title)
        );
        """)

def ensure_user(user_id: int, first_name: str = "", username: str = ""):
    now = datetime.now().isoformat()
    with connect() as db:
        row = db.execute("SELECT telegram_id FROM users WHERE telegram_id=?", (user_id,)).fetchone()
        if row:
            db.execute(
                "UPDATE users SET first_name=?, username=?, updated_at=? WHERE telegram_id=?",
                (first_name, username, now, user_id)
            )
        else:
            db.execute("""
                INSERT INTO users(telegram_id, first_name, username, created_at, updated_at)
                VALUES(?,?,?,?,?)
            """, (user_id, first_name, username, now, now))

def get_user(user_id: int):
    with connect() as db:
        row = db.execute("SELECT * FROM users WHERE telegram_id=?", (user_id,)).fetchone()
        return dict(row) if row else None

def update_user(user_id: int, **fields):
    if not fields:
        return

    now = datetime.now().isoformat()

    with connect() as db:
        existing = db.execute(
            "SELECT telegram_id FROM users WHERE telegram_id=?",
            (user_id,),
        ).fetchone()

        if not existing:
            db.execute(
                """
                INSERT INTO users(
                    telegram_id,
                    first_name,
                    username,
                    created_at,
                    updated_at
                )
                VALUES (?, '', '', ?, ?)
                """,
                (user_id, now, now),
            )

        fields["updated_at"] = now

        keys = list(fields.keys())
        values = [fields[key] for key in keys]
        assignments = ", ".join(f"{key}=?" for key in keys)

        db.execute(
            f"UPDATE users SET {assignments} WHERE telegram_id=?",
            (*values, user_id),
        )

def add_food(user_id: int, title: str, calories=0, protein_g=0, fat_g=0, carbs_g=0, source="text"):
    with connect() as db:
        db.execute("""
            INSERT INTO food_entries
            (telegram_id,title,calories,protein_g,fat_g,carbs_g,source,created_at)
            VALUES(?,?,?,?,?,?,?,?)
        """, (user_id, title, calories, protein_g, fat_g, carbs_g, source, datetime.now().isoformat()))

def delete_food(user_id: int, entry_id: int):
    with connect() as db:
        db.execute("DELETE FROM food_entries WHERE id=? AND telegram_id=?", (entry_id, user_id))

def get_food_entry(user_id: int, entry_id: int):
    with connect() as db:
        row = db.execute(
            "SELECT * FROM food_entries WHERE id=? AND telegram_id=?",
            (entry_id, user_id),
        ).fetchone()
        return dict(row) if row else None

def update_food_entry(
    user_id: int,
    entry_id: int,
    title: str,
    calories: float,
    protein_g: float,
    fat_g: float,
    carbs_g: float,
) -> bool:
    with connect() as db:
        cursor = db.execute(
            """
            UPDATE food_entries
            SET title=?, calories=?, protein_g=?, fat_g=?, carbs_g=?
            WHERE id=? AND telegram_id=?
            """,
            (
                title,
                float(calories or 0),
                float(protein_g or 0),
                float(fat_g or 0),
                float(carbs_g or 0),
                entry_id,
                user_id,
            ),
        )
        return cursor.rowcount == 1

def today_food(user_id: int):
    day = date.today().isoformat()
    with connect() as db:
        rows = db.execute("""
            SELECT * FROM food_entries
            WHERE telegram_id=? AND substr(created_at,1,10)=?
            ORDER BY created_at ASC
        """, (user_id, day)).fetchall()
        return [dict(r) for r in rows]

def recent_unique_foods(user_id: int, limit: int = 5):
    safe_limit = max(1, min(int(limit), 10))
    with connect() as db:
        rows = db.execute(
            """
            SELECT f.*
            FROM food_entries AS f
            INNER JOIN (
                SELECT LOWER(TRIM(title)) AS normalized_title,
                       MAX(id) AS latest_id
                FROM food_entries
                WHERE telegram_id=? AND TRIM(title) <> ''
                GROUP BY LOWER(TRIM(title))
            ) AS latest ON latest.latest_id = f.id
            WHERE f.telegram_id=?
            ORDER BY f.created_at DESC, f.id DESC
            LIMIT ?
            """,
            (user_id, user_id, safe_limit),
        ).fetchall()
        return [dict(row) for row in rows]

def _normalize_food_title(title: str) -> str:
    return " ".join(str(title or "").strip().lower().split())


def add_favorite_from_food(user_id: int, entry_id: int) -> bool:
    row = get_food_entry(user_id, entry_id)
    if not row:
        return False

    normalized_title = _normalize_food_title(row["title"])
    if not normalized_title:
        return False

    now = datetime.now().isoformat()

    with connect() as db:
        existing = db.execute(
            """
            SELECT id FROM favorite_meals
            WHERE telegram_id=? AND normalized_title=?
            """,
            (user_id, normalized_title),
        ).fetchone()

        if existing:
            db.execute(
                """
                UPDATE favorite_meals
                SET title=?, calories=?, protein_g=?, fat_g=?, carbs_g=?, updated_at=?
                WHERE id=? AND telegram_id=?
                """,
                (
                    row["title"],
                    float(row["calories"] or 0),
                    float(row["protein_g"] or 0),
                    float(row["fat_g"] or 0),
                    float(row["carbs_g"] or 0),
                    now,
                    existing["id"],
                    user_id,
                ),
            )
            return True

        db.execute(
            """
            INSERT INTO favorite_meals(
                telegram_id, normalized_title, title, calories,
                protein_g, fat_g, carbs_g, created_at, updated_at
            )
            VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (
                user_id,
                normalized_title,
                row["title"],
                float(row["calories"] or 0),
                float(row["protein_g"] or 0),
                float(row["fat_g"] or 0),
                float(row["carbs_g"] or 0),
                now,
                now,
            ),
        )
        return True


def list_favorite_meals(user_id: int, limit: int = 20):
    safe_limit = max(1, min(int(limit), 50))
    with connect() as db:
        rows = db.execute(
            """
            SELECT * FROM favorite_meals
            WHERE telegram_id=?
            ORDER BY updated_at DESC, id DESC
            LIMIT ?
            """,
            (user_id, safe_limit),
        ).fetchall()
        return [dict(row) for row in rows]


def get_favorite_meal(user_id: int, favorite_id: int):
    with connect() as db:
        row = db.execute(
            """
            SELECT * FROM favorite_meals
            WHERE id=? AND telegram_id=?
            """,
            (favorite_id, user_id),
        ).fetchone()
        return dict(row) if row else None


def delete_favorite_meal(user_id: int, favorite_id: int) -> bool:
    with connect() as db:
        cursor = db.execute(
            "DELETE FROM favorite_meals WHERE id=? AND telegram_id=?",
            (favorite_id, user_id),
        )
        return cursor.rowcount == 1


def is_food_favorite(user_id: int, entry_id: int) -> bool:
    row = get_food_entry(user_id, entry_id)
    if not row:
        return False

    normalized_title = _normalize_food_title(row["title"])
    if not normalized_title:
        return False

    with connect() as db:
        favorite = db.execute(
            """
            SELECT id FROM favorite_meals
            WHERE telegram_id=? AND normalized_title=?
            """,
            (user_id, normalized_title),
        ).fetchone()
        return favorite is not None


def toggle_favorite_for_food(user_id: int, entry_id: int) -> str | None:
    row = get_food_entry(user_id, entry_id)
    if not row:
        return None

    normalized_title = _normalize_food_title(row["title"])
    if not normalized_title:
        return None

    with connect() as db:
        favorite = db.execute(
            """
            SELECT id FROM favorite_meals
            WHERE telegram_id=? AND normalized_title=?
            """,
            (user_id, normalized_title),
        ).fetchone()

    if favorite:
        delete_favorite_meal(user_id, int(favorite["id"]))
        return "removed"

    return "added" if add_favorite_from_food(user_id, entry_id) else None


def add_water(user_id: int, amount_ml: int):
    with connect() as db:
        db.execute(
            "INSERT INTO water_entries(telegram_id,amount_ml,created_at) VALUES(?,?,?)",
            (user_id, int(amount_ml), datetime.now().isoformat())
        )

def today_water(user_id: int) -> int:
    day = date.today().isoformat()
    with connect() as db:
        row = db.execute("""
            SELECT COALESCE(SUM(amount_ml),0) AS total
            FROM water_entries
            WHERE telegram_id=? AND substr(created_at,1,10)=?
        """, (user_id, day)).fetchone()
        return int(row["total"] or 0)

def add_weight(user_id: int, weight_kg: float):
    now = datetime.now().isoformat()
    with connect() as db:
        db.execute(
            "INSERT INTO weight_entries(telegram_id,weight_kg,created_at) VALUES(?,?,?)",
            (user_id, float(weight_kg), now)
        )
        db.execute(
            "UPDATE users SET weight_kg=?, updated_at=? WHERE telegram_id=?",
            (float(weight_kg), now, user_id)
        )

def weight_history(user_id: int, limit=10):
    with connect() as db:
        rows = db.execute("""
            SELECT weight_kg, created_at FROM weight_entries
            WHERE telegram_id=?
            ORDER BY created_at DESC LIMIT ?
        """, (user_id, limit)).fetchall()
        return [dict(r) for r in rows]

def daily_summary(user_id: int) -> dict[str, Any]:
    foods = today_food(user_id)
    return {
        "calories": round(sum(float(x["calories"] or 0) for x in foods)),
        "protein_g": round(sum(float(x["protein_g"] or 0) for x in foods)),
        "fat_g": round(sum(float(x["fat_g"] or 0) for x in foods)),
        "carbs_g": round(sum(float(x["carbs_g"] or 0) for x in foods)),
        "water_ml": today_water(user_id),
        "food_count": len(foods),
    }

def day_history(user_id: int, days=7):
    with connect() as db:
        rows = db.execute("""
            SELECT substr(created_at,1,10) AS day,
                   ROUND(SUM(calories)) AS calories,
                   ROUND(SUM(protein_g)) AS protein_g,
                   ROUND(SUM(fat_g)) AS fat_g,
                   ROUND(SUM(carbs_g)) AS carbs_g,
                   COUNT(*) AS food_count
            FROM food_entries
            WHERE telegram_id=?
            GROUP BY substr(created_at,1,10)
            ORDER BY day DESC LIMIT ?
        """, (user_id, days)).fetchall()
        result = [dict(r) for r in rows]

    water_map = {}
    with connect() as db:
        rows = db.execute("""
            SELECT substr(created_at,1,10) AS day, SUM(amount_ml) AS water_ml
            FROM water_entries WHERE telegram_id=?
            GROUP BY substr(created_at,1,10)
        """, (user_id,)).fetchall()
        water_map = {r["day"]: int(r["water_ml"] or 0) for r in rows}

    for item in result:
        item["water_ml"] = water_map.get(item["day"], 0)

    return result


def weekly_history(user_id: int, days: int = 7):
    safe_days = max(1, min(int(days), 31))
    return day_history(user_id, safe_days)

def award(user_id: int, code: str, title: str) -> bool:
    try:
        with connect() as db:
            db.execute(
                "INSERT INTO achievements(telegram_id,code,title,created_at) VALUES(?,?,?,?)",
                (user_id, code, title, datetime.now().isoformat())
            )
        return True
    except sqlite3.IntegrityError:
        return False

def list_achievements(user_id: int):
    with connect() as db:
        rows = db.execute("""
            SELECT title,created_at FROM achievements
            WHERE telegram_id=? ORDER BY created_at DESC
        """, (user_id,)).fetchall()
        return [dict(r) for r in rows]
