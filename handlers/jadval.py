# ============================================================
# handlers/jadval.py — Jadval ko'rish
# ============================================================

import logging
from datetime import date, timedelta
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db
from utils.formatlar import jadval_xabar, sana_format, km_format

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "menu_jadval")
async def jadval_menu(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    foydalanuvchi = await db.foydalanuvchi_olish(telegram_id)
    mashinalar = await db.foydalanuvchi_mashinalar(foydalanuvchi["id"])

    if not mashinalar:
        kb = InlineKeyboardBuilder()
        kb.button(text="🔙 Orqaga", callback_data="menu_bosh")
        await callback.message.edit_text(
            "📭 Hali mashina yo'q.", reply_markup=kb.as_markup()
        )
        return

    if len(mashinalar) == 1:
        await _jadval_korsatish(callback, mashinalar[0]["id"])
        return

    kb = InlineKeyboardBuilder()
    for m in mashinalar:
        kb.button(
            text=f"🚗 {m['rusum']} {m['yil']}",
            callback_data=f"jadval_mashina_{m['id']}"
        )
    kb.button(text="🔙 Orqaga", callback_data="menu_bosh")
    kb.adjust(1)

    await callback.message.edit_text(
        "📅 Qaysi mashina jadvalini ko'rmoqchisiz?",
        reply_markup=kb.as_markup()
    )


@router.callback_query(F.data.startswith("jadval_mashina_"))
async def jadval_mashina(callback: CallbackQuery):
    mashina_id = int(callback.data.replace("jadval_mashina_", ""))
    await _jadval_korsatish(callback, mashina_id)


async def _jadval_korsatish(callback: CallbackQuery, mashina_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="📅 Bu oy", callback_data=f"jadval_oy_{mashina_id}_bu_oy")
    kb.button(text="📅 Keyingi oy", callback_data=f"jadval_oy_{mashina_id}_keyingi_oy")
    kb.button(text="📋 Barcha", callback_data=f"jadval_oy_{mashina_id}_barchasi")
    kb.button(text="🔙 Orqaga", callback_data="menu_jadval")
    kb.adjust(2)

    m = await db.mashina_olish(mashina_id)
    await callback.message.edit_text(
        f"📅 <b>{m['rusum']} {m['yil']}</b> jadvali\nQaysi davrni ko'rmoqchisiz?",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("jadval_oy_"))
async def jadval_davr(callback: CallbackQuery):
    parts = callback.data.replace("jadval_oy_", "").split("_", 1)
    mashina_id = int(parts[0])
    davr = parts[1]

    m = await db.mashina_olish(mashina_id)
    barcha_eslatmalar = await db.mashina_eslatmalari(mashina_id)

    bugun = date.today()

    if davr == "bu_oy":
        oy_boshi = date(bugun.year, bugun.month, 1)
        if bugun.month == 12:
            keyingi_oy = date(bugun.year + 1, 1, 1)
        else:
            keyingi_oy = date(bugun.year, bugun.month + 1, 1)
        oy_oxiri = keyingi_oy - timedelta(days=1)
        filtrlangan = [
            e for e in barcha_eslatmalar
            if e["sana"] and oy_boshi.isoformat() <= e["sana"] <= oy_oxiri.isoformat()
        ]
    elif davr == "keyingi_oy":
        if bugun.month == 12:
            keyingi_boshi = date(bugun.year + 1, 1, 1)
            keyingi_oxiri = date(bugun.year + 1, 1, 31)
        else:
            keyingi_boshi = date(bugun.year, bugun.month + 1, 1)
            keyingi_ay2 = bugun.month + 2
            yil2 = bugun.year
            if keyingi_ay2 > 12:
                keyingi_ay2 -= 12
                yil2 += 1
            keyingi_oxiri = date(yil2, keyingi_ay2, 1) - timedelta(days=1)
        filtrlangan = [
            e for e in barcha_eslatmalar
            if e["sana"] and keyingi_boshi.isoformat() <= e["sana"] <= keyingi_oxiri.isoformat()
        ]
    else:
        filtrlangan = list(barcha_eslatmalar[:20])

    mashina_dict = dict(m)
    text = jadval_xabar(
        [dict(e) for e in filtrlangan],
        mashina_dict,
        davr
    )

    kb = InlineKeyboardBuilder()
    kb.button(text="📅 Bu oy", callback_data=f"jadval_oy_{mashina_id}_bu_oy")
    kb.button(text="📅 Keyingi oy", callback_data=f"jadval_oy_{mashina_id}_keyingi_oy")
    kb.button(text="📋 Barcha", callback_data=f"jadval_oy_{mashina_id}_barchasi")
    kb.button(text="🔙 Orqaga", callback_data="menu_bosh")
    kb.adjust(2)

    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
