# ============================================================
# database.py — SQLite bilan barcha amallar
# ============================================================

import aiosqlite
import logging
from datetime import date, datetime
from config import DB_PATH

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# JADVALLAR YARATISH
# ─────────────────────────────────────────────

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS foydalanuvchilar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                ism TEXT,
                royxat_sanasi TEXT DEFAULT (date('now')),
                faol INTEGER DEFAULT 1
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS mashinalar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                foydalanuvchi_id INTEGER NOT NULL,
                rusum TEXT NOT NULL,
                yil INTEGER NOT NULL,
                dvigatel TEXT NOT NULL,
                moy_turi TEXT NOT NULL,
                joriy_km INTEGER NOT NULL,
                oxirgi_moy_km INTEGER NOT NULL,
                kunlik_km INTEGER NOT NULL,
                faol INTEGER DEFAULT 1,
                qoshilgan_sana TEXT DEFAULT (date('now')),
                FOREIGN KEY (foydalanuvchi_id) REFERENCES foydalanuvchilar(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS eslatmalar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mashina_id INTEGER NOT NULL,
                foydalanuvchi_id INTEGER NOT NULL,
                tur TEXT NOT NULL,
                nomi TEXT NOT NULL,
                km_da INTEGER,
                sana TEXT,
                yuborildi INTEGER DEFAULT 0,
                tasdiqlandi INTEGER DEFAULT 0,
                kechiktirildi INTEGER DEFAULT 0,
                FOREIGN KEY (mashina_id) REFERENCES mashinalar(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS servis_tarix (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mashina_id INTEGER NOT NULL,
                foydalanuvchi_id INTEGER NOT NULL,
                tur TEXT NOT NULL,
                nomi TEXT NOT NULL,
                km INTEGER,
                sana TEXT DEFAULT (date('now')),
                narx INTEGER DEFAULT 0,
                izoh TEXT,
                FOREIGN KEY (mashina_id) REFERENCES mashinalar(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS admin_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER,
                amal TEXT,
                tavsif TEXT,
                sana TEXT DEFAULT (datetime('now'))
            )
        """)
        await db.commit()
    logger.info("✅ DB tayyor")


# ─────────────────────────────────────────────
# FOYDALANUVCHI
# ─────────────────────────────────────────────

async def foydalanuvchi_olish(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM foydalanuvchilar WHERE telegram_id = ?",
            (telegram_id,)
        ) as cursor:
            return await cursor.fetchone()


async def foydalanuvchi_qoshish(telegram_id: int, ism: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO foydalanuvchilar (telegram_id, ism) VALUES (?, ?)",
            (telegram_id, ism)
        )
        await db.commit()


async def barcha_foydalanuvchilar():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM foydalanuvchilar WHERE faol = 1"
        ) as cursor:
            return await cursor.fetchall()


async def foydalanuvchi_blok(telegram_id: int, faol: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE foydalanuvchilar SET faol = ? WHERE telegram_id = ?",
            (faol, telegram_id)
        )
        await db.commit()


# ─────────────────────────────────────────────
# MASHINA
# ─────────────────────────────────────────────

async def mashina_qoshish(foydalanuvchi_id: int, rusum: str, yil: int,
                           dvigatel: str, moy_turi: str, joriy_km: int,
                           oxirgi_moy_km: int, kunlik_km: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """INSERT INTO mashinalar
               (foydalanuvchi_id, rusum, yil, dvigatel, moy_turi,
                joriy_km, oxirgi_moy_km, kunlik_km)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (foydalanuvchi_id, rusum, yil, dvigatel, moy_turi,
             joriy_km, oxirgi_moy_km, kunlik_km)
        )
        await db.commit()
        return cursor.lastrowid


async def foydalanuvchi_mashinalar(foydalanuvchi_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM mashinalar WHERE foydalanuvchi_id = ? AND faol = 1",
            (foydalanuvchi_id,)
        ) as cursor:
            return await cursor.fetchall()


async def mashina_olish(mashina_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM mashinalar WHERE id = ?",
            (mashina_id,)
        ) as cursor:
            return await cursor.fetchone()


async def mashina_km_yangilash(mashina_id: int, yangi_km: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE mashinalar SET joriy_km = ? WHERE id = ?",
            (yangi_km, mashina_id)
        )
        await db.commit()


async def mashina_oxirgi_moy_yangilash(mashina_id: int, km: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE mashinalar SET oxirgi_moy_km = ? WHERE id = ?",
            (km, mashina_id)
        )
        await db.commit()


async def mashina_ochirish(mashina_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE mashinalar SET faol = 0 WHERE id = ?",
            (mashina_id,)
        )
        await db.commit()


# ─────────────────────────────────────────────
# ESLATMALAR
# ─────────────────────────────────────────────

async def eslatma_qoshish(mashina_id: int, foydalanuvchi_id: int,
                           tur: str, nomi: str,
                           km_da: int = None, sana: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO eslatmalar
               (mashina_id, foydalanuvchi_id, tur, nomi, km_da, sana)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (mashina_id, foydalanuvchi_id, tur, nomi, km_da, sana)
        )
        await db.commit()


async def bugungi_eslatmalar(foydalanuvchi_id: int):
    """Bugun yuborish kerak bo'lgan eslatmalar"""
    bugun = date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT e.*, m.rusum, m.yil, m.joriy_km
               FROM eslatmalar e
               JOIN mashinalar m ON e.mashina_id = m.id
               WHERE e.foydalanuvchi_id = ?
               AND e.yuborildi = 0
               AND e.tasdiqlandi = 0
               AND (e.sana <= ? OR e.sana IS NULL)
               AND m.faol = 1""",
            (foydalanuvchi_id, bugun)
        ) as cursor:
            return await cursor.fetchall()


async def km_eslatmalari_tekshir(mashina_id: int, joriy_km: int):
    """Joriy km ga yetgan eslatmalarni topish"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT * FROM eslatmalar
               WHERE mashina_id = ?
               AND km_da IS NOT NULL
               AND km_da <= ?
               AND tasdiqlandi = 0
               AND yuborildi = 0""",
            (mashina_id, joriy_km)
        ) as cursor:
            return await cursor.fetchall()


async def eslatma_yuborildi(eslatma_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE eslatmalar SET yuborildi = 1 WHERE id = ?",
            (eslatma_id,)
        )
        await db.commit()


async def eslatma_tasdiqlandi(eslatma_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE eslatmalar SET tasdiqlandi = 1, yuborildi = 1 WHERE id = ?",
            (eslatma_id,)
        )
        await db.commit()


async def eslatma_kechiktir(eslatma_id: int, yangi_sana: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """UPDATE eslatmalar
               SET kechiktirildi = 1, yuborildi = 0, sana = ?
               WHERE id = ?""",
            (yangi_sana, eslatma_id)
        )
        await db.commit()


async def mashina_eslatmalari(mashina_id: int):
    """Bitta mashina uchun barcha kelgusi eslatmalar"""
    bugun = date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT * FROM eslatmalar
               WHERE mashina_id = ?
               AND tasdiqlandi = 0
               ORDER BY km_da ASC, sana ASC""",
            (mashina_id,)
        ) as cursor:
            return await cursor.fetchall()


async def mashina_eslatmalar_ochir(mashina_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM eslatmalar WHERE mashina_id = ?",
            (mashina_id,)
        )
        await db.commit()


# ─────────────────────────────────────────────
# SERVIS TARIXI
# ─────────────────────────────────────────────

async def tarix_qoshish(mashina_id: int, foydalanuvchi_id: int,
                         tur: str, nomi: str, km: int,
                         narx: int = 0, izoh: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO servis_tarix
               (mashina_id, foydalanuvchi_id, tur, nomi, km, narx, izoh)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (mashina_id, foydalanuvchi_id, tur, nomi, km, narx, izoh)
        )
        await db.commit()


async def mashina_tarixi(mashina_id: int, limit: int = 20):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT * FROM servis_tarix
               WHERE mashina_id = ?
               ORDER BY sana DESC, id DESC
               LIMIT ?""",
            (mashina_id, limit)
        ) as cursor:
            return await cursor.fetchall()


async def yillik_xarajat(mashina_id: int, yil: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT SUM(narx) as jami FROM servis_tarix
               WHERE mashina_id = ?
               AND strftime('%Y', sana) = ?""",
            (mashina_id, str(yil))
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] or 0


# ─────────────────────────────────────────────
# STATISTIKA (admin uchun)
# ─────────────────────────────────────────────

async def statistika():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM foydalanuvchilar WHERE faol = 1"
        ) as c:
            foydalanuvchilar = (await c.fetchone())[0]

        async with db.execute(
            "SELECT COUNT(*) FROM mashinalar WHERE faol = 1"
        ) as c:
            mashinalar = (await c.fetchone())[0]

        async with db.execute(
            "SELECT COUNT(*) FROM eslatmalar WHERE tasdiqlandi = 1"
        ) as c:
            bajarilgan = (await c.fetchone())[0]

        return {
            "foydalanuvchilar": foydalanuvchilar,
            "mashinalar": mashinalar,
            "bajarilgan_eslatmalar": bajarilgan,
        }


async def admin_log(admin_id: int, amal: str, tavsif: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO admin_log (admin_id, amal, tavsif) VALUES (?, ?, ?)",
            (admin_id, amal, tavsif)
        )
        await db.commit()
