# ============================================================
# handlers/menu.py — Bosh menyu va navigatsiya
# ============================================================

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db

logger = logging.getLogger(__name__)
router = Router()


async def bosh_menyu_korsatish(message: Message):
    telegram_id = message.from_user.id
    foydalanuvchi = await db.foydalanuvchi_olish(telegram_id)

    if not foydalanuvchi:
        await message.answer("❌ Siz ro'yxatdan o'tmagansiz. /start bosing.")
        return

    mashinalar = await db.foydalanuvchi_mashinalar(foydalanuvchi["id"])

    kb = InlineKeyboardBuilder()
    kb.button(text="🚗 Mashinalarim", callback_data="menu_mashinalar")
    kb.button(text="📅 Jadval", callback_data="menu_jadval")
    kb.button(text="⚠️ Belgi tekshir", callback_data="menu_belgi")
    kb.button(text="💰 Xarajat hisob", callback_data="menu_xarajat")
    kb.button(text="📋 Servis tarixi", callback_data="menu_tarix")
    kb.button(text="⚙️ Sozlamalar", callback_data="menu_sozlamalar")
    kb.adjust(2)

    mashina_soni = len(mashinalar)
    text = (
        f"🏠 <b>Bosh Menyu</b>\n\n"
        f"👤 {foydalanuvchi['ism']}\n"
        f"🚗 Mashinalar: {mashina_soni} ta\n\n"
        "Nima qilmoqchisiz?"
    )

    await message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "menu_bosh")
async def bosh_menyu_callback(callback: CallbackQuery):
    await callback.message.delete()
    await bosh_menyu_korsatish(callback.message)


@router.callback_query(F.data == "menu_mashinalar")
async def mashinalar_royxat(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    foydalanuvchi = await db.foydalanuvchi_olish(telegram_id)
    mashinalar = await db.foydalanuvchi_mashinalar(foydalanuvchi["id"])

    if not mashinalar:
        kb = InlineKeyboardBuilder()
        kb.button(text="➕ Mashina qo'shish", callback_data="mashina_qoshish")
        kb.button(text="🔙 Orqaga", callback_data="menu_bosh")
        kb.adjust(1)
        await callback.message.edit_text(
            "📭 Hali mashina qo'shilmagan.\nQo'shish uchun pastdagi tugmani bosing:",
            reply_markup=kb.as_markup()
        )
        return

    text = "🚗 <b>Mashinalarim:</b>\n━━━━━━━━━━━━━━━━━━━\n"
    kb = InlineKeyboardBuilder()

    for m in mashinalar:
        text += f"\n🚗 {m['rusum']} {m['yil']} ({m['dvigatel']}L)\n"
        text += f"📍 {m['joriy_km']:,} km\n"
        kb.button(
            text=f"📋 {m['rusum']} {m['yil']}",
            callback_data=f"mashina_{m['id']}"
        )

    kb.button(text="➕ Yangi mashina", callback_data="mashina_qoshish")
    kb.button(text="🔙 Orqaga", callback_data="menu_bosh")
    kb.adjust(1)

    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")


@router.callback_query(F.data.startswith("mashina_") & ~F.data.startswith("mashina_qoshish"))
async def mashina_detail(callback: CallbackQuery):
    try:
        mashina_id = int(callback.data.replace("mashina_", ""))
    except ValueError:
        return

    m = await db.mashina_olish(mashina_id)
    if not m:
        await callback.answer("Mashina topilmadi")
        return

    eslatmalar = await db.mashina_eslatmalari(mashina_id)
    keyingi = eslatmalar[0] if eslatmalar else None

    from utils.formatlar import km_format, sana_format
    text = (
        f"🚗 <b>{m['rusum']} {m['yil']} ({m['dvigatel']}L)</b>\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"🛢️ Moy: {m['moy_turi'].replace('_', ' ').title()}\n"
        f"📍 Joriy km: <b>{km_format(m['joriy_km'])}</b>\n"
        f"📊 Kunlik: ~{m['kunlik_km']} km\n"
    )

    if keyingi:
        text += f"\n📌 Keyingi ish: {keyingi['nomi']}\n"
        if keyingi.get("km_da"):
            qolgan = keyingi["km_da"] - m["joriy_km"]
            text += f"   Qoldi: {km_format(max(0, qolgan))}\n"
        if keyingi.get("sana"):
            text += f"   Sana: {sana_format(keyingi['sana'])}\n"

    kb = InlineKeyboardBuilder()
    kb.button(text="📍 KM yangilash", callback_data=f"km_yangilash_{mashina_id}")
    kb.button(text="📅 Jadval", callback_data=f"jadval_mashina_{mashina_id}")
    kb.button(text="📋 Tarix", callback_data=f"tarix_mashina_{mashina_id}")
    kb.button(text="🗑️ O'chirish", callback_data=f"mashina_ochir_{mashina_id}")
    kb.button(text="🔙 Orqaga", callback_data="menu_mashinalar")
    kb.adjust(2)

    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "mashina_qoshish")
async def mashina_qoshish_start(callback: CallbackQuery):
    await callback.message.edit_text(
        "➕ Yangi mashina qo'shish uchun /start buyrug'ini bosing "
        "va ro'yxat jarayonida mashina ma'lumotlarini kiriting.\n\n"
        "Yoki /mashina_qosh buyrug'ini yuboring."
    )


@router.callback_query(F.data.startswith("mashina_ochir_"))
async def mashina_ochirish_tasdiqlash(callback: CallbackQuery):
    mashina_id = int(callback.data.replace("mashina_ochir_", ""))
    m = await db.mashina_olish(mashina_id)

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Ha, o'chirish", callback_data=f"ochir_ha_{mashina_id}")
    kb.button(text="❌ Yo'q", callback_data=f"mashina_{mashina_id}")
    kb.adjust(2)

    await callback.message.edit_text(
        f"⚠️ <b>{m['rusum']} {m['yil']}</b>ni o'chirishni xohlaysizmi?\n"
        "Barcha eslatmalar ham o'chadi.",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("ochir_ha_"))
async def mashina_ochirish_bajar(callback: CallbackQuery):
    mashina_id = int(callback.data.replace("ochir_ha_", ""))
    await db.mashina_ochirish(mashina_id)
    await db.mashina_eslatmalar_ochir(mashina_id)
    await callback.answer("✅ O'chirildi")
    await mashinalar_royxat(callback)


@router.callback_query(F.data.startswith("km_yangilash_"))
async def km_yangilash_start(callback: CallbackQuery):
    mashina_id = int(callback.data.replace("km_yangilash_", ""))
    m = await db.mashina_olish(mashina_id)

    await callback.message.edit_text(
        f"📍 <b>{m['rusum']} {m['yil']}</b>\n"
        f"Hozirgi km: {m['joriy_km']:,}\n\n"
        "Yangi km ni kiriting:\n"
        f"<code>__km__{mashina_id}</code> formatida yuboring\n"
        f"Masalan: <code>90500 {mashina_id}</code>",
        parse_mode="HTML"
    )


@router.message(F.text.regexp(r"^\d+ \d+$"))
async def km_yangilash_qabul(message: Message):
    """Format: "yangi_km mashina_id" """
    try:
        parts = message.text.strip().split()
        yangi_km = int(parts[0])
        mashina_id = int(parts[1])

        m = await db.mashina_olish(mashina_id)
        if not m:
            return

        telegram_id = message.from_user.id
        foydalanuvchi = await db.foydalanuvchi_olish(telegram_id)
        if not foydalanuvchi or m["foydalanuvchi_id"] != foydalanuvchi["id"]:
            return

        if yangi_km < m["joriy_km"]:
            await message.answer(
                f"❌ Yangi km ({yangi_km:,}) joriy km dan "
                f"({m['joriy_km']:,}) kichik bo'lishi mumkin emas."
            )
            return

        await db.mashina_km_yangilash(mashina_id, yangi_km)

        # Eslatmalarni tekshirish
        from utils.hisoblash import km_yangilaganda_eslatmalar
        ogohlantirishlar = km_yangilaganda_eslatmalar(
            rusum=m["rusum"],
            moy_turi=m["moy_turi"],
            eski_km=m["joriy_km"],
            yangi_km=yangi_km,
            kunlik_km=m["kunlik_km"],
        )

        text = f"✅ KM yangilandi: <b>{yangi_km:,} km</b>\n"

        if ogohlantirishlar:
            text += "\n⚠️ <b>Yaqinlashgan ishlar:</b>\n"
            for o in ogohlantirishlar:
                text += f"• {o['nomi']} — {o['qolgan_km']:,} km qoldi\n"

        from utils.formatlar import narx_format
        await message.answer(text, parse_mode="HTML")

    except Exception as e:
        logger.error(f"KM yangilash xatosi: {e}")


@router.callback_query(F.data == "menu_sozlamalar")
async def sozlamalar(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    foydalanuvchi = await db.foydalanuvchi_olish(telegram_id)

    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Mashina qo'shish", callback_data="mashina_qoshish")
    kb.button(text="🔙 Orqaga", callback_data="menu_bosh")
    kb.adjust(1)

    await callback.message.edit_text(
        f"⚙️ <b>Sozlamalar</b>\n\n"
        f"👤 Ism: {foydalanuvchi['ism']}\n"
        f"🔔 Eslatma vaqti: 08:00\n",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )
