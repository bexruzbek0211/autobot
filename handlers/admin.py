# ============================================================
# handlers/admin.py — Admin panel
# ============================================================

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db
from config import ADMIN_ID, ADMIN_PAROL

logger = logging.getLogger(__name__)
router = Router()


class AdminHolat(StatesGroup):
    parol = State()
    xabar_matni = State()
    xabar_yuborish = State()


def admin_tekshir(telegram_id: int) -> bool:
    return telegram_id == ADMIN_ID


# ─────────────────────────────────────────────
# /admin
# ─────────────────────────────────────────────

@router.message(Command("admin"))
async def admin_start(message: Message, state: FSMContext):
    if not admin_tekshir(message.from_user.id):
        return

    await message.answer("🔐 Admin parolini kiriting:")
    await state.set_state(AdminHolat.parol)


@router.message(AdminHolat.parol)
async def admin_parol(message: Message, state: FSMContext):
    if not admin_tekshir(message.from_user.id):
        return

    if message.text.strip() != ADMIN_PAROL:
        await message.answer("❌ Parol noto'g'ri.")
        await state.clear()
        return

    await state.clear()
    await _admin_menyu(message)


async def _admin_menyu(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="📊 Statistika", callback_data="admin_stat")
    kb.button(text="👥 Foydalanuvchilar", callback_data="admin_users")
    kb.button(text="📢 Xabar yuborish", callback_data="admin_xabar")
    kb.button(text="🚗 Mashinalar", callback_data="admin_mashinalar")
    kb.adjust(2)

    await message.answer(
        "🔧 <b>Admin Panel</b>\n\nNima qilmoqchisiz?",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )


# ─────────────────────────────────────────────
# STATISTIKA
# ─────────────────────────────────────────────

@router.callback_query(F.data == "admin_stat")
async def admin_statistika(callback: CallbackQuery):
    if not admin_tekshir(callback.from_user.id):
        return

    stat = await db.statistika()

    text = (
        "📊 <b>Bot Statistikasi</b>\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Jami foydalanuvchilar: {stat['foydalanuvchilar']}\n"
        f"🚗 Jami mashinalar: {stat['mashinalar']}\n"
        f"✅ Bajarilgan eslatmalar: {stat['bajarilgan_eslatmalar']}\n"
        "━━━━━━━━━━━━━━━━━━━"
    )

    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 Orqaga", callback_data="admin_menu")
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")


# ─────────────────────────────────────────────
# FOYDALANUVCHILAR
# ─────────────────────────────────────────────

@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    if not admin_tekshir(callback.from_user.id):
        return

    foydalanuvchilar = await db.barcha_foydalanuvchilar()

    text = f"👥 <b>Foydalanuvchilar ({len(foydalanuvchilar)} ta)</b>\n━━━━━━━━━━━━━━━━━━━\n"

    for f in foydalanuvchilar[:20]:
        text += f"\n👤 {f['ism']} (ID: {f['telegram_id']})\n"
        text += f"   📅 Qo'shilgan: {f['royxat_sanasi']}\n"

    if len(foydalanuvchilar) > 20:
        text += f"\n...va yana {len(foydalanuvchilar) - 20} ta"

    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 Orqaga", callback_data="admin_menu")
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")


# ─────────────────────────────────────────────
# MASHINALAR
# ─────────────────────────────────────────────

@router.callback_query(F.data == "admin_mashinalar")
async def admin_mashinalar(callback: CallbackQuery):
    if not admin_tekshir(callback.from_user.id):
        return

    async with __import__("aiosqlite").connect(__import__("config").DB_PATH) as conn:
        conn.row_factory = __import__("aiosqlite").Row
        async with conn.execute(
            """SELECT m.*, f.ism FROM mashinalar m
               JOIN foydalanuvchilar f ON m.foydalanuvchi_id = f.id
               WHERE m.faol = 1 ORDER BY m.id DESC LIMIT 20"""
        ) as cur:
            mashinalar = await cur.fetchall()

    text = f"🚗 <b>Mashinalar ({len(mashinalar)} ta)</b>\n━━━━━━━━━━━━━━━━━━━\n"

    rusum_stat = {}
    for m in mashinalar:
        rusum_stat[m["rusum"]] = rusum_stat.get(m["rusum"], 0) + 1

    for rusum, son in sorted(rusum_stat.items(), key=lambda x: -x[1]):
        text += f"🚗 {rusum}: {son} ta\n"

    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 Orqaga", callback_data="admin_menu")
    await callback.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")


# ─────────────────────────────────────────────
# XABAR YUBORISH
# ─────────────────────────────────────────────

@router.callback_query(F.data == "admin_xabar")
async def admin_xabar_menu(callback: CallbackQuery):
    if not admin_tekshir(callback.from_user.id):
        return

    kb = InlineKeyboardBuilder()
    kb.button(text="📢 Barcha foydalanuvchilarga", callback_data="admin_xabar_barcha")
    kb.button(text="🔙 Orqaga", callback_data="admin_menu")
    kb.adjust(1)

    await callback.message.edit_text(
        "📢 Xabar yuborish\nKimga?",
        reply_markup=kb.as_markup()
    )


@router.callback_query(F.data == "admin_xabar_barcha")
async def admin_xabar_barcha(callback: CallbackQuery, state: FSMContext):
    if not admin_tekshir(callback.from_user.id):
        return

    await state.update_data(xabar_turi="barcha")
    await callback.message.edit_text(
        "✏️ Yubormoqchi bo'lgan xabaringizni yozing:"
    )
    await state.set_state(AdminHolat.xabar_matni)


@router.message(AdminHolat.xabar_matni)
async def admin_xabar_qabul(message: Message, state: FSMContext):
    if not admin_tekshir(message.from_user.id):
        return

    matn = message.text.strip()
    await state.update_data(matn=matn)

    foydalanuvchilar = await db.barcha_foydalanuvchilar()

    kb = InlineKeyboardBuilder()
    kb.button(text=f"✅ Ha, {len(foydalanuvchilar)} ta foydalanuvchiga yuborish", callback_data="admin_xabar_yuborish")
    kb.button(text="❌ Bekor qilish", callback_data="admin_menu")
    kb.adjust(1)

    await message.answer(
        f"📢 <b>Preview:</b>\n━━━━━━━━━━━━━━━━━━━\n{matn}\n━━━━━━━━━━━━━━━━━━━\n"
        f"Jami: {len(foydalanuvchilar)} ta foydalanuvchi\nYuborilsinmi?",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )
    await state.set_state(AdminHolat.xabar_yuborish)


@router.callback_query(F.data == "admin_xabar_yuborish", AdminHolat.xabar_yuborish)
async def admin_xabar_yuborish(callback: CallbackQuery, state: FSMContext):
    if not admin_tekshir(callback.from_user.id):
        return

    data = await state.get_data()
    matn = data.get("matn", "")

    foydalanuvchilar = await db.barcha_foydalanuvchilar()
    yuborildi = 0
    xato = 0

    bot = callback.bot
    for f in foydalanuvchilar:
        try:
            await bot.send_message(f["telegram_id"], f"📢 <b>Xabar:</b>\n\n{matn}", parse_mode="HTML")
            yuborildi += 1
        except Exception as e:
            logger.warning(f"Xabar yuborishda xato {f['telegram_id']}: {e}")
            xato += 1

    await state.clear()
    await callback.message.edit_text(
        f"✅ Xabar yuborildi!\n"
        f"📤 Muvaffaqiyatli: {yuborildi}\n"
        f"❌ Xato: {xato}"
    )
    await db.admin_log(callback.from_user.id, "xabar_yuborish", f"Yuborildi: {yuborildi}")


@router.callback_query(F.data == "admin_menu")
async def admin_menu_callback(callback: CallbackQuery):
    if not admin_tekshir(callback.from_user.id):
        return
    await callback.message.delete()
    await _admin_menyu(callback.message)
