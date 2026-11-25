# 🤖 Multi-Funksional Telegram Bot (DLS Karta, Ismlar Ma'nosi, Tabrik Video)

Ushbu bot bitta platformada 3 ta ommabop va qiziqarli xizmatni birlashtirgan:

1. ⚽ **DLS Karta Yasash** – O'yinchi ismi, pozitsiyasi (ST, CAM, CB, GK va h.k.), reytingi va rasmi bilan Dream League Soccer (DLS) uslubidagi sifatli oltin futbolchi kartasini yaratadi.
2. 📖 **Ismlar Ma'nosi** – O'zbek, arab, fors va turkiy ismlarning kelib chiqishi va ma'nosini qidirib topib beradi.
3. 🎬 **Tabrik Video Yasash** – Tug'ilgan kun, to'y, bayramlar va ezgu tilaklar uchun ism va matn bilan animatsion tabrik videosi (MP4) yasaydi.

---

## 🚀 Ishga Tushirish Bo'yicha Qo'llanma

### 1. Bot Tokenini o'rnatish
Telegramda [@BotFather](https://t.me/BotFather) botiga kiring va yangi bot yarating (`/newbot`).
Berilgan tokenni oling va uni [config.py](file:///c:/Users/user/Desktop/bot%20imtihon/config.py) faylidagi `BOT_TOKEN` o'zgaruvchisiga yozing:

```python
BOT_TOKEN = "1234567890:ABC-DEF..."
```

### 2. Botni ishga tushirish
Terminal yoki buyruqlar satrida quyidagi buyruqni bering:

```bash
python main.py
```

---

## 📂 Loyiha Fayllari Tuzilishi

* **`main.py`** – Botni ishga tushiruvchi markaziy fayl.
* **`config.py`** – Bot tokeni va papkalar sozlamalari.
* **`handlers/`**:
  * `start.py` – Bosh menyu, `/start` komandasi va umumiy navigatsiya.
  * `dls_card.py` – DLS kartasi yasash jarayoni (FSM orqali bosqichma-bosqich).
  * `names.py` – Ismlar ma'nosini qidirish va tezkor tugmalar.
  * `greeting_video.py` – Tabrik video yaratish va yuborish.
* **`services/`**:
  * `dls_generator.py` – Pillow grafik kutubxonasi orqali DLS kartasini chizish.
  * `names_db.py` – Ismlar lug'ati bazasi.
  * `video_generator.py` – OpenCV orqali animatsion tabrik video generatsiya qilish.

