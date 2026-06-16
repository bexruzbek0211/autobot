# ============================================================
# handlers/tarix.py — Servis tarixi ko'rish
# ============================================================

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db
from utils.formatlar import tarix_xabar, son_format, sana_format

logger = logging.getLogger(__name__)
router = Router()


class NarxQoshHolat(StatesGroup):
    narx_kiritish = State()


@router.callback_query(F.data == "menu_tarix")
async def tarix_menu(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    foydalanuvchi = await db.foydalanuvchi_olish(telegram_id)
    mashinalar = await db.foydalanuvchi_mashinalar(foydalanuvchi["id"])

    if not mashinalar:
        kb = InlineKeyboardBuilder()
        kb.button(text="🔙 Orqaga", callback_data="menu_bosh")
        await callback.message.edit_text("📭 Hali mashina yo'q.", reply_markup=kb.as_markup())
        return

    if len(mashinalar) == 1:
        await _tarix_korsatish(callback, mashinalar[0]["id"])
        return

    kb = InlineKeyboardBuilder()
    for m in mashinalar:
        kb.button(
            text=f"🚗 {m['rusum']} {m['yil']}",
            callback_data=f"tarix_mashina_{m['id']}"
        )
    kb.button(text="🔙 Orqaga", callback_data="menu_bosh")
    kb.adjust(1)

    await callback.message.edit_text(
        "📋 Qaysi mashina tarixini ko'rmoqchisiz?",
        reply_markup=kb.as_markup()
    )


@router.callback_query(F.data.startswith("tarix_mashina_"))
async def tarix_mashina(callback: CallbackQuery):
    mashina_id = int(callback.data.replace("tarix_mashina_", ""))
    await _tarix_korsatish(callback, mashina_id)


async def _tarix_korsatish(callback: CallbackQuery, mashina_id: int):
    m = await db.mashina_olish(mashina_id)
    tarix = await db.mashina_tarixi(mashina_id, limit=15)

    mashina_dict = dict(m)
    text = tarix_xabar([dict(t) for t in tarix], mashina_dict)

    # Yillik xarajat
    from datetime import date
    yil_xarajat = await db.yillik_xarajat(mashina_id, date.today().year)
    if yil_xarajat:
        text += f"\n\n💰 {date.today().year} yil jami: {son_format(int(yil_xarajat))} so'm"

    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Xarajat qo'shish", callback_data=f"tarix_qosh_{mashina_id}")
    kb.button(text="🔙 Orqaga", callback_data="menu_bosh")
    kb.adjust(1)

    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")


@router.callback_query(F.data.startswith("tarix_qosh_"))
async def tarix_qosh(callback: CallbackQuery, state: FSMContext):
    mashina_id = int(callback.data.replace("tarix_qosh_", ""))
    m = await db.mashina_olish(mashina_id)

    # Texnik ish turlarini ko'rsatish
    turlar = [
        ("🛢️ Moy almashtirish", "moy"),
        ("🔧 Tormoz kolodka", "tormoz"),
        ("🔩 Filtr almashtirish", "filtr"),
        ("⚙️ Qayish almashtirish", "qayish"),
        ("🔋 Akkumulyator", "elektr"),
        ("🔩 Podveska", "podveska"),
        ("🛞 Shina", "shina"),
        ("🔧 Boshqa ta'mirot", "boshqa"),
    ]

    kb = InlineKeyboardBuilder()
    for nom, kalit in turlar:
        kb.button(
            text=nom,
            callback_data=f"tarix_tur_{mashina_id}_{kalit}"
        )
    kb.button(text="🔙 Orqaga", callback_data=f"tarix_mashina_{mashina_id}")
    kb.adjust(2)

    await state.update_data(mashina_id=mashina_id)
    await callback.message.edit_text(
        f"➕ <b>{m['rusum']} {m['yil']}</b>\nQanday ish bajarildi?",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("tarix_tur_"))
async def tarix_tur_qabul(callback: CallbackQuery, state: FSMContext):
    qism = callback.data.replace("tarix_tur_", "")
    parts = qism.rsplit("_", 1)
    mashina_id = int(parts[0])
    tur = parts[1]

    TUR_NOMLARI = {
        "moy": "Moy almashtirish",
        "tormoz": "Tormoz kolodka",
        "filtr": "Filtr almashtirish",
        "qayish": "Qayish almashtirish",
        "elektr": "Elektr tizim",
        "podveska": "Podveska",
        "shina": "Shina",
        "boshqa": "Boshqa ta'mirot",
    }

    nomi = TUR_NOMLARI.get(tur, tur)
    m = await db.mashina_olish(mashina_id)

    await state.update_data(mashina_id=mashina_id, tur=tur, nomi=nomi)

    await callback.message.edit_text(
        f"💵 <b>{nomi}</b> uchun xarajat miqdorini kiriting (so'mda):\n"
        f"Masalan: <code>120000</code>\n\n"
        f"(0 kiriting agar narxni bilmasangiz)",
        parse_mode="HTML"
    )
    await state.set_state(NarxQoshHolat.narx_kiritish)


@router.message(NarxQoshHolat.narx_kiritish)
async def narx_qabul(message: Message, state: FSMContext):
    try:
        narx = int(message.text.strip().replace(" ", "").replace(",", ""))
        if narx < 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ To'g'ri narx kiriting (masalan: 120000):")
        return

    data = await state.get_data()
    mashina_id = data["mashina_id"]
    tur = data["tur"]
    nomi = data["nomi"]

    telegram_id = message.from_user.id
    foydalanuvchi = await db.foydalanuvchi_olish(telegram_id)
    m = await db.mashina_olish(mashina_id)

    await db.tarix_qoshish(
        mashina_id=mashina_id,
        foydalanuvchi_id=foydalanuvchi["id"],
        tur=tur,
        nomi=nomi,
        km=m["joriy_km"],
        narx=narx,
    )

    await state.clear()

    kb = InlineKeyboardBuilder()
    kb.button(text="📋 Tarixni ko'rish", callback_data=f"tarix_mashina_{mashina_id}")
    kb.button(text="🏠 Bosh menyu", callback_data="menu_bosh")
    kb.adjust(1)

    narx_str = f"{son_format(narx)} so'm" if narx > 0 else "narx kiritilmadi"
    await message.answer(
        f"✅ <b>{nomi}</b> tarixga yozildi!\n"
        f"📍 Km: {m['joriy_km']:,}\n"
        f"💵 Narx: {narx_str}",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )
