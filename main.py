import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramNetworkError

from config import BOT_TOKEN
from handlers import start, dls_card, names, greeting_video, remove_bg
from services.db import add_user, init_db
from aiogram import BaseMiddleware
from aiogram.types import BotCommand
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject

class UserTrackingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = data.get("event_from_user")
        if user and not user.is_bot:
            add_user(user.id, user.username, user.full_name)
        return await handler(event, data)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def run_bot():
    if not BOT_TOKEN or BOT_TOKEN.strip() == "":
        print("\n" + "="*60)
        print("DIQQAT: Bot Token kiritilmagan!")
        print("Iltimos, config.py fayliga bot tokeningizni kiriting.")
        print("="*60 + "\n")
        return

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Har qanday foydalanuvchini avtomatik ro'yxatga olish (1 akkaunt = 1)
    dp.message.outer_middleware(UserTrackingMiddleware())
    dp.callback_query.outer_middleware(UserTrackingMiddleware())

    # Handler routerlarini ro'yxatdan o'tkazish
    dp.include_router(start.router)
    dp.include_router(dls_card.router)
    dp.include_router(names.router)
    dp.include_router(greeting_video.router)
    dp.include_router(remove_bg.router)

    try:
        await bot.delete_webhook(drop_pending_updates=True)

        # Telegram menyusiga / buyruqlarini o'rnatish
        await bot.set_my_commands([
            BotCommand(command="start", description="🚀 Botni ishga tushirish / Bosh menyu"),
            BotCommand(command="dls", description="⚽ DLS futbolchi kartasi yasash"),
            BotCommand(command="ism", description="📖 Ismlar ma'nosi qidirish"),
            BotCommand(command="tabrik", description="🎬 Tabrik video yasash"),
            BotCommand(command="bg", description="🖼️ Rasm orqa fonini tozalash"),
            BotCommand(command="about", description="ℹ️ Bot haqida va statistika")
        ])

        bot_info = await bot.get_me()
        logger.info(f"Bot muvaffaqiyatli ishga tushdi: @{bot_info.username}")
        print(f"\n[+] Bot ishlamoqda: @{bot_info.username}\nTo'xtatish uchun Ctrl+C bosing.\n")

        await dp.start_polling(bot)
    finally:
        await bot.session.close()

async def main():
    retry_delay = 5
    while True:
        try:
            await run_bot()
            break
        except TelegramNetworkError as net_err:
            print("\n" + "!"*60)
            print("⚠️ INTERNET GA ULANISHDA XATOLIK:")
            print("Kompyuteringizda internet o'chgan yoki 'api.telegram.org' serveriga ulanib bo'lmadi.")
            print(f"{retry_delay} soniyadan so'ng qayta ulanishga harakat qilinadi...")
            print("Iltimos, Wi-Fi yoki internet tarmog'ingiz ulanganligini tekshiring!")
            print("!"*60 + "\n")
            await asyncio.sleep(retry_delay)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Bot to'xtatildi!")
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi!")
