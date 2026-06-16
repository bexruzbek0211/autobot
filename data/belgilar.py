# ============================================================
# data/belgilar.py — Belgиlar va diagnostika bazasi
# ============================================================

BELGILAR = {
    "lampochka": {
        "nomi": "🔴 Lampochka yondi",
        "turlar": {
            "moy": {
                "nomi": "🔴 Moy bosimi",
                "xavf": "YUQORI",
                "emoji": "🔴",
                "tavsif": "Moy bosimi past yoki nasos muammo",
                "nima_qilish": [
                    "Darhol to'xtating va dvigatelni o'chiring",
                    "Dvigatel sovigandan keyin (20 daqiqa) moy darajasini tekshiring",
                    "Moy kam bo'lsa — to'g'ri markali moy qo'shing",
                    "Darajasi normal bo'lsa — nasos muammo, servisga yuring",
                ],
                "ogohlantiris": "❌ Shu holda haydamang — dvigatel buzilishi mumkin!",
            },
            "harorat": {
                "nomi": "🌡️ Harorat (qizil)",
                "xavf": "YUQORI",
                "emoji": "🔴",
                "tavsif": "Dvigatel qizib ketmoqda",
                "nima_qilish": [
                    "Darhol to'xtating",
                    "Dvigatelni o'chirmang (konditsioner o'chiring)",
                    "Qizib ketgan bo'lsa pechni maksimumga qo'ying",
                    "Antifriz darajasini tekshiring (sovigandan keyin)",
                    "Servisga yoki evakuatorga qo'ng'iroq qiling",
                ],
                "ogohlantiris": "❌ Haydashda davom eting = dvigatel 100% buziladi",
            },
            "akkumulyator": {
                "nomi": "🔋 Akkumulyator",
                "xavf": "O'RTA",
                "emoji": "🔶",
                "tavsif": "Generator ishlamayapti yoki akkumulyator zaryadi past",
                "nima_qilish": [
                    "Elektr jihozlarni o'chiring (konditsioner, radiator va h.)",
                    "Yaqin servisga boring",
                    "Generator yoki akkumulyatorni tekshiring",
                ],
                "ogohlantiris": "⚠️ Mashina to'xtashidan oldin servisga boring",
            },
            "tormoz": {
                "nomi": "🔴 Tormoz tizimi",
                "xavf": "YUQORI",
                "emoji": "🔴",
                "tavsif": "Tormoz suyuqligi kam yoki qo'llanma tormoz yoniq",
                "nima_qilish": [
                    "Avvalo qo'llanma tormoz tushirilganligini tekshiring",
                    "Qo'llanma tormoz tushirilgan bo'lsa — tormoz suyuqligini tekshiring",
                    "Suyuqlik kam bo'lsa — qo'shing va darhol servisga boring",
                    "Tormoz pedali yumshoq bo'lsa — to'xtating!",
                ],
                "ogohlantiris": "❌ Tormoz nosoz bo'lsa haydamang",
            },
            "yoqilgi": {
                "nomi": "⛽ Yoqilgi",
                "xavf": "PAST",
                "emoji": "🟡",
                "tavsif": "Yoqilgi tugayapti",
                "nima_qilish": [
                    "Yaqin AZSga boring",
                    "Benzin to'liq tugasa injektorlar shikastlanishi mumkin",
                    "Lampochka yonishi = ~50 km qoldi (rusumga qarab)",
                ],
                "ogohlantiris": "⚠️ Kechiktirmang — injektorlar uchun yomon",
            },
            "airbag": {
                "nomi": "💥 Airbag",
                "xavf": "O'RTA",
                "emoji": "🔶",
                "tavsif": "Xavfsizlik yostig'i tizimi muammo",
                "nima_qilish": [
                    "Avtodiagnostika cihaziga ulang",
                    "Servisga boring — o'zingiz tuzata olmaysiz",
                    "Avtohalokat bo'lsa yostiq ishlamasligi mumkin",
                ],
                "ogohlantiris": "⚠️ Xavfsizlik tizimi — e'tibor bering",
            },
            "abs": {
                "nomi": "🔴 ABS",
                "xavf": "O'RTA",
                "emoji": "🔶",
                "tavsif": "Blokirovkaga qarshi tizim muammo",
                "nima_qilish": [
                    "Oddiy tormoz ishlaydi — haydashni davom ettirish mumkin",
                    "Lekin sirpanchiq yo'lda ehtiyot bo'ling",
                    "Qulay paytda servisga boring",
                ],
                "ogohlantiris": "⚠️ Favqulodda tormoz qilishda xavfli bo'lishi mumkin",
            },
        },
    },

    "tovush": {
        "nomi": "🔊 G'alati tovush",
        "turlar": {
            "taqillatish": {
                "nomi": "🔨 Taqillatish (dvigatel)",
                "xavf": "YUQORI",
                "tavsif": "Dvigatel ichida muammo",
                "nima_qilish": [
                    "Moy darajasini tekshiring",
                    "Agar tovush kuchli bo'lsa — to'xtating",
                    "Servisga olib boring — ko'p kuting = ko'p xarajat",
                ],
            },
            "gijillash": {
                "nomi": "🎵 Gijillash (tormozda)",
                "xavf": "O'RTA",
                "tavsif": "Tormoz kolodkalari tugayapti",
                "nima_qilish": [
                    "Kolodkalar yupqalanib qolgan",
                    "Imkon boricha tezroq almashtiring",
                    "Kech qolsangiz disk ham shikastlanadi (qimmatroq ta'mirot)",
                ],
            },
            "vizillash": {
                "nomi": "💨 Vizillash (qayishdan)",
                "xavf": "O'RTA",
                "tavsif": "Generator yoki gaz qayishi sirpanmoqda",
                "nima_qilish": [
                    "Qayish tarangligini tekshiring",
                    "Qayish yorilib qolgan bo'lsa — darhol almashtiring",
                    "Gaz qayishi bo'lsa ayniqsa xavfli",
                ],
            },
            "gumbirash": {
                "nomi": "💥 Gumbirash (g'ildirakdan)",
                "xavf": "O'RTA",
                "tavsif": "Temir g'ildirak podshipniki yoki shina muammo",
                "nima_qilish": [
                    "Shinani tekshiring — kamar sindirganmi?",
                    "Podshipnik bo'lsa — tezroq almashtiring",
                    "Tezlikda kuchaysa — podshipnik muammo",
                ],
            },
        },
    },

    "tutun": {
        "nomi": "💨 Tutun chiqmoqda",
        "turlar": {
            "oq_tutun": {
                "nomi": "🤍 Oq tutun (egzozdan)",
                "xavf": "YUQORI",
                "tavsif": "Antifriz yonmoqda — bosh qopqoq muammo bo'lishi mumkin",
                "nima_qilish": [
                    "Antifriz darajasini tekshiring",
                    "Moy emulsiyaga aylangan bo'lsa — bosh qopqoq muammo",
                    "Servisga olib boring — o'zi o'tib ketmaydi",
                ],
                "ogohlantiris": "❌ Kech qolsangiz dvigatel to'liq ta'miri kerak bo'ladi",
            },
            "qora_tutun": {
                "nomi": "🖤 Qora tutun",
                "xavf": "O'RTA",
                "tavsif": "Yoqilgi to'liq yonmayapti",
                "nima_qilish": [
                    "Havo filtri iflos bo'lishi mumkin — tekshiring",
                    "Injektorlar muammo bo'lishi mumkin",
                    "Diagnostika o'tkazing",
                ],
            },
            "ko_k_tutun": {
                "nomi": "💙 Ko'k tutun",
                "xavf": "O'RTA",
                "tavsif": "Dvigatel moy yoqmoqda",
                "nima_qilish": [
                    "Moy sarfini kuzating",
                    "Moy muhrlari shikastlangan bo'lishi mumkin",
                    "Servisga olib boring — diagnostika",
                ],
            },
        },
    },

    "harorat": {
        "nomi": "🌡️ Harorat ko'tarilmoqda",
        "turlar": {
            "tiqilib": {
                "nomi": "Faqat tiqilib qolganda",
                "xavf": "O'RTA",
                "tavsif": "Radiator ventilyatori muammo bo'lishi mumkin",
                "nima_qilish": [
                    "To'xtab konditsionerni o'ching",
                    "Ventilyator ishlayaptimi tekshiring",
                    "Antifriz darajasini tekshiring",
                    "Servisda ventilyator va termostat tekshiring",
                ],
            },
            "doim": {
                "nomi": "Doim ko'tarilmoqda",
                "xavf": "YUQORI",
                "tavsif": "Sovutish tizimi jiddiy muammo",
                "nima_qilish": [
                    "Haydashni to'xtating",
                    "Antifriz va suv darajasini tekshiring",
                    "Servisga evakuator bilan yuboring",
                ],
                "ogohlantiris": "❌ Haydashda davom etmang!",
            },
        },
    },

    "moy_sarfi": {
        "nomi": "🛢️ Moy sarfi ko'paydi",
        "turlar": {
            "tez_kamayish": {
                "nomi": "Tez kamaymoqda (1000 km da 0.5L dan ko'p)",
                "xavf": "O'RTA",
                "tavsif": "Dvigatel moy yoqmoqda yoki sizdiryapti",
                "nima_qilish": [
                    "Mashina ostini tekshiring — sizish bormi",
                    "Egzozdan ko'k tutun bormi",
                    "Diagnostika — muhrlarga qarating",
                    "Shu davr moy darajasini haftada tekshiring",
                ],
            },
        },
    },

    "sizish": {
        "nomi": "💧 Suyuqlik sizmoqda",
        "turlar": {
            "yashil_sariq": {
                "nomi": "Yashil/sariq suyuqlik",
                "xavf": "O'RTA",
                "tavsif": "Antifriz (tosol) sizmoqda",
                "nima_qilish": [
                    "Qayerdan sizayotganini toping",
                    "Antifriz darajasini tekshiring",
                    "Servisda radiator, shlangi tekshiring",
                ],
            },
            "qoramtir": {
                "nomi": "Qora/qo'ng'ir suyuqlik",
                "xavf": "O'RTA",
                "tavsif": "Moy sizmoqda",
                "nima_qilish": [
                    "Moy darajasini tekshiring",
                    "Sizish joyini toping (sifon, muhrlар)",
                    "Servisda muhrlаr va prоkladkani tekshiring",
                ],
            },
            "shaffof": {
                "nomi": "Shaffof suyuqlik",
                "xavf": "PAST",
                "tavsif": "Konditsioner kondensati (normal)",
                "nima_qilish": [
                    "Konditsioner ishlayotganida bu normal",
                    "Boshqa belgi bo'lmasa xavotir olmanа",
                ],
            },
        },
    },
}
