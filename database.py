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

def today_food(user_id: int):
    day = date.today().isoformat()
    with connect() as db:
        rows = db.execute("""
            SELECT * FROM food_entries
            WHERE telegram_id=? AND substr(created_at,1,10)=?
            ORDER BY created_at ASC
        """, (user_id, day)).fetchall()
        return [dict(r) for r in rows]

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
                   ROUND(SUM(protein_g)) AS protein_g
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
