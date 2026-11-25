import os
import io
import html
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, FSInputFile,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.video_generator import generate_greeting_video

router = Router()

class GreetingStates(StatesGroup):
    waiting_for_occasion = State()
    waiting_for_name = State()
    waiting_for_photo = State()
    waiting_for_wish = State()

def get_occasions_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🎂 Tug'ilgan kun", callback_data="occ_Tug'ilgan kun"),
         InlineKeyboardButton(text="💍 To'y tabrigi", callback_data="occ_To'y")],
        [InlineKeyboardButton(text="🌸 8-Mart bayrami", callback_data="occ_8-Mart"),
         InlineKeyboardButton(text="🎉 Yangi Yil", callback_data="occ_Yangi Yil")],
        [InlineKeyboardButton(text="🌙 Qutlug' Hayit", callback_data="occ_Hayit"),
         InlineKeyboardButton(text="✨ Ezgu tilaklar", callback_data="occ_Umumiy")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_skip_photo_keyboard():
    buttons = [
        [InlineKeyboardButton(text="⏩ O'tkazib yuborish (Rasmsiz)", callback_data="skip_video_photo")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_wish_options_keyboard():
    buttons = [
        [InlineKeyboardButton(text="⭐ Standart chiroyli tilak", callback_data="wish_default")],
        [InlineKeyboardButton(text="✍️ O'zim tilak yozaman", callback_data="wish_custom")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Asosiy Menyu")]],
        resize_keyboard=True
    )

@router.message(Command("tabrik"))
@router.message(F.text == "🎬 Tabrik Video Yasash")
async def start_greeting_video(message: Message, state: FSMContext):
    await state.set_state(GreetingStates.waiting_for_occasion)
    await message.answer(
        "🎬 <b>Tabrik Video Maker xizmatiga xush kelibsiz!</b>\n\n"
        "1-qadam: Qaysi bayram yoki sana uchun tabrik video tayyorlaymiz? Tanlang: 👇",
        reply_markup=get_occasions_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("occ_"), GreetingStates.waiting_for_occasion)
async def process_occasion(callback: CallbackQuery, state: FSMContext):
    occasion = callback.data.split("_")[1]
    await state.update_data(occasion=occasion)
    await callback.message.delete()
    
    await state.set_state(GreetingStates.waiting_for_name)
    await callback.message.answer(
        f"Tanlangan ayyom: <b>{occasion}</b>!\n\n"
        "2-qadam: Tabrik kimga atalgan? <b>Ismini</b> yozib yuboring:\n"
        "<i>(Masalan: Madinaxon, Alisher, Onajonim, Jasurbek...)</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(GreetingStates.waiting_for_name)
async def process_recipient_name(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy Menyu":
        await state.clear()
        from handlers.start import get_main_keyboard
        await message.answer("Bosh menyuga qaytdingiz.", reply_markup=get_main_keyboard())
        return

    name = message.text.strip()
    if len(name) > 30:
        await message.answer("⚠️ Ism juda uzun! Iltimos, qisqaroq ism kiriting:")
        return

    await state.update_data(recipient_name=name)
    await state.set_state(GreetingStates.waiting_for_photo)
    safe_name = html.escape(name.title())
    
    await message.answer(
        f"Qabul qiluvchi: <b>{safe_name}</b>!\n\n"
        "3-qadam: <b>Tabrik egasining rasmini (foto)</b> yuborasizmi? 📸\n"
        "<i>(Rasm videoda porloq nurlangan oltin ramkada ko'rsatiladi)</i>\n\n"
        "Agar rasm qo'ymoqchi bo'lmasangiz, quyidagi tugmani bosing:",
        reply_markup=get_skip_photo_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "skip_video_photo", GreetingStates.waiting_for_photo)
async def process_skip_photo(callback: CallbackQuery, state: FSMContext):
    await state.update_data(recipient_photo_bytes=None)
    await callback.message.delete()
    
    await state.set_state(GreetingStates.waiting_for_wish)
    await callback.message.answer(
        "4-qadam: Endi tabrik matnini tanlang: 👇",
        reply_markup=get_wish_options_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(GreetingStates.waiting_for_photo, F.photo)
async def process_video_photo(message: Message, state: FSMContext):
    photo = message.photo[-1]
    photo_file = await message.bot.get_file(photo.file_id)
    photo_bytes_io = io.BytesIO()
    await message.bot.download_file(photo_file.file_path, photo_bytes_io)
    
    await state.update_data(recipient_photo_bytes=photo_bytes_io.getvalue())
    await state.set_state(GreetingStates.waiting_for_wish)
    
    await message.answer(
        "Rasm qabul qilindi! ✅\n\n"
        "4-qadam: Endi tabrik matnini tanlang: 👇",
        reply_markup=get_wish_options_keyboard(),
        parse_mode="HTML"
    )

@router.message(GreetingStates.waiting_for_photo)
async def process_video_photo_text(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy Menyu":
        await state.clear()
        from handlers.start import get_main_keyboard
        await message.answer("Bosh menyuga qaytdingiz.", reply_markup=get_main_keyboard())
        return

    # O'tkazib yuborish deb yozilgan bo'lsa
    await state.update_data(recipient_photo_bytes=None)
    await state.set_state(GreetingStates.waiting_for_wish)
    await message.answer(
        "4-qadam: Tabrik matnini tanlang: 👇",
        reply_markup=get_wish_options_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "wish_default", GreetingStates.waiting_for_wish)
async def process_default_wish(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    loading_msg = await callback.message.answer("🎬 <b>Musiqali va animatsion tabrik video tayyorlanmoqda...</b>\n<i>Iltimos, kuting (5-10 soniya).</i>", parse_mode="HTML")
    
    data = await state.get_data()
    occasion = data.get("occasion", "Tug'ilgan kun")
    name = data.get("recipient_name", "Do'stim")
    photo_bytes = data.get("recipient_photo_bytes", None)
    
    video_path = generate_greeting_video(
        recipient_name=name,
        occasion_type=occasion,
        custom_wish=None,
        recipient_photo_bytes=photo_bytes
    )
    
    await loading_msg.delete()
    
    video_file = FSInputFile(video_path)
    from handlers.start import get_main_keyboard
    safe_name = html.escape(name.title())
    safe_occ = html.escape(occasion)
    caption = (
        f"🎉 <b>Tabrik videongiz tayyor!</b>\n\n"
        f"🎯 <b>Ayyom:</b> {safe_occ}\n"
        f"👤 <b>Kimga:</b> {safe_name}\n\n"
        f"Videoni yaqinlaringizga yuborib ulashishingiz mumkin! 🎁"
    )
    await callback.message.answer_video(video=video_file, caption=caption, reply_markup=get_main_keyboard(), parse_mode="HTML")
    
    try:
        if os.path.exists(video_path):
            os.remove(video_path)
    except Exception:
        pass
        
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "wish_custom", GreetingStates.waiting_for_wish)
async def ask_custom_wish(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        "✍️ Videoda ko'rsatiladigan <b>o'z tabrik matningizni</b> yozib yuboring:\n"
        "<i>(Masalan: Baxt va omad tilayman, har doim sog' bo'ling!)</i>",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(GreetingStates.waiting_for_wish)
async def process_custom_wish_text(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy Menyu":
        await state.clear()
        from handlers.start import get_main_keyboard
        await message.answer("Bosh menyuga qaytdingiz.", reply_markup=get_main_keyboard())
        return

    wish_text = message.text.strip()
    loading_msg = await message.answer("🎬 <b>Maxsus musiqali tabrik video tayyorlanmoqda...</b>\n<i>Iltimos, kuting (5-10 soniya).</i>", parse_mode="HTML")
    
    data = await state.get_data()
    occasion = data.get("occasion", "Tug'ilgan kun")
    name = data.get("recipient_name", "Do'stim")
    photo_bytes = data.get("recipient_photo_bytes", None)
    
    video_path = generate_greeting_video(
        recipient_name=name,
        occasion_type=occasion,
        custom_wish=wish_text,
        recipient_photo_bytes=photo_bytes
    )
    
    await loading_msg.delete()
    
    video_file = FSInputFile(video_path)
    from handlers.start import get_main_keyboard
    safe_name = html.escape(name.title())
    safe_occ = html.escape(occasion)
    caption = (
        f"🎉 <b>Tabrik videongiz tayyor!</b>\n\n"
        f"🎯 <b>Ayyom:</b> {safe_occ}\n"
        f"👤 <b>Kimga:</b> {safe_name}\n\n"
        f"Videoni yaqinlaringizga yuborishingiz mumkin! 🎁"
    )
    await message.answer_video(video=video_file, caption=caption, reply_markup=get_main_keyboard(), parse_mode="HTML")
    
    try:
        if os.path.exists(video_path):
            os.remove(video_path)
    except Exception:
        pass
        
    await state.clear()
