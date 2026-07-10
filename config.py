import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip().strip('"').strip("'")
OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip().strip('"').strip("'")
OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-4o-mini").strip()
TIMEZONE = (os.getenv("TIMEZONE") or "Europe/Moscow").strip()
DB_PATH = os.getenv("DB_PATH", "nutrivision.db")
