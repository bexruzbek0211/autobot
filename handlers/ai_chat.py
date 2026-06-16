import logging
import os
import asyncio
import aiohttp
from aiogram import Router, F
from aiogram.types import Message
import database as db

logger = logging.getLogger(__name__)
router = Router()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={GEMINI_API_KEY}"

SYSTEM_PROMPT = """Sen avtomobil texnik xizmati bo'yicha mutaxassissan. O'zbekistondagi avtomobil egalari (Nexia, Matiz, Cobalt, Lacetti) uchun maslahat berasan. Qisqa, aniq va amaliy javob ber. O'zbek tilida javob ber."""

async def gemini_javob(savol: str, mashina_info: str = "") -> str:
    for urinish in range(3):
        try:
            if mashina_info:
                matn = f"Foydalanuvchining mashinasi: {mashina_info}\n\nSavol: {savol}"
            else:
                matn = savol

            payload = {
                "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                "contents": [{"parts": [{"text": matn}]}],
                "generationConfig": {"maxOutputTokens": 500, "temperature": 0.7}
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(GEMINI_URL, json=payload) as resp:
                    if resp.status == 429:
                        await asyncio.sleep(15 * (urinish + 1))
                        continue
                    data = await resp.json()
                    javob = data["candidates"][0]["content"]["parts"][0]["text"]
                    return javob.strip()
        except Exception as e:
            logger.error(f"Gemini xatosi: {e}")
            await asyncio.sleep(3)
    return "Hozircha band, 1 daqiqadan keyin urinib ko'ring."

@router.message(F.text & ~F.text.startswith("/"))
async def ai_savol(message: Message):
    telegram_id = message.from_user.id
    foydalanuvchi = await db.foydalanuvchi_olish(telegram_id)
    if not foydalanuvchi:
        return

    mashina_info = ""
    mashinalar = await db.foydalanuvchi_mashinalar(foydalanuvchi["id"])
    if mashinalar:
        m = mashinalar[0]
        mashina_info = f"{m['rusum']} {m['yil']} ({m['dvigatel']}L), {m['joriy_km']} km"

    await message.answer("🤔 Javob tayyorlanmoqda...")
    javob = await gemini_javob(message.text, mashina_info)
    await message.answer(f"🤖 {javob}")
