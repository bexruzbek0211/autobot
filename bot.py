# ============================================================
# bot.py — Asosiy ishga tushirish fayli
# ============================================================

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from database import init_db
from scheduler import scheduler_ishga_tushir

# Handlerlar
from handlers import start, menu, jadval, eslatma, belgi, xarajat, tarix, admin

# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("autobot.log", encoding="utf-8"),
    ]
)
logger = logging.getLogger(__name__)


async def main():
    # Bot va Dispatcher yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Routerlarni qo'shish (tartib muhim)
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(jadval.router)
    dp.include_router(eslatma.router)
    dp.include_router(belgi.router)
    dp.include_router(xarajat.router)
    dp.include_router(tarix.router)
    dp.include_router(admin.router)

    # DB ishga tushirish
    await init_db()
    logger.info("✅ Ma'lumotlar bazasi tayyor")

    # Scheduler ishga tushirish
    scheduler = scheduler_ishga_tushir(bot)
    logger.info("✅ Scheduler ishga tushdi")

    # Botni ishga tushirish
    logger.info("🚗 AvtoServis Bot ishga tushdi!")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown()
        await bot.session.close()
        logger.info("Bot to'xtatildi")


if __name__ == "__main__":
    asyncio.run(main())
