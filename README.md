# 🚗 AvtoServis Bot

O'zbekiston avtomobil egalari uchun texnik xizmat eslatma boti.

## Fayl tuzilmasi

```
autobot/
├── bot.py              ← Asosiy ishga tushirish
├── config.py           ← Token va sozlamalar
├── database.py         ← SQLite operatsiyalar
├── scheduler.py        ← Kunlik eslatmalar
├── requirements.txt    ← Kutubxonalar
│
├── data/
│   ├── nexia.py        ← Nexia texnik baza
│   ├── matiz.py        ← Matiz texnik baza
│   ├── cobalt.py       ← Cobalt texnik baza
│   ├── lacetti.py      ← Lacetti texnik baza
│   └── belgilar.py     ← Diagnostika baza
│
├── handlers/
│   ├── start.py        ← /start va ro'yxat (FSM)
│   ├── menu.py         ← Bosh menyu
│   ├── jadval.py       ← Jadval ko'rish
│   ├── eslatma.py      ← Eslatmaga javob
│   ├── belgi.py        ← Belgi diagnostika
│   ├── xarajat.py      ← Xarajat hisoblash
│   ├── tarix.py        ← Servis tarixi
│   └── admin.py        ← Admin panel
│
└── utils/
    ├── hisoblash.py    ← Jadval generatsiya
    └── formatlar.py    ← Xabar formatlash
```

## Ishga tushirish

### 1. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 2. config.py ni to'ldirish
```python
BOT_TOKEN = "BotFatherdan olgan tokeningiz"
ADMIN_ID = 123456789   # @userinfobot dan oling
ADMIN_PAROL = "o'z parolingiz"
```

### 3. Ishga tushirish
```bash
python bot.py
```

### 4. Railway.app ga yuklash (bepul hosting)
1. GitHub repoga yuklang
2. Railway.app → New Project → GitHub
3. Environment Variables qo'shing:
   - `BOT_TOKEN` = tokeningiz
   - `ADMIN_ID` = telegram id
   - `ADMIN_PAROL` = parolingiz
4. Deploy → tayyor!

## Buyruqlar

| Buyruq | Vazifa |
|--------|--------|
| /start | Ro'yxat yoki bosh menyu |
| /admin | Admin panel (parol kerak) |

## Bosh menyu tugmalari

| Tugma | Vazifa |
|-------|--------|
| 🚗 Mashinalarim | Mashinalar ro'yxati va batafsil |
| 📅 Jadval | Bu oy / keyingi oy / barcha |
| ⚠️ Belgi tekshir | Diagnostika |
| 💰 Xarajat hisob | Bu oy / yillik taxmin |
| 📋 Servis tarixi | Barcha bajarilgan ishlar |
| ⚙️ Sozlamalar | KM yangilash, mashina qo'shish |

## Eslatma vaqtlari

- **08:00** — Bugungi eslatmalar
- **09:00** — 3 kun ichidagi ogohlantirishlar
- **1-Iyun** — Yoz mavsumiy tekshiruv
- **1-Noyabr** — Qish tayyorgarligi

## Qo'llab-quvvatlanadigan rusumlar

- Nexia (1995-2016) — 1.5L, 1.6L
- Matiz (1998-2015) — 0.8L, 1.0L
- Cobalt (2011-hozir) — 1.5L
- Lacetti (2002-2013) — 1.4L, 1.6L, 1.8L
