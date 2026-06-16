# ============================================================
# scheduler.py — APScheduler bilan kunlik eslatmalar
# ============================================================

import logging
from datetime import date, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

import database as db
from utils.formatlar import eslatma_xabar, mavsumiy_xabar
from utils.hisoblash import mashina_data_olish
from config import ESLATMA_VAQTI, YOZ_TEKSHIRUV_KUN, QISH_TEKSHIRUV_KUN

logger = logging.getLogger(__name__)


async def kunlik_eslatmalar_yuborish(bot: Bot):
    """Har kuni 08:00 da: barcha foydalanuvchilarga eslatma"""
    logger.info("Kunlik eslatmalar yuborilmoqda...")

    foydalanuvchilar = await db.barcha_foydalanuvchilar()
    yuborildi = 0

    for f in foydalanuvchilar:
        try:
            # Bu foydalanuvchining bugungi eslatmalari
            eslatmalar = await db.bugungi_eslatmalar(f["id"])

            if not eslatmalar:
                continue

            mashinalar = await db.foydalanuvchi_mashinalar(f["id"])
            mashina_map = {m["id"]: dict(m) for m in mashinalar}

            for eslatma in eslatmalar:
                mashina_id = eslatma["mashina_id"]
                mashina = mashina_map.get(mashina_id)
                if not mashina:
                    continue

                # Xabar formatlash
                text = eslatma_xabar(dict(eslatma), mashina)

                # Tugmalar
                from aiogram.utils.keyboard import InlineKeyboardBuilder
                kb = InlineKeyboardBuilder()
                kb.button(
                    text="✅ Bajardim",
                    callback_data=f"eslatma_bajardim_{eslatma['id']}"
                )
                kb.button(
                    text="⏰ 3 kun kechiktir",
                    callback_data=f"eslatma_kechir3_{eslatma['id']}"
                )
                kb.button(
                    text="⏰ 1 hafta kechiktir",
                    callback_data=f"eslatma_kechir7_{eslatma['id']}"
                )
                kb.adjust(1)

                await bot.send_message(
                    f["telegram_id"],
                    text,
                    reply_markup=kb.as_markup(),
                    parse_mode="HTML"
                )

                # Yuborildi deb belgilash
                await db.eslatma_yuborildi(eslatma["id"])
                yuborildi += 1

        except Exception as e:
            logger.error(f"Foydalanuvchi {f['telegram_id']} eslatma xatosi: {e}")

    logger.info(f"Kunlik eslatmalar: {yuborildi} ta yuborildi")


async def yaqinlashgan_eslatmalar(bot: Bot):
    """
    Har kuni 08:00 da: 3 kun ichidagi ishlar uchun ogohlantirish
    """
    logger.info("Yaqinlashgan eslatmalar tekshirilmoqda...")

    foydalanuvchilar = await db.barcha_foydalanuvchilar()
    uch_kun_keyin = (date.today() + timedelta(days=3)).isoformat()
    bugun = date.today().isoformat()

    for f in foydalanuvchilar:
        try:
            mashinalar = await db.foydalanuvchi_mashinalar(f["id"])
            for m in mashinalar:
                eslatmalar = await db.mashina_eslatmalari(m["id"])
                yaqin = [
                    e for e in eslatmalar
                    if e.get("sana") and bugun < e["sana"] <= uch_kun_keyin
                    and not e["yuborildi"]
                ]

                if yaqin:
                    text = (
                        f"⏰ <b>3 kun ichida kerakli ishlar:</b>\n"
                        f"🚗 {m['rusum']} {m['yil']}\n"
                        "━━━━━━━━━━━━━━━━━━━\n"
                    )
                    for e in yaqin:
                        from utils.formatlar import sana_format
                        text += f"📌 {e['nomi']} — {sana_format(e['sana'])}\n"

                    await bot.send_message(
                        f["telegram_id"], text, parse_mode="HTML"
                    )

        except Exception as e:
            logger.error(f"Yaqinlashgan eslatma xatosi {f['telegram_id']}: {e}")


async def mavsumiy_eslatma(bot: Bot, mavsum: str):
    """Yoz va qish mavsumiy tekshiruvlari"""
    logger.info(f"{mavsum} mavsumiy eslatma yuborilmoqda...")

    foydalanuvchilar = await db.barcha_foydalanuvchilar()

    for f in foydalanuvchilar:
        try:
            mashinalar = await db.foydalanuvchi_mashinalar(f["id"])
            for m in mashinalar:
                data = mashina_data_olish(m["rusum"])
                tekshiruvlar = data.get("mavsumiy_tekshiruvlar", {}).get(mavsum, [])

                if tekshiruvlar:
                    text = mavsumiy_xabar(mavsum, tekshiruvlar, m["rusum"])
                    from aiogram.utils.keyboard import InlineKeyboardBuilder
                    kb = InlineKeyboardBuilder()
                    kb.button(
                        text="✅ Hammasini tekshirdim",
                        callback_data="mavsum_tasdiqlash"
                    )
                    await bot.send_message(
                        f["telegram_id"], text,
                        reply_markup=kb.as_markup(),
                        parse_mode="HTML"
                    )
        except Exception as e:
            logger.error(f"Mavsumiy eslatma xatosi {f['telegram_id']}: {e}")


def scheduler_ishga_tushir(bot: Bot) -> AsyncIOScheduler:
    """Schedulerni sozlash va ishga tushirish"""
    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")

    vaqt_parts = ESLATMA_VAQTI.split(":")
    soat = int(vaqt_parts[0])
    daqiqa = int(vaqt_parts[1])

    # Har kuni eslatmalar
    scheduler.add_job(
        kunlik_eslatmalar_yuborish,
        trigger="cron",
        hour=soat,
        minute=daqiqa,
        args=[bot],
        id="kunlik_eslatmalar",
    )

    # Har kuni 09:00 — yaqinlashgan eslatmalar
    scheduler.add_job(
        yaqinlashgan_eslatmalar,
        trigger="cron",
        hour=9,
        minute=0,
        args=[bot],
        id="yaqinlashgan",
    )

    # 1-Iyun — Yoz mavsumiy tekshiruv
    scheduler.add_job(
        mavsumiy_eslatma,
        trigger="cron",
        month=6,
        day=1,
        hour=9,
        minute=0,
        args=[bot, "yoz"],
        id="yoz_mavsumiy",
    )

    # 1-Noyabr — Qish mavsumiy tekshiruv
    scheduler.add_job(
        mavsumiy_eslatma,
        trigger="cron",
        month=11,
        day=1,
        hour=9,
        minute=0,
        args=[bot, "qish"],
        id="qish_mavsumiy",
    )

    scheduler.start()
    logger.info("✅ Scheduler ishga tushdi")
    return scheduler
