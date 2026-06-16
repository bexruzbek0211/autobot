# ============================================================
# handlers/belgi.py — Belgi va diagnostika
# ============================================================

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.belgilar import BELGILAR
from utils.formatlar import belgi_xabar

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "menu_belgi")
async def belgi_menu(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="🔴 Lampochka yondi", callback_data="belgi_lampochka")
    kb.button(text="🔊 G'alati tovush", callback_data="belgi_tovush")
    kb.button(text="💨 Tutun chiqmoqda", callback_data="belgi_tutun")
    kb.button(text="🌡️ Harorat ko'tarilmoqda", callback_data="belgi_harorat")
    kb.button(text="🛢️ Moy sarfi ko'paydi", callback_data="belgi_moy_sarfi")
    kb.button(text="💧 Suyuqlik sizmoqda", callback_data="belgi_sizish")
    kb.button(text="🔙 Orqaga", callback_data="menu_bosh")
    kb.adjust(2)

    await callback.message.edit_text(
        "⚠️ <b>Belgi Tekshirish</b>\n\n"
        "Qanday belgi kuzatilmoqda?",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("belgi_") & ~F.data.startswith("belgi_tur_"))
async def belgi_turi(callback: CallbackQuery):
    kalit = callback.data.replace("belgi_", "")

    belgi = BELGILAR.get(kalit)
    if not belgi:
        await callback.answer("Topilmadi")
        return

    turlar = belgi.get("turlar", {})
    kb = InlineKeyboardBuilder()
    for tur_kalit, tur_info in turlar.items():
        kb.button(
            text=tur_info.get("nomi", tur_kalit),
            callback_data=f"belgi_tur_{kalit}_{tur_kalit}"
        )
    kb.button(text="🔙 Orqaga", callback_data="menu_belgi")
    kb.adjust(1)

    await callback.message.edit_text(
        f"{belgi.get('nomi', '')}\n\nAniqlang:",
        reply_markup=kb.as_markup()
    )


@router.callback_query(F.data.startswith("belgi_tur_"))
async def belgi_javob(callback: CallbackQuery):
    # format: belgi_tur_ASOSIY_TUR
    qism = callback.data.replace("belgi_tur_", "")
    # asosiy belgi va tur ajratish
    parts = qism.split("_", 1)
    if len(parts) < 2:
        await callback.answer("Xatolik")
        return

    asosiy = parts[0]
    tur = parts[1]

    belgi = BELGILAR.get(asosiy, {})
    turlar = belgi.get("turlar", {})
    belgi_info = turlar.get(tur)

    if not belgi_info:
        await callback.answer("Topilmadi")
        return

    text = belgi_xabar(belgi_info)

    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 Boshqa belgi", callback_data="menu_belgi")
    kb.button(text="🏠 Bosh menyu", callback_data="menu_bosh")
    kb.adjust(1)

    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
