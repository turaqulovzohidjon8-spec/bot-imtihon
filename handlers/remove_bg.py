import io
import html
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.bg_remover import remove_background

router = Router()

class RemoveBgStates(StatesGroup):
    waiting_for_photo = State()

def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Asosiy Menyu")]],
        resize_keyboard=True
    )

@router.message(Command("bg"))
@router.message(F.text == "🖼️ Orqa Fon Olish")
async def start_remove_bg(message: Message, state: FSMContext):
    await state.set_state(RemoveBgStates.waiting_for_photo)
    text = (
        "🖼️ <b>Orqa Fonni Olib Tashlash xizmatiga xush kelibsiz!</b>\n\n"
        "Orqa fonini tozalash (qirqib olish) kerak bo'lgan <b>rasm (foto)</b> yuboring 📸.\n\n"
        "<i>Bot obyektni aniqlab, orqa fonini olib tashlaydi va sizga shaffof (PNG) formatida taqdim etadi!</i>"
    )
    await message.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")

@router.message(RemoveBgStates.waiting_for_photo, F.photo)
async def process_remove_bg_photo(message: Message, state: FSMContext):
    loading_msg = await message.answer("⏳ <b>Rasm tahlil qilinmoqda va orqa fon olib tashlanmoqda...</b>\n<i>Iltimos, kuting (3-5 soniya).</i>", parse_mode="HTML")
    
    try:
        photo = message.photo[-1]
        photo_file = await message.bot.get_file(photo.file_id)
        photo_bytes_io = io.BytesIO()
        await message.bot.download_file(photo_file.file_path, photo_bytes_io)
        input_bytes = photo_bytes_io.getvalue()

        # Orqa fonni olib tashlash
        clean_png_bytes = remove_background(input_bytes)
        await loading_msg.delete()

        doc_file = BufferedInputFile(clean_png_bytes, filename="no_bg_image.png")
        from handlers.start import get_main_keyboard
        caption = (
            "✅ <b>Orqa fon muvaffaqiyatli olib tashlandi!</b>\n\n"
            "Ushbu shaffof (PNG) rasmni DLS karta, stiker yoki boshqa dizaynlarda ishlatishingiz mumkin."
        )
        # Fayl ko'rinishida yuborish (haqiqiy shaffoflik saqlanishi uchun)
        await message.answer_document(document=doc_file, caption=caption, reply_markup=get_main_keyboard(), parse_mode="HTML")
        await state.clear()
    except Exception as e:
        await loading_msg.delete()
        await message.answer("⚠️ Rasmni qayta ishlashda xatolik yuz berdi. Iltimos, boshqa aniqroq rasm yuborib ko'ring.")
        await state.clear()

@router.message(RemoveBgStates.waiting_for_photo, F.document)
async def process_remove_bg_document(message: Message, state: FSMContext):
    if not message.document.mime_type or not message.document.mime_type.startswith("image/"):
        await message.answer("⚠️ Iltimos, rasm faylini yuboring!")
        return

    loading_msg = await message.answer("⏳ <b>Fayl yuklanib, orqa fon tozalanmoqda...</b>", parse_mode="HTML")
    try:
        doc_file_info = await message.bot.get_file(message.document.file_id)
        doc_bytes_io = io.BytesIO()
        await message.bot.download_file(doc_file_info.file_path, doc_bytes_io)
        input_bytes = doc_bytes_io.getvalue()

        clean_png_bytes = remove_background(input_bytes)
        await loading_msg.delete()

        doc_file = BufferedInputFile(clean_png_bytes, filename="no_bg_image.png")
        from handlers.start import get_main_keyboard
        caption = "✅ <b>Orqa foni tozalangan shaffof PNG tayyor!</b>"
        await message.answer_document(document=doc_file, caption=caption, reply_markup=get_main_keyboard(), parse_mode="HTML")
        await state.clear()
    except Exception:
        await loading_msg.delete()
        await message.answer("⚠️ Faylni qayta ishlashda xatolik yuz berdi. Iltimos, boshqa rasm yuborib ko'ring.")
        await state.clear()

