# ============================================================
# handlers/xarajat.py — Xarajat hisoblash
# ============================================================

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db
from utils.hisoblash import oylik_xarajat_hisob, yillik_xarajat_hisob
from utils.formatlar import xarajat_xabar, son_format, narx_format

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "menu_xarajat")
async def xarajat_menu(callback: CallbackQuery):
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
        await _xarajat_davr(callback, mashinalar[0]["id"])
        return

    kb = InlineKeyboardBuilder()
    for m in mashinalar:
        kb.button(
            text=f"🚗 {m['rusum']} {m['yil']}",
            callback_data=f"xarajat_mashina_{m['id']}"
        )
    kb.button(text="🔙 Orqaga", callback_data="menu_bosh")
    kb.adjust(1)

    await callback.message.edit_text(
        "💰 Qaysi mashina xarajatini ko'rmoqchisiz?",
        reply_markup=kb.as_markup()
    )


@router.callback_query(F.data.startswith("xarajat_mashina_"))
async def xarajat_mashina(callback: CallbackQuery):
    mashina_id = int(callback.data.replace("xarajat_mashina_", ""))
    await _xarajat_davr(callback, mashina_id)


async def _xarajat_davr(callback: CallbackQuery, mashina_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="📅 Bu oy", callback_data=f"xarajat_hisob_{mashina_id}_bu_oy")
    kb.button(text="📊 Yillik taxmin", callback_data=f"xarajat_hisob_{mashina_id}_yillik")
    kb.button(text="🔙 Orqaga", callback_data="menu_bosh")
    kb.adjust(2)

    m = await db.mashina_olish(mashina_id)
    await callback.message.edit_text(
        f"💰 <b>{m['rusum']} {m['yil']}</b>\nQaysi davr?",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("xarajat_hisob_"))
async def xarajat_hisob(callback: CallbackQuery):
    qism = callback.data.replace("xarajat_hisob_", "")
    parts = qism.rsplit("_", 1)
    mashina_id = int(parts[0].replace("_bu", "").replace("_yillik", ""))

    # Davr aniqlash
    if "yillik" in callback.data:
        davr = "yillik"
    else:
        davr = "bu_oy"

    # mashina_id ni to'g'ri ajratish
    data_parts = callback.data.replace("xarajat_hisob_", "").split("_")
    mashina_id = int(data_parts[0])
    davr = data_parts[-1] if data_parts[-1] in ["oy", "yillik"] else "bu_oy"
    if davr == "oy":
        davr = "bu_oy"

    m = await db.mashina_olish(mashina_id)
    mashina_dict = dict(m)

    if davr == "yillik":
        xarajat = yillik_xarajat_hisob(m["rusum"])
        text = (
            f"📊 <b>{m['rusum']} {m['yil']} — Yillik taxmin</b>\n"
            "━━━━━━━━━━━━━━━━━━━\n"
        )
        for ish in xarajat["ishlar"][:10]:
            text += f"🔧 {ish['nomi']} (x{ish['marta']})\n"
            text += f"   {narx_format(ish['narx_min'], ish['narx_max'])}\n"

        text += "━━━━━━━━━━━━━━━━━━━\n"
        text += f"💵 Jami taxmin:\n"
        text += f"   {narx_format(xarajat['jami_min'], xarajat['jami_max'])}"
    else:
        eslatmalar = await db.mashina_eslatmalari(mashina_id)
        xarajat = oylik_xarajat_hisob(m["rusum"], [dict(e) for e in eslatmalar])
        text = xarajat_xabar(xarajat, mashina_dict)

    kb = InlineKeyboardBuilder()
    kb.button(text="📅 Bu oy", callback_data=f"xarajat_hisob_{mashina_id}_bu_oy")
    kb.button(text="📊 Yillik", callback_data=f"xarajat_hisob_{mashina_id}_yillik")
    kb.button(text="🔙 Orqaga", callback_data="menu_bosh")
    kb.adjust(2)

    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
