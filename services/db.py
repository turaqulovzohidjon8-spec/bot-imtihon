import sqlite3
from pathlib import Path
from config import BASE_DIR

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "users.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def add_user(user_id: int, username: str = None, full_name: str = None) -> bool:
    """
    Yangi foydalanuvchini bazaga qo'shish.
    Agar akkaunt allaqachon mavjud bo'lsa, qayta qo'shilmaydi (1 ta Telegram akkount = 1).
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO users (user_id, username, full_name)
                VALUES (?, ?, ?)
            """, (user_id, username, full_name))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Baza xatoligi (add_user): {e}")
        return False

def get_users_count() -> int:
    """Noyob (unikal) foydalanuvchilarning umumiy soni"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(DISTINCT user_id) FROM users")
            row = cursor.fetchone()
            return row[0] if row else 0
    except Exception as e:
        print(f"Baza xatoligi (get_users_count): {e}")
        return 0

# Modul yuklanganda bazani avtomatik ishga tushirish
init_db()

