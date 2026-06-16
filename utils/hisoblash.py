# ============================================================
# utils/hisoblash.py — Hisoblash va jadval generatsiya
# ============================================================

import logging
from datetime import date, timedelta
from data.nexia import NEXIA_DATA
from data.matiz import MATIZ_DATA
from data.cobalt import COBALT_DATA
from data.lacetti import LACETTI_DATA

logger = logging.getLogger(__name__)

MASHINA_DATA = {
    "Nexia":   NEXIA_DATA,
    "Matiz":   MATIZ_DATA,
    "Cobalt":  COBALT_DATA,
    "Lacetti": LACETTI_DATA,
}


def mashina_data_olish(rusum: str) -> dict:
    return MASHINA_DATA.get(rusum, {})


def moy_interval_olish(rusum: str, moy_turi: str) -> int:
    data = mashina_data_olish(rusum)
    return data.get("moy_intervallari", {}).get(moy_turi, 5000)


def km_dan_sana(joriy_km: int, maqsad_km: int, kunlik_km: int) -> date:
    """Maqsad km ga qancha kunda etishishni hisoblash"""
    qolgan_km = maqsad_km - joriy_km
    if qolgan_km <= 0:
        return date.today()
    kunlar = max(1, qolgan_km // kunlik_km)
    return date.today() + timedelta(days=kunlar)


def eslatmalar_generatsiya(rusum: str, moy_turi: str,
                            joriy_km: int, oxirgi_moy_km: int,
                            kunlik_km: int) -> list:
    """
    Mashina ma'lumotlari asosida barcha eslatmalarni hisoblaydi.
    Return: [{"nomi": ..., "km_da": ..., "sana": ..., "tur": ...}, ...]
    """
    data = mashina_data_olish(rusum)
    if not data:
        logger.warning(f"Rusum topilmadi: {rusum}")
        return []

    eslatmalar = []
    jadval = data.get("texnik_jadval", {})
    bugun = date.today()

    for nomi, info in jadval.items():
        tur = info.get("tur", "boshqa")

        # MOY uchun maxsus hisob
        if tur == "moy" and "Moy" in nomi and "korobka" not in nomi.lower() and "gur" not in nomi.lower():
            interval = moy_interval_olish(rusum, moy_turi)
            keyingi_moy_km = oxirgi_moy_km + interval

            # Agar allaqachon o'tib ketgan bo'lsa
            if keyingi_moy_km <= joriy_km:
                keyingi_moy_km = joriy_km + interval

            sana = km_dan_sana(joriy_km, keyingi_moy_km, kunlik_km)
            eslatmalar.append({
                "nomi": nomi,
                "tur": tur,
                "km_da": keyingi_moy_km,
                "sana": sana.isoformat(),
            })
            continue

        # YILLIK texnik ishlar uchun
        if info.get("interval_yil"):
            yillar = info["interval_yil"]
            keyingi_sana = bugun + timedelta(days=yillar * 365)
            eslatmalar.append({
                "nomi": nomi,
                "tur": tur,
                "km_da": None,
                "sana": keyingi_sana.isoformat(),
            })
            continue

        # KM asosidagi texnik ishlar
        interval_km = info.get("interval_km")
        if interval_km:
            # Oxirgi moy km dan hisoblash (taxminan)
            keyingi_km = joriy_km + interval_km
            sana = km_dan_sana(joriy_km, keyingi_km, kunlik_km)
            eslatmalar.append({
                "nomi": nomi,
                "tur": tur,
                "km_da": keyingi_km,
                "sana": sana.isoformat(),
            })

    # Sanaga qarab tartiblash
    eslatmalar.sort(key=lambda x: x["sana"] or "9999-99-99")
    return eslatmalar


def oylik_xarajat_hisob(rusum: str, eslatmalar: list) -> dict:
    """Bu oy rejalashtirilgan xarajatlarni hisoblash"""
    data = mashina_data_olish(rusum)
    jadval = data.get("texnik_jadval", {})

    bugun = date.today()
    oy_oxiri = date(bugun.year, bugun.month, 1) + timedelta(days=32)
    oy_oxiri = date(oy_oxiri.year, oy_oxiri.month, 1) - timedelta(days=1)

    jami_min = 0
    jami_max = 0
    bu_oy_ishlar = []

    for eslatma in eslatmalar:
        sana_str = eslatma.get("sana")
        if not sana_str:
            continue
        try:
            sana = date.fromisoformat(sana_str)
        except Exception:
            continue

        if bugun <= sana <= oy_oxiri:
            nomi = eslatma.get("nomi", "")
            info = jadval.get(nomi, {})
            narx_min = info.get("narx_min", 0)
            narx_max = info.get("narx_max", 0)
            jami_min += narx_min
            jami_max += narx_max
            bu_oy_ishlar.append({
                "nomi": nomi,
                "narx_min": narx_min,
                "narx_max": narx_max,
                "sana": sana_str,
            })

    return {
        "ishlar": bu_oy_ishlar,
        "jami_min": jami_min,
        "jami_max": jami_max,
    }


def yillik_xarajat_hisob(rusum: str) -> dict:
    """Bir yillik taxminiy xarajat"""
    data = mashina_data_olish(rusum)
    jadval = data.get("texnik_jadval", {})

    jami_min = 0
    jami_max = 0
    ishlar = []

    for nomi, info in jadval.items():
        interval_km = info.get("interval_km", 0) or 0
        interval_yil = info.get("interval_yil", 0) or 0
        narx_min = info.get("narx_min", 0)
        narx_max = info.get("narx_max", 0)

        # Yilga necha marta (20000 km/yil deb hisoblaymiz)
        if interval_km > 0:
            marta = max(1, round(20000 / interval_km))
        elif interval_yil > 0:
            marta = max(1, round(1 / interval_yil))
        else:
            marta = 1

        jami_min += narx_min * marta
        jami_max += narx_max * marta
        if narx_min > 0:
            ishlar.append({
                "nomi": nomi,
                "marta": marta,
                "narx_min": narx_min * marta,
                "narx_max": narx_max * marta,
            })

    return {
        "ishlar": sorted(ishlar, key=lambda x: x["narx_max"], reverse=True),
        "jami_min": jami_min,
        "jami_max": jami_max,
    }


def progress_hisob(joriy_km: int, keyingi_km: int, oldingi_km: int) -> int:
    """Moy almashtirish progressini foizda hisoblash"""
    if keyingi_km <= oldingi_km:
        return 100
    interval = keyingi_km - oldingi_km
    o_tilgan = joriy_km - oldingi_km
    foiz = (o_tilgan / interval) * 100
    return min(100, max(0, int(foiz)))


def km_yangilaganda_eslatmalar(rusum: str, moy_turi: str,
                                eski_km: int, yangi_km: int,
                                kunlik_km: int) -> list:
    """
    Km yangilanganda qaysi eslatmalar yaqinlashganini tekshirish.
    Qaytaradi: ogohlantirish kerak bo'lgan eslatmalar
    """
    data = mashina_data_olish(rusum)
    jadval = data.get("texnik_jadval", {})
    ogohlantirishlar = []

    for nomi, info in jadval.items():
        interval_km = info.get("interval_km")
        if not interval_km:
            continue

        # Har bir interval uchun keyingi maqsad km
        # (oddiy hisob: yangi_km ga eng yaqin keyingi interval)
        keyingi = ((yangi_km // interval_km) + 1) * interval_km
        qolgan = keyingi - yangi_km

        # 500 km dan kam qolsa ogohlantirish
        if qolgan <= 500:
            ogohlantirishlar.append({
                "nomi": nomi,
                "km_da": keyingi,
                "qolgan_km": qolgan,
                "narx_min": info.get("narx_min", 0),
                "narx_max": info.get("narx_max", 0),
            })

    return ogohlantirishlar
