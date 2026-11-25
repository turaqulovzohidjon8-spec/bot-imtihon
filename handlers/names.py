import html
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, 
    InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.names_db import get_name_meaning, get_popular_names

router = Router()

class NameStates(StatesGroup):
    waiting_for_name = State()

def get_names_inline_keyboard():
    popular = get_popular_names()
    buttons = []
    row = []
    for idx, name in enumerate(popular):
        row.append(InlineKeyboardButton(text=name, callback_data=f"searchname_{name}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Asosiy Menyu")]],
        resize_keyboard=True
    )

@router.message(Command("ism"))
@router.message(F.text == "📖 Ismlar Ma'nosi")
async def start_names_menu(message: Message, state: FSMContext):
    await state.set_state(NameStates.waiting_for_name)
    text = (
        "📖 <b>Ismlar Ma'nosi bo'limiga xush kelibsiz!</b>\n\n"
        "O'zingiz yoki yaqinlaringizning ismini yozing, va men uning kelib chiqishi "
        "hamda to'liq ma'nosini topib beraman.\n\n"
        "<i>Masalan: <b>Ali, Madina, Jasur, Rayhona, Temur...</b></i>\n\n"
        "Yoki quyidagi mashhur ismlardan birini tanlang: 👇"
    )
    await message.answer(text, reply_markup=get_back_keyboard(), parse_mode="HTML")
    await message.answer("Mashhur ismlar:", reply_markup=get_names_inline_keyboard())

@router.callback_query(F.data.startswith("searchname_"))
async def callback_search_name(callback: CallbackQuery, state: FSMContext):
    name = callback.data.split("_")[1]
    result = await get_name_meaning(name)
    
    if result:
        q_name = html.escape(str(result['query']))
        origin = html.escape(str(result['origin']))
        gender = html.escape(str(result['gender']))
        meaning = html.escape(str(result['meaning']))
        source = html.escape(str(result.get('source', "O'zbek ismlari izohli lug'ati")))
        response = (
            f"📖 <b>Ism:</b> {q_name}\n"
            f"🌍 <b>Kelib chiqishi:</b> {origin}\n"
            f"👤 <b>Jinsi:</b> {gender}\n"
            f"📚 <b>Manba:</b> {source}\n\n"
            f"📝 <b>To'liq ma'nosi:</b>\n<i>{meaning}</i>\n\n"
            f"Boshqa ism ma'nosini bilish uchun ismni yozib yuboring! 👇"
        )
    else:
        safe_name = html.escape(name)
        response = f"Afsuski, <b>{safe_name}</b> ismi bo'yicha ma'lumot topilmadi."
        
    await callback.message.answer(response, parse_mode="HTML")
    await callback.answer()

@router.message(NameStates.waiting_for_name)
async def process_name_input(message: Message, state: FSMContext):
    if message.text == "🔙 Asosiy Menyu":
        await state.clear()
        from handlers.start import get_main_keyboard
        await message.answer("Bosh menyuga qaytdingiz.", reply_markup=get_main_keyboard())
        return

    name = message.text.strip()
    result = await get_name_meaning(name)

    if result:
        suggest_note = ""
        if "suggested" in result:
            s_name = html.escape(str(result['suggested']))
            suggest_note = f"\n💡 <i>(Mos ism: {s_name})</i>\n"
            
        q_name = html.escape(str(result['query']))
        origin = html.escape(str(result['origin']))
        gender = html.escape(str(result['gender']))
        meaning = html.escape(str(result['meaning']))
        source = html.escape(str(result.get('source', "O'zbek ismlari izohli lug'ati")))
        response = (
            f"📖 <b>Ism:</b> {q_name}\n"
            f"🌍 <b>Kelib chiqishi:</b> {origin}\n"
            f"👤 <b>Jinsi:</b> {gender}{suggest_note}\n"
            f"📚 <b>Manba:</b> {source}\n\n"
            f"📝 <b>To'liq ma'nosi:</b>\n<i>{meaning}</i>\n\n"
            f"✨ <i>Boshqa ism bilmoqchi bo'lsangiz, ismni yozing yoki orqaga qaytish uchun tugmani bosing:</i>"
        )
    else:
        safe_name = html.escape(name.title())
        response = (
            f"🔍 <b>'{safe_name}'</b> ismi bo'yicha bazamizdan aniq ma'lumot topilmadi.\n\n"
            f"Iltimos, ismni to'g'ri yozilganini tekshiring yoki boshqa ism kiriting.\n"
            f"<i>Misol uchun: Ali, Madina, Bobur, Sevara, Jasur...</i>"
        )

    await message.answer(response, parse_mode="HTML")

