# ============================================================
# handlers/eslatma.py — Eslatmalarga javob berish
# ============================================================

import logging
from datetime import date, timedelta
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db
from utils.formatlar import sana_format, km_format, son_format

logger = logging.getLogger(__name__)
router = Router()


def eslatma_keyboard(eslatma_id: int, mashina_id: int) -> object:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Bajardim", callback_data=f"eslatma_bajardim_{eslatma_id}")
    kb.button(text="⏰ 3 kun kechiktir", callback_data=f"eslatma_kechir3_{eslatma_id}")
    kb.button(text="⏰ 1 hafta kechiktir", callback_data=f"eslatma_kechir7_{eslatma_id}")
    kb.button(text="📅 Jadval", callback_data=f"jadval_mashina_{mashina_id}")
    kb.adjust(1)
    return kb.as_markup()


@router.callback_query(F.data.startswith("eslatma_bajardim_"))
async def eslatma_bajardim(callback: CallbackQuery):
    eslatma_id = int(callback.data.replace("eslatma_bajardim_", ""))

    # DB dan eslatma olish
    async with __import__("aiosqlite").connect(__import__("config").DB_PATH) as conn:
        conn.row_factory = __import__("aiosqlite").Row
        async with conn.execute(
            "SELECT * FROM eslatmalar WHERE id = ?", (eslatma_id,)
        ) as cur:
            eslatma = await cur.fetchone()

    if not eslatma:
        await callback.answer("❌ Topilmadi")
        return

    mashina = await db.mashina_olish(eslatma["mashina_id"])
    joriy_km = mashina["joriy_km"] if mashina else 0

    # Tasdiqlaш
    await db.eslatma_tasdiqlandi(eslatma_id)

    # Tarix yozish
    await db.tarix_qoshish(
        mashina_id=eslatma["mashina_id"],
        foydalanuvchi_id=eslatma["foydalanuvchi_id"],
        tur=eslatma["tur"],
        nomi=eslatma["nomi"],
        km=joriy_km,
    )

    # Agar moy bo'lsa — oxirgi_moy_km yangilash
    if "Moy" in eslatma["nomi"] and "korobka" not in eslatma["nomi"].lower():
        await db.mashina_oxirgi_moy_yangilash(eslatma["mashina_id"], joriy_km)

    await callback.message.edit_text(
        f"✅ <b>{eslatma['nomi']}</b> bajarildi!\n\n"
        f"📋 Tarixga yozildi.\n"
        f"📍 Km: {km_format(joriy_km)}",
        parse_mode="HTML"
    )
    await callback.answer("✅ Yaxshi!")


@router.callback_query(F.data.startswith("eslatma_kechir3_"))
async def eslatma_kechir3(callback: CallbackQuery):
    eslatma_id = int(callback.data.replace("eslatma_kechir3_", ""))
    yangi_sana = (date.today() + timedelta(days=3)).isoformat()
    await db.eslatma_kechiktir(eslatma_id, yangi_sana)
    await callback.answer("⏰ 3 kundan keyin eslatiladi")
    await callback.message.edit_text(
        f"⏰ Kechiktirildi.\n"
        f"Yangi sana: {sana_format(yangi_sana)}"
    )


@router.callback_query(F.data.startswith("eslatma_kechir7_"))
async def eslatma_kechir7(callback: CallbackQuery):
    eslatma_id = int(callback.data.replace("eslatma_kechir7_", ""))
    yangi_sana = (date.today() + timedelta(days=7)).isoformat()
    await db.eslatma_kechiktir(eslatma_id, yangi_sana)
    await callback.answer("⏰ 1 haftadan keyin eslatiladi")
    await callback.message.edit_text(
        f"⏰ Kechiktirildi.\n"
        f"Yangi sana: {sana_format(yangi_sana)}"
    )
