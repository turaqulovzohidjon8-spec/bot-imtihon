import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Bot Token (agar .env da bo'lmasa, shu yerga yozish mumkin)
BOT_TOKEN = os.getenv("BOT_TOKEN") or "8867474269:AAHPNSCv8gn4WFKzIE6KtsXC2OxUfa7nuWc"

# Papkalar
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
TEMPLATES_DIR = ASSETS_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"

# Output papkasini tekshirish
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

