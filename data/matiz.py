# ============================================================
# data/matiz.py — Matiz texnik ma'lumotlar bazasi
# ============================================================

MATIZ_DATA = {
    "rusum": "Matiz",
    "yillar": "1998-2015",
    "dvigateller": ["0.8", "1.0"],
    "moy_intervallari": {
        "mineral":       5000,
        "yarim_sintetik": 7000,
        "sintetik":      8000,
    },
    "texnik_jadval": {
        "Moy + yog filtri": {
            "interval_km": None,
            "tur": "moy",
            "narx_min": 70000,
            "narx_max": 110000,
            "izoh": "Kichik dvigatel — moy sifatiga ayniqsa e'tibor bering",
        },
        "Havo filtri": {
            "interval_km": 10000,
            "tur": "filtr",
            "narx_min": 15000,
            "narx_max": 30000,
            "izoh": "Kichik dvigatel tez ifloslanadi, tez-tez tekshiring",
        },
        "Yoqilgi filtri": {
            "interval_km": 20000,
            "tur": "filtr",
            "narx_min": 15000,
            "narx_max": 25000,
            "izoh": "Karbyurator tizimi uchun muhim",
        },
        "Old tormoz kolodkalari": {
            "interval_km": 25000,
            "tur": "tormoz",
            "narx_min": 80000,
            "narx_max": 150000,
            "izoh": "Yengil mashina — kam eyiladi, lekin kuzating",
        },
        "Orqa baraban": {
            "interval_km": 60000,
            "tur": "tormoz",
            "narx_min": 80000,
            "narx_max": 140000,
            "izoh": "Baraban tizimi — uzoq chidaydi",
        },
        "Korobka moyi": {
            "interval_km": 40000,
            "tur": "moy",
            "narx_min": 60000,
            "narx_max": 100000,
            "izoh": "Mexanik korobka, oddiy moy",
        },
        "Gaz qayishi": {
            "interval_km": 45000,
            "tur": "qayish",
            "narx_min": 80000,
            "narx_max": 150000,
            "izoh": "MUHIM! Uzilsa dvigatel to'xtaydi va shikastlanadi",
        },
        "Generator qayishi": {
            "interval_km": 40000,
            "tur": "qayish",
            "narx_min": 20000,
            "narx_max": 40000,
            "izoh": "Tez-tez tekshirib turing, arzon almashtirish",
        },
        "Antifriz": {
            "interval_km": None,
            "interval_yil": 2,
            "tur": "suyuqlik",
            "narx_min": 35000,
            "narx_max": 60000,
            "izoh": "Kichik sistema — darajani doim kuzating",
        },
        "Buji (sham)": {
            "interval_km": 15000,
            "tur": "elektr",
            "narx_min": 30000,
            "narx_max": 60000,
            "izoh": "3 dona (0.8L) yoki 4 dona (1.0L). Tez-tez almashtiring",
        },
        "Akkumulyator": {
            "interval_km": None,
            "interval_yil": 3,
            "tur": "elektr",
            "narx_min": 280000,
            "narx_max": 450000,
            "izoh": "Kichik akkumulyator — sovuqda zaiflanadi",
        },
        "Amortizatorlar (old)": {
            "interval_km": 70000,
            "tur": "podveska",
            "narx_min": 180000,
            "narx_max": 320000,
            "izoh": "Yomonlashsa salonda tebranish seziladi",
        },
        "Shina aylantirishи": {
            "interval_km": 10000,
            "tur": "shina",
            "narx_min": 20000,
            "narx_max": 40000,
            "izoh": "Old g'ildiraklar tez eyiladi — aylantiring",
        },
    },
    "mavsumiy_tekshiruvlar": {
        "yoz": [
            "Antifriz darajasi (kichik sistema!)",
            "Harorat ko'rsatkichi kuzatish",
            "Shina bosimi",
            "Konditsioner gazi (mavjud bo'lsa)",
        ],
        "qish": [
            "Antifriz -25 ga chidashini tekshiring",
            "Akkumulyator — kichik, sovuqda zaif",
            "Qish rezinasi (kichik mashina uchun muhim)",
            "Oyna suyuqligi",
            "Qotib qolishni oldini olish",
        ],
    },
}
