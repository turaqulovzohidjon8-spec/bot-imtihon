import io
import html
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, BufferedInputFile, 
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.dls_generator import create_dls_card

router = Router()

class DLSCardStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_position = State()
    waiting_for_rating = State()
    waiting_for_theme = State()
    waiting_for_photo = State()

def get_positions_keyboard():
    buttons = [
        [InlineKeyboardButton(text="⚡ ST (Hujumchi)", callback_data="pos_ST"),
         InlineKeyboardButton(text="🎯 CAM (Hujumkor yarim)", callback_data="pos_CAM")],
        [InlineKeyboardButton(text="⚡ RW (O'ng qanot)", callback_data="pos_RW"),
         InlineKeyboardButton(text="⚡ LW (Chap qanot)", callback_data="pos_LW")],
        [InlineKeyboardButton(text="🛡️ CM (Markaziy yarim)", callback_data="pos_CM"),
         InlineKeyboardButton(text="🧱 CB (Himoyachi)", callback_data="pos_CB")],
        [InlineKeyboardButton(text="🧤 GK (Darvozabon)", callback_data="pos_GK")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_ratings_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🔥 99 (Maximal)", callback_data="rate_99"),
         InlineKeyboardButton(text="⭐ 95 (Afsona)", callback_data="rate_95")],
        [InlineKeyboardButton(text="🌟 90 (Yulduz)", callback_data="rate_90"),
         InlineKeyboardButton(text="✨ 88 (Professional)", callback_data="rate_88")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_themes_keyboard():
    """DLS o'yinidagi barcha 14 ta orqa fonlar menyusi"""
    buttons = [
        [InlineKeyboardButton(text="🌟 Oltin (Legendary)", callback_data="theme_gold"),
         InlineKeyboardButton(text="🔵 Moviy (Rare)", callback_data="theme_blue")],
        [InlineKeyboardButton(text="⚫ Qora Karbon", callback_data="theme_black"),
         InlineKeyboardButton(text="🥉 Bronza (Common)", callback_data="theme_bronze")],
        [InlineKeyboardButton(text="🌅 Sunset (Kamalak)", callback_data="theme_sunset"),
         InlineKeyboardButton(text="🟣 Binafsha Neon", callback_data="theme_purple")],
        [InlineKeyboardButton(text="⚡ Kiber To'lqin", callback_data="theme_neon"),
         InlineKeyboardButton(text="🔴 Qizil Alanga", callback_data="theme_red")],
        [InlineKeyboardButton(text="💖 Pushti Magenta", callback_data="theme_magenta"),
         InlineKeyboardButton(text="🟠 Olovrang Katak", callback_data="theme_orange")],
        [InlineKeyboardButton(text="❄️ Muzdek Moviy", callback_data="theme_cyan"),
         InlineKeyboardButton(text="⚜️ Klassik Oltin", callback_data="theme_classic_gold")],
        [InlineKeyboardButton(text="🟢 Zumrad Yashil", callback_data="theme_green"),
         InlineKeyboardButton(text="🌍 Jahon Yulduzlari", callback_data="theme_world")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_photo_keyboard():
    buttons = [
        [InlineKeyboardButton(text="⏭️ Rasmsiz davom etish (Standart siluet)", callback_data="skip_dls_photo")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Asosiy Menyu")]],
        resize_keyboard=True
    )

@router.message(Command("dls"))
@router.message(F.text == "⚽ DLS Karta Yasash")
async def start_dls_creation(message: Message, state: FSMContext):
    await state.set_state(DLSCardStates.waiting_for_name)
    await message.answer(
        "⚽ <b>DLS Karta Generatoriga xush kelibsiz!</b>\n\n"
        "1-qadam: Kartaga yoziladigan <b>O'yinchi Ismini</b> (yoki familiyasini) yuboring:\n"
        "<i>(Masalan: JASUR, RONALDO, MESSI yoki o'z ismingiz)</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(DLSCardStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy Menyu":
        await state.clear()
        from handlers.start import get_main_keyboard
        await message.answer("Bosh menyuga qaytdingiz.", reply_markup=get_main_keyboard())
        return

    name = message.text.strip()
    if len(name) > 20:
        await message.answer("⚠️ Ism juda uzun! Iltimos, 16 belgidan oshmagan ism kiriting:")
        return

    await state.update_data(player_name=name)
    await state.set_state(DLSCardStates.waiting_for_position)
    safe_name = html.escape(name.upper())
    await message.answer(
        f"Ajoyib, ism: <b>{safe_name}</b>!\n\n"
        "2-qadam: O'yinchining <b>Pozitsiyasini</b> tanlang:",
        reply_markup=get_positions_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("pos_"), DLSCardStates.waiting_for_position)
async def process_position(callback: CallbackQuery, state: FSMContext):
    pos = callback.data.split("_")[1]
    await state.update_data(position=pos)
    await callback.message.delete()
    
    await state.set_state(DLSCardStates.waiting_for_rating)
    await callback.message.answer(
        f"Pozitsiya: <b>{pos}</b> qabul qilindi.\n\n"
        "3-qadam: O'yinchining <b>Umumiy Reytingini</b> tanlang yoki son ko'rinishida yozing (70 dan 99 gacha):",
        reply_markup=get_ratings_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("rate_"), DLSCardStates.waiting_for_rating)
async def process_rating_cb(callback: CallbackQuery, state: FSMContext):
    rating = int(callback.data.split("_")[1])
    await state.update_data(rating=rating)
    await callback.message.delete()
    
    await state.set_state(DLSCardStates.waiting_for_theme)
    await callback.message.answer(
        f"Reyting: <b>{rating}</b> tanlandi!\n\n"
        "4-qadam: <b>DLS Karta Orqa Fonini (Dizaynini)</b> tanlang: 👇",
        reply_markup=get_themes_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(DLSCardStates.waiting_for_rating)
async def process_rating_text(message: Message, state: FSMContext):
    try:
        rating = int(message.text.strip())
        if not (60 <= rating <= 99):
            await message.answer("⚠️ Reyting 60 dan 99 oralig'ida bo'lishi kerak. Qaytadan kiriting:")
            return
    except ValueError:
        await message.answer("⚠️ Iltimos, faqat butun son kiriting (masalan: 95):")
        return

    await state.update_data(rating=rating)
    await state.set_state(DLSCardStates.waiting_for_theme)
    await message.answer(
        f"Reyting: <b>{rating}</b> qabul qilindi!\n\n"
        "4-qadam: <b>DLS Karta Orqa Fonini (Dizaynini)</b> tanlang: 👇",
        reply_markup=get_themes_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("theme_"), DLSCardStates.waiting_for_theme)
async def process_theme_choice(callback: CallbackQuery, state: FSMContext):
    theme_name = callback.data.split("_", 1)[1]
    await state.update_data(theme=theme_name)
    await callback.message.delete()

    await state.set_state(DLSCardStates.waiting_for_photo)
    await callback.message.answer(
        "Karta foni muvaffaqiyatli tanlandi! ✅\n\n"
        "5-qadam: Endi kartaga qo'yish uchun <b>Rasm (Foto)</b> yuboring 📸.\n"
        "<i>(O'zingiz yoki futbolchining rasmini yuboring)</i>\n\n"
        "Agar rasm qo'ymoqchi bo'lmasangiz, quyidagi tugmani bosing 👇",
        reply_markup=get_photo_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

async def generate_and_send_card(message: Message, state: FSMContext, user_photo_bytes: bytes = None):
    loading_msg = await message.answer("⏳ DLS Karta tayyorlanmoqda, kuting...")
    
    data = await state.get_data()
    player_name = data.get("player_name", "PLAYER")
    rating = data.get("rating", 99)
    position = data.get("position", "ST")
    theme = data.get("theme", "black")
    
    has_photo = user_photo_bytes is not None and len(user_photo_bytes) > 0
    print(f"\n[DLS KARTA] Yaratilmoqda: Ism={player_name}, Reyting={rating}, Pozitsiya={position}, Fon={theme}, Rasm={'Bor (' + str(len(user_photo_bytes)) + ' bayt)' if has_photo else 'Yo\'q (Standart siluet)'}")

    try:
        card_bytes = create_dls_card(
            player_name=player_name,
            rating=rating,
            position=position,
            user_photo_bytes=user_photo_bytes,
            theme=theme
        )
        
        await loading_msg.delete()
        
        input_file = BufferedInputFile(card_bytes.getvalue(), filename=f"dls_{player_name}.png")
        
        from handlers.start import get_main_keyboard
        safe_name = html.escape(player_name.upper())
        caption = (
            f"✨ <b>DLS Kartangiz muvaffaqiyatli tayyorlandi!</b>\n\n"
            f"👤 <b>O'yinchi:</b> {safe_name}\n"
            f"⭐ <b>Reyting:</b> {rating}\n"
            f"⚡ <b>Pozitsiya:</b> {position}\n"
            f"🎨 <b>Fon dizayni:</b> {theme.title()}\n\n"
            f"Yana yangi karta yasash uchun quyidagi menyudan foydalanishingiz mumkin."
        )
        await message.answer_photo(photo=input_file, caption=caption, reply_markup=get_main_keyboard(), parse_mode="HTML")
        print(f"[DLS KARTA] Karta foydalanuvchiga yuborildi! ✅\n")
    except Exception as e:
        print(f"[DLS XATOLIK] {e}")
        await loading_msg.edit_text(f"⚠️ Xatolik yuz berdi: {html.escape(str(e))}")
    finally:
        await state.clear()

@router.message(DLSCardStates.waiting_for_photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    photo = message.photo[-1]
    photo_bytes_io = io.BytesIO()
    try:
        await message.bot.download(photo, destination=photo_bytes_io)
        user_photo_bytes = photo_bytes_io.getvalue()
    except Exception:
        user_photo_bytes = None
    
    await generate_and_send_card(message, state, user_photo_bytes)

@router.message(DLSCardStates.waiting_for_photo, F.document)
async def process_photo_document(message: Message, state: FSMContext):
    doc = message.document
    is_img = False
    if doc.mime_type and doc.mime_type.startswith("image/"):
        is_img = True
    elif doc.file_name and doc.file_name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        is_img = True
    
    if not is_img:
        await message.answer(
            "⚠️ Iltimos, rasm faylini (.jpg, .png) yuboring yoki quyidagi tugmani bosing:",
            reply_markup=get_photo_keyboard()
        )
        return

    doc_bytes_io = io.BytesIO()
    try:
        await message.bot.download(doc, destination=doc_bytes_io)
        user_photo_bytes = doc_bytes_io.getvalue()
    except Exception:
        user_photo_bytes = None
        
    await generate_and_send_card(message, state, user_photo_bytes)

@router.callback_query(F.data == "skip_dls_photo", DLSCardStates.waiting_for_photo)
async def process_photo_skip_cb(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await generate_and_send_card(callback.message, state, user_photo_bytes=None)
    await callback.answer()

@router.message(DLSCardStates.waiting_for_photo)
async def process_photo_text(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy Menyu":
        await state.clear()
        from handlers.start import get_main_keyboard
        await message.answer("Bosh menyuga qaytdingiz.", reply_markup=get_main_keyboard())
        return

    text_lower = (message.text or "").strip().lower()
    skip_keywords = ["o'tkazib yuborish", "otkazib yuborish", "skip", "yo'q", "yoq", "kerakmas", "tashlab ketish", "keyingisi", "rasmsiz"]
    if any(k in text_lower for k in skip_keywords):
        await generate_and_send_card(message, state, user_photo_bytes=None)
        return

    await message.answer(
        "📸 Iltimos, karta uchun <b>Rasm</b> yuboring yoki quyidagi <b>'⏭️ Rasmsiz davom etish'</b> tugmasini bosing:",
        reply_markup=get_photo_keyboard(),
        parse_mode="HTML"
    )
