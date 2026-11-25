import sys
import os
import asyncio

# Asosiy loyiha papkasini yo'lga qo'shish
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# main.py ni ishga tushirish
from main import main

if __name__ == "__main__":
    asyncio.run(main())

