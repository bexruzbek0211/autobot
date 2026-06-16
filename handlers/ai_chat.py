# ============================================================
# handlers/ai_chat.py — Gemini AI integratsiya
# ============================================================

import logging
import os
import aiohttp
from aiogram import Router, F
from aiogram.types import Message

import database as db

logger = logging.getLogger(__name__)
router = Router()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

SYSTEM_PROMPT = """Sen avtomobil texnik xizmati bo'yicha mutaxassissan.
O'zbekistondagi avtomobil egalari (Nexia, Matiz, Cobalt, Lacetti) uchun maslahat berasan.
Qisqa, aniq va amaliy javob ber. O'zbek tilida javob ber.
Faqat avtomobil va texnik xizmat haqida savollarga javob ber."""


async def gemini_javob(savol: str, mashina_info: str = "") -> str:
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
                data = await resp.json()
                javob = data["candidates"][0]["content"]["parts"][0]["text"]
                return javob.strip()

    except Exception as e:
        logger.error(f"Gemini xatosi: {e}")
        return "Hozircha javob bera olmayapman. Keyinroq urinib ko'ring."


@router.message(F.text & ~F.text.startswith("/"))
async def ai_savol(message: Message):
    telegram_id = message.from_user.id
    foydalanuvchi = await db.foydalanuvchi_olish(telegram_id)

    if not foydalanuvchi:
        return

    # Mashina ma'lumotlarini olish
    mashina_info = ""
    mashinalar = await db.foydalanuvchi_mashinalar(foydalanuvchi["id"])
    if mashinalar:
        m = mashinalar[0]
        mashina_info = f"{m['rusum']} {m['yil']} ({m['dvigatel']}L), {m['joriy_km']} km"

    # AI dan javob olish
    await message.answer("🤔 Javob tayyorlanmoqda...")
    javob = await gemini_javob(message.text, mashina_info)
    await message.answer(f"🤖 {javob}")
