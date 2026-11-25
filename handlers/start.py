import html
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from services.db import add_user, get_users_count

router = Router()

def get_main_keyboard():
    keyboard = [
        [
            KeyboardButton(text="⚽ DLS Karta Yasash"),
            KeyboardButton(text="📖 Ismlar Ma'nosi")
        ],
        [
            KeyboardButton(text="🎬 Tabrik Video Yasash"),
            KeyboardButton(text="🖼️ Orqa Fon Olish")
        ],
        [
            KeyboardButton(text="ℹ️ Bot Haqida")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

@router.message(CommandStart())
@router.message(F.text == "/")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    # Foydalanuvchini bazaga qo'shish (faqat 1 marta yoziladi, 1 akkount = 1)
    if message.from_user:
        add_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
    
    safe_name = html.escape(message.from_user.full_name or "Foydalanuvchi")
    welcome_text = (
        f"Assalomu alaykum, <b>{safe_name}</b>!\n\n"
        f"🤖 <b>Universal Multi-Funksional Botimizga xush kelibsiz!</b>\n\n"
        f"Kerakli xizmatlardan birini tanlang:\n"
        f"▫️ ⚽ <b>DLS Karta Yasash</b> – Haqiqiy DLS uslubidagi afsonaviy futbolchi kartasini yasang.\n"
        f"▫️ 📖 <b>Ismlar Ma'nosi</b> – Dunyodagi barcha ismlarning rasmiy va to'liq ma'nosini bilib oling.\n"
        f"▫️ 🎬 <b>Tabrik Video Yasash</b> – Ovozli, musiqali va fotosuratli maxsus bayram videolari yarating.\n"
        f"▫️ 🖼️ <b>Orqa Fon Olish</b> – Har qanday rasmning orqa fonini tozalab, shaffof PNG stikerga aylantiring.\n\n"
        f"<i>Quyidagi tugmalardan birini bosing:</i> 👇"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

@router.message(F.text == "🔙 Asosiy Menyu")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Siz asosiy menyudasiz. Kerakli bo'limni tanlang:", reply_markup=get_main_keyboard())

@router.message(Command("about"))
@router.message(F.text.lower().contains("bot haqida") | (F.text == "ℹ️ Bot Haqida"))
async def about_bot(message: Message):
    # Har qanday holatda foydalanuvchini bazaga kiritib qo'yish
    if message.from_user:
        add_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
        
    total_users = get_users_count()
    
    about_text = (
        "ℹ️ <b>Bot haqida ma'lumot:</b>\n\n"
        f"📊 <b>Foydalanuvchilar statistikasi:</b>\n"
        f"👥 <b>Jami foydalanuvchilar soni:</b> <code>{total_users}</code> ta\n"
        f"<i>(Har bir Telegram akkaunt faqat 1 marta hisoblanadi. Botni o'chirib qayta start bosilsa ham hisob 1 tadan oshmaydi)</i>\n\n"
        "Ushbu bot bitta joyda 4 ta kuchli xizmatni birlashtiradi:\n"
        "1. <b>DLS Karta Generator</b> - DLS 24/25 o'yinidagi barcha 14 xil fon bilan Casillas kartasi uslubida karta yaratish.\n"
        "2. <b>Ismlar ensiklopediyasi</b> - Ismlar.com va akademik lug'atlar orqali ismlar ma'nosi.\n"
        "3. <b>Tabrik Video Maker</b> - Musiqali va fotosuratli tantanali tabrik videoroliklar.\n"
        "4. <b>Orqa Fon Tozalash (Remove BG)</b> - Rasm orqa fonini qirqib olish va shaffof PNG qilish.\n\n"
        "⚡ <i>Tezkor, sifatli va doimiy yangilanib boruvchi universal bot.</i>"
    )
    await message.answer(about_text, parse_mode="HTML")
