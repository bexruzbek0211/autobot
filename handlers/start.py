# ============================================================
# handlers/start.py — /start va ro'yxat
# ============================================================

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db

logger = logging.getLogger(__name__)
router = Router()

RUSUMLAR = ["Nexia", "Matiz", "Cobalt", "Lacetti"]

DVIGATELLER = {
    "Nexia":   ["1.5", "1.6"],
    "Matiz":   ["0.8", "1.0"],
    "Cobalt":  ["1.5"],
    "Lacetti": ["1.4", "1.6", "1.8"],
}

MOY_TURLARI = ["Mineral", "Yarim sintetik", "Sintetik"]

KUNLIK_KM = {
    "km_kam":   15,   # 10-20 km/kun
    "km_orta":  40,   # 30-50 km/kun
    "km_kop":   80,   # 60-100 km/kun
}

OXIRGI_MOY = {
    "moy_1oy":   1000,    # 1 oy ichida
    "moy_3oy":   3000,    # 3 oy ichida
    "moy_6oy":   6000,    # yarim yil
    "moy_bilmay": 0,      # bilmayman
}


class RoyxatHolat(StatesGroup):
    ism = State()
    rusum = State()
    yil = State()
    dvigatel = State()
    moy_turi = State()
    joriy_km = State()
    oxirgi_moy = State()
    kunlik_km = State()
    tasdiqlash = State()


# ─────────────────────────────────────────────
# /start
# ─────────────────────────────────────────────

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    telegram_id = message.from_user.id

    foydalanuvchi = await db.foydalanuvchi_olish(telegram_id)

    if foydalanuvchi:
        from handlers.menu import bosh_menyu_korsatish
        await bosh_menyu_korsatish(message)
        return

    await message.answer(
        "🚗 <b>AvtoServis Botga xush kelibsiz!</b>\n\n"
        "Bu bot sizga avtomobilingiz texnik xizmatini "
        "o'z vaqtida eslatib turadi.\n\n"
        "Ro'yxatdan o'tish uchun ismingizni kiriting:",
        parse_mode="HTML"
    )
    await state.set_state(RoyxatHolat.ism)


# ─────────────────────────────────────────────
# ISM
# ─────────────────────────────────────────────

@router.message(RoyxatHolat.ism)
async def ism_qabul(message: Message, state: FSMContext):
    ism = message.text.strip()
    if len(ism) < 2 or len(ism) > 50:
        await message.answer("❌ Ism 2-50 ta harf bo'lishi kerak. Qayta kiriting:")
        return

    await state.update_data(ism=ism)

    kb = InlineKeyboardBuilder()
    for rusum in RUSUMLAR:
        kb.button(text=f"🚗 {rusum}", callback_data=f"rusum_{rusum}")
    kb.adjust(2)

    await message.answer(
        f"✅ Salom, <b>{ism}</b>!\n\n"
        "Avtomobilingiz rusumini tanlang:",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )
    await state.set_state(RoyxatHolat.rusum)


# ─────────────────────────────────────────────
# RUSUM
# ─────────────────────────────────────────────

@router.callback_query(RoyxatHolat.rusum, F.data.startswith("rusum_"))
async def rusum_qabul(callback: CallbackQuery, state: FSMContext):
    rusum = callback.data.replace("rusum_", "")
    await state.update_data(rusum=rusum)
    await callback.message.edit_text(
        f"🚗 Rusum: <b>{rusum}</b>\n\n"
        "Ishlab chiqarilgan yilini kiriting (masalan: 2005):",
        parse_mode="HTML"
    )
    await state.set_state(RoyxatHolat.yil)


# ─────────────────────────────────────────────
# YIL
# ─────────────────────────────────────────────

@router.message(RoyxatHolat.yil)
async def yil_qabul(message: Message, state: FSMContext):
    try:
        yil = int(message.text.strip())
        if yil < 1990 or yil > 2025:
            raise ValueError
    except ValueError:
        await message.answer("❌ To'g'ri yil kiriting (1990-2025 oralig'ida):")
        return

    data = await state.get_data()
    rusum = data["rusum"]
    await state.update_data(yil=yil)

    dvigateller = DVIGATELLER.get(rusum, ["1.5"])
    kb = InlineKeyboardBuilder()
    for d in dvigateller:
        kb.button(text=f"⚙️ {d}L", callback_data=f"dvigatel_{d}")
    kb.adjust(2)

    await message.answer(
        f"✅ Yil: <b>{yil}</b>\n\n"
        "Dvigatel hajmini tanlang:",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )
    await state.set_state(RoyxatHolat.dvigatel)


# ─────────────────────────────────────────────
# DVIGATEL
# ─────────────────────────────────────────────

@router.callback_query(RoyxatHolat.dvigatel, F.data.startswith("dvigatel_"))
async def dvigatel_qabul(callback: CallbackQuery, state: FSMContext):
    dvigatel = callback.data.replace("dvigatel_", "")
    await state.update_data(dvigatel=dvigatel)

    kb = InlineKeyboardBuilder()
    for moy in MOY_TURLARI:
        kb.button(text=moy, callback_data=f"moy_{moy}")
    kb.adjust(1)

    await callback.message.edit_text(
        f"✅ Dvigatel: <b>{dvigatel}L</b>\n\n"
        "🛢️ Qanday moy ishlatasan?",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )
    await state.set_state(RoyxatHolat.moy_turi)


# ─────────────────────────────────────────────
# MOY TURI
# ─────────────────────────────────────────────

@router.callback_query(RoyxatHolat.moy_turi, F.data.startswith("moy_"))
async def moy_turi_qabul(callback: CallbackQuery, state: FSMContext):
    moy_turi = callback.data.replace("moy_", "")
    await state.update_data(moy_turi=moy_turi)

    await callback.message.edit_text(
        f"✅ Moy: <b>{moy_turi}</b>\n\n"
        "📍 Hozirgi speedometr ko'rsatkichi (km):\n"
        "Masalan: <code>87500</code>",
        parse_mode="HTML"
    )
    await state.set_state(RoyxatHolat.joriy_km)


# ─────────────────────────────────────────────
# JORIY KM
# ─────────────────────────────────────────────

@router.message(RoyxatHolat.joriy_km)
async def joriy_km_qabul(message: Message, state: FSMContext):
    try:
        km = int(message.text.strip().replace(" ", "").replace(",", ""))
        if km < 0 or km > 2000000:
            raise ValueError
    except ValueError:
        await message.answer("❌ To'g'ri km kiriting (masalan: 87500):")
        return

    await state.update_data(joriy_km=km)

    kb = InlineKeyboardBuilder()
    kb.button(text="1 oy ichida", callback_data="moy_vaqt_moy_1oy")
    kb.button(text="3 oy ichida", callback_data="moy_vaqt_moy_3oy")
    kb.button(text="Yarim yil", callback_data="moy_vaqt_moy_6oy")
    kb.button(text="Bilmayman", callback_data="moy_vaqt_moy_bilmay")
    kb.adjust(2)

    await message.answer(
        f"✅ Joriy km: <b>{km:,} km</b>\n\n"
        "🛢️ Oxirgi moy qachon almashtirilgan?",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )
    await state.set_state(RoyxatHolat.oxirgi_moy)


# ─────────────────────────────────────────────
# OXIRGI MOY
# ─────────────────────────────────────────────

@router.callback_query(RoyxatHolat.oxirgi_moy, F.data.startswith("moy_vaqt_"))
async def oxirgi_moy_qabul(callback: CallbackQuery, state: FSMContext):
    kalit = callback.data.replace("moy_vaqt_", "")
    qoshimcha_km = OXIRGI_MOY.get(kalit, 0)

    data = await state.get_data()
    joriy_km = data["joriy_km"]
    oxirgi_moy_km = max(0, joriy_km - qoshimcha_km)

    await state.update_data(oxirgi_moy_km=oxirgi_moy_km)

    kb = InlineKeyboardBuilder()
    kb.button(text="🐢 Kam (10-20 km/kun)", callback_data="kunlik_km_kam")
    kb.button(text="🚗 O'rta (30-50 km/kun)", callback_data="kunlik_km_orta")
    kb.button(text="🚀 Ko'p (60-100 km/kun)", callback_data="kunlik_km_kop")
    kb.adjust(1)

    await callback.message.edit_text(
        "📊 Kunda taxminan qancha km yurasiz?",
        reply_markup=kb.as_markup()
    )
    await state.set_state(RoyxatHolat.kunlik_km)


# ─────────────────────────────────────────────
# KUNLIK KM
# ─────────────────────────────────────────────

@router.callback_query(RoyxatHolat.kunlik_km, F.data.startswith("kunlik_"))
async def kunlik_km_qabul(callback: CallbackQuery, state: FSMContext):
    kalit = callback.data.replace("kunlik_", "")
    kunlik = KUNLIK_KM.get(kalit, 40)
    await state.update_data(kunlik_km=kunlik)

    data = await state.get_data()

    # Tasdiqlash xabari
    text = (
        "📋 <b>Ma'lumotlaringiz:</b>\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Ism: {data['ism']}\n"
        f"🚗 Rusum: {data['rusum']} {data['yil']}\n"
        f"⚙️ Dvigatel: {data['dvigatel']}L\n"
        f"🛢️ Moy: {data['moy_turi']}\n"
        f"📍 Joriy km: {data['joriy_km']:,}\n"
        f"📊 Kunlik masofa: ~{kunlik} km\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "To'g'rimi?"
    )

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Ha, to'g'ri", callback_data="royxat_tasdiqlash")
    kb.button(text="✏️ Qayta kiritish", callback_data="royxat_qayta")
    kb.adjust(1)

    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await state.set_state(RoyxatHolat.tasdiqlash)


# ─────────────────────────────────────────────
# TASDIQLASH
# ─────────────────────────────────────────────

@router.callback_query(RoyxatHolat.tasdiqlash, F.data == "royxat_tasdiqlash")
async def royxat_tasdiqlash(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    telegram_id = callback.from_user.id

    try:
        # Foydalanuvchi saqlash
        await db.foydalanuvchi_qoshish(telegram_id, data["ism"])
        foydalanuvchi = await db.foydalanuvchi_olish(telegram_id)

        # Mashina saqlash
        moy_turi_kichik = data["moy_turi"].lower().replace(" ", "_")
        mashina_id = await db.mashina_qoshish(
            foydalanuvchi_id=foydalanuvchi["id"],
            rusum=data["rusum"],
            yil=data["yil"],
            dvigatel=data["dvigatel"],
            moy_turi=moy_turi_kichik,
            joriy_km=data["joriy_km"],
            oxirgi_moy_km=data.get("oxirgi_moy_km", data["joriy_km"]),
            kunlik_km=data["kunlik_km"],
        )

        # Eslatmalar generatsiya
        from utils.hisoblash import eslatmalar_generatsiya
        moy_turi_map = {
            "mineral": "mineral",
            "yarim_sintetik": "yarim_sintetik",
            "sintetik": "sintetik",
        }
        moy_norm = moy_turi_kichik.replace(" ", "_")

        eslatmalar = eslatmalar_generatsiya(
            rusum=data["rusum"],
            moy_turi=moy_turi_map.get(moy_norm, "mineral"),
            joriy_km=data["joriy_km"],
            oxirgi_moy_km=data.get("oxirgi_moy_km", data["joriy_km"]),
            kunlik_km=data["kunlik_km"],
        )

        for e in eslatmalar:
            await db.eslatma_qoshish(
                mashina_id=mashina_id,
                foydalanuvchi_id=foydalanuvchi["id"],
                tur=e["tur"],
                nomi=e["nomi"],
                km_da=e.get("km_da"),
                sana=e.get("sana"),
            )

        await state.clear()
        await callback.message.edit_text(
            f"🎉 <b>Tabriklaymiz, {data['ism']}!</b>\n\n"
            f"✅ {data['rusum']} {data['yil']} ro'yxatga olindi\n"
            f"✅ {len(eslatmalar)} ta eslatma tuzildi\n\n"
            "Har kuni soat 08:00 da kerakli eslatmalar keladi.",
            parse_mode="HTML"
        )

        from handlers.menu import bosh_menyu_korsatish
        await bosh_menyu_korsatish(callback.message)

    except Exception as e:
        logger.error(f"Ro'yxat xatosi: {e}")
        await callback.message.edit_text(
            "❌ Xatolik yuz berdi. /start bilan qayta urinib ko'ring."
        )


@router.callback_query(RoyxatHolat.tasdiqlash, F.data == "royxat_qayta")
async def royxat_qayta(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("🔄 Qayta boshlaymiz...")
    await start(callback.message, state)
