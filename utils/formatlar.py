# ============================================================
# utils/formatlar.py — Xabarlarni formatlash
# ============================================================

from datetime import date


def son_format(son: int) -> str:
    """1234567 → 1,234,567"""
    return f"{son:,}".replace(",", " ")


def narx_format(narx_min: int, narx_max: int) -> str:
    if narx_min == 0 and narx_max == 0:
        return "—"
    return f"{son_format(narx_min)} – {son_format(narx_max)} so'm"


def mashina_sarlavha(rusum: str, yil: int, dvigatel: str) -> str:
    return f"🚗 {rusum} {yil} ({dvigatel}L)"


def km_format(km: int) -> str:
    return f"{son_format(km)} km"


def sana_format(sana_str: str) -> str:
    """2025-07-15 → 15 Iyul 2025"""
    oylar = {
        1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel",
        5: "May", 6: "Iyun", 7: "Iyul", 8: "Avgust",
        9: "Sentyabr", 10: "Oktyabr", 11: "Noyabr", 12: "Dekabr",
    }
    try:
        d = date.fromisoformat(sana_str)
        return f"{d.day} {oylar[d.month]} {d.year}"
    except Exception:
        return sana_str


def qolgan_kun(sana_str: str) -> str:
    try:
        d = date.fromisoformat(sana_str)
        kunlar = (d - date.today()).days
        if kunlar < 0:
            return "⚠️ O'tib ketgan"
        elif kunlar == 0:
            return "🔴 BUGUN"
        elif kunlar <= 3:
            return f"🔴 {kunlar} kun qoldi"
        elif kunlar <= 7:
            return f"🟡 {kunlar} kun qoldi"
        elif kunlar <= 30:
            return f"🟢 {kunlar} kun qoldi"
        else:
            return f"✅ {kunlar} kun qoldi"
    except Exception:
        return ""


def eslatma_xabar(eslatma: dict, mashina: dict) -> str:
    """Eslatma xabarini formatlash"""
    rusum = mashina.get("rusum", "")
    yil = mashina.get("yil", "")
    dvigatel = mashina.get("dvigatel", "")
    joriy_km = mashina.get("joriy_km", 0)

    nomi = eslatma.get("nomi", "")
    km_da = eslatma.get("km_da")
    sana_str = eslatma.get("sana", "")

    lines = [
        f"🔧 {nomi.upper()}",
        f"━━━━━━━━━━━━━━━━━━━",
        f"🚗 {rusum} {yil} ({dvigatel}L)",
        f"📍 Joriy km: {km_format(joriy_km)}",
    ]

    if km_da:
        qolgan = km_da - joriy_km
        lines.append(f"🎯 Kerak km: {km_format(km_da)}")
        if qolgan <= 0:
            lines.append("⚠️ VAQTI KELDI yoki O'TIB KETDI!")
        elif qolgan <= 300:
            lines.append(f"🔴 Qoldi: {km_format(qolgan)} (juda yaqin!)")
        elif qolgan <= 1000:
            lines.append(f"🟡 Qoldi: {km_format(qolgan)}")
        else:
            lines.append(f"🟢 Qoldi: {km_format(qolgan)}")

    if sana_str:
        lines.append(f"📅 Taxminiy sana: {sana_format(sana_str)}")
        lines.append(qolgan_kun(sana_str))

    lines.append("━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)


def jadval_xabar(eslatmalar: list, mashina: dict, davr: str = "bu_oy") -> str:
    """Jadval xabarini formatlash"""
    rusum = mashina.get("rusum", "")
    yil = mashina.get("yil", "")

    bugun = date.today()

    if davr == "bu_oy":
        sarlavha = f"📅 {_oy_nomi(bugun.month)} {bugun.year} — {rusum} {yil}"
    elif davr == "keyingi_oy":
        keyingi = date(bugun.year, bugun.month % 12 + 1, 1) if bugun.month < 12 else date(bugun.year + 1, 1, 1)
        sarlavha = f"📅 {_oy_nomi(keyingi.month)} {keyingi.year} — {rusum} {yil}"
    else:
        sarlavha = f"📅 {bugun.year} yillik jadval — {rusum} {yil}"

    lines = [sarlavha, "━━━━━━━━━━━━━━━━━━━"]

    if not eslatmalar:
        lines.append("✅ Bu davrda rejalashtirilgan ish yo'q")
    else:
        for e in eslatmalar:
            nomi = e.get("nomi", "")
            sana_str = e.get("sana", "")
            km_da = e.get("km_da")
            tasdiqlandi = e.get("tasdiqlandi", 0)

            status = "✅" if tasdiqlandi else "📌"
            km_str = f" ({km_format(km_da)})" if km_da else ""
            sana_str_f = sana_format(sana_str) if sana_str else ""

            lines.append(f"{status} {sana_str_f}  {nomi}{km_str}")

    lines.append("━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)


def xarajat_xabar(xarajat: dict, mashina: dict) -> str:
    """Xarajat hisobini formatlash"""
    rusum = mashina.get("rusum", "")
    yil = mashina.get("yil", "")

    lines = [
        f"💰 Rejalashtirilgan xarajat",
        f"🚗 {rusum} {yil}",
        "━━━━━━━━━━━━━━━━━━━",
    ]

    ishlar = xarajat.get("ishlar", [])
    if not ishlar:
        lines.append("✅ Bu davrda xarajat rejalashtirilmagan")
    else:
        for ish in ishlar:
            nomi = ish.get("nomi", "")
            narx_min = ish.get("narx_min", 0)
            narx_max = ish.get("narx_max", 0)
            lines.append(f"🔧 {nomi}")
            lines.append(f"   {narx_format(narx_min, narx_max)}")

    lines.append("━━━━━━━━━━━━━━━━━━━")
    jami_min = xarajat.get("jami_min", 0)
    jami_max = xarajat.get("jami_max", 0)
    if jami_min or jami_max:
        lines.append(f"💵 Jami taxmin: {narx_format(jami_min, jami_max)}")

    return "\n".join(lines)


def tarix_xabar(tarix: list, mashina: dict) -> str:
    """Servis tarixi xabarini formatlash"""
    rusum = mashina.get("rusum", "")
    yil = mashina.get("yil", "")

    lines = [
        f"📋 Servis tarixi",
        f"🚗 {rusum} {yil}",
        "━━━━━━━━━━━━━━━━━━━",
    ]

    if not tarix:
        lines.append("📭 Hali hech narsa yozilmagan")
    else:
        jami = 0
        for yozuv in tarix:
            nomi = yozuv.get("nomi", "")
            sana_str = yozuv.get("sana", "")
            km = yozuv.get("km", 0)
            narx = yozuv.get("narx", 0)
            jami += narx

            narx_str = f"  💵 {son_format(narx)} so'm" if narx else ""
            km_str = f"  {km_format(km)}" if km else ""
            lines.append(f"✅ {sana_format(sana_str)}  {nomi}{km_str}{narx_str}")

        lines.append("━━━━━━━━━━━━━━━━━━━")
        if jami:
            lines.append(f"💰 Jami: {son_format(jami)} so'm")

    return "\n".join(lines)


def belgi_xabar(belgi_info: dict) -> str:
    """Belgi diagnostika xabarini formatlash"""
    lines = [
        f"{belgi_info.get('emoji', '⚠️')} {belgi_info.get('nomi', '').upper()}",
        "━━━━━━━━━━━━━━━━━━━",
        f"📋 Sabab: {belgi_info.get('tavsif', '')}",
        f"🚨 Xavf darajasi: {belgi_info.get('xavf', '')}",
        "━━━━━━━━━━━━━━━━━━━",
        "📌 Nima qilish kerak:",
    ]
    for i, qadam in enumerate(belgi_info.get("nima_qilish", []), 1):
        lines.append(f"{i}. {qadam}")

    ogohlantiris = belgi_info.get("ogohlantiris")
    if ogohlantiris:
        lines.append("━━━━━━━━━━━━━━━━━━━")
        lines.append(ogohlantiris)

    return "\n".join(lines)


def mavsumiy_xabar(mavsum: str, tekshiruvlar: list, rusum: str) -> str:
    if mavsum == "yoz":
        sarlavha = "☀️ YOZ MAVSUMI TEKSHIRUVI"
    else:
        sarlavha = "❄️ QISH TAYYORGARLIGI"

    lines = [
        sarlavha,
        f"🚗 {rusum}",
        "━━━━━━━━━━━━━━━━━━━",
    ]
    for tekshiruv in tekshiruvlar:
        lines.append(f"☑️ {tekshiruv}")

    lines.append("━━━━━━━━━━━━━━━━━━━")
    lines.append("Hammasini tekshirdingizmi?")
    return "\n".join(lines)


def _oy_nomi(oy: int) -> str:
    oylar = {
        1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel",
        5: "May", 6: "Iyun", 7: "Iyul", 8: "Avgust",
        9: "Sentyabr", 10: "Oktyabr", 11: "Noyabr", 12: "Dekabr",
    }
    return oylar.get(oy, "")
