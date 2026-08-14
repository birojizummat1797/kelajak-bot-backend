import os
import json
import httpx
from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv

import models
from database import engine, get_db

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = "https://kelajak-bot-frontend.vercel.app"  # O'zingizning Vercel domeningiz

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

user_test_state = {}

# 📋 GIBRID DIAGNOSTIKA SAVOLLARI (10 TA)
QUESTIONS = [
    {
        "text": "<b>1-savol:</b> Bo'sh vaqtingizda oldingizda 4 ta loyiha turibdi. Qaysi birini tanlaysiz?",
        "options": [
            {"text": "A) Boshqotirma yechish, tizim yoki kod yozish 💻", "val": "A"},
            {"text": "B) Chiroyli dizayn yoki vizual asar yaratish 🎨", "val": "B"},
            {"text": "C) Jamoa bilan muloqot va yangi g'oyalarni muhokama qilish 🗣", "val": "C"},
            {"text": "D) Hujjatlarni va jarayonlarni tartibga keltirish 📋", "val": "D"}
        ]
    },
    {
        "text": "<b>2-savol:</b> Qanday turdagi kitoblar/ma'lumotlar sizni ko'proq jalb qiladi?",
        "options": [
            {"text": "A) Texnologiyalar va ilmiy kashfiyotlar 🚀", "val": "A"},
            {"text": "B) San'at, psixologiya va ijod sirlari 🎭", "val": "B"},
            {"text": "C) Biznes, marketing va liderlik 📈", "val": "C"},
            {"text": "D) Taym-menejment va shaxsiy samaradorlik ⏳", "val": "D"}
        ]
    },
    {
        "text": "<b>3-savol:</b> Jamoaviy ishda siz odatda qanday rolni tanlaysiz?",
        "options": [
            {"text": "A) \"Miya\" – texnik va mantiqiy yechim topuvchi 🧩", "val": "A"},
            {"text": "B) \"Yurak\" – kreativlik va go'zallik kirituvchi 🎨", "val": "B"},
            {"text": "C) \"Lider\" – hammani birlashtirib, yo'l ko'rsatuvchi 🚩", "val": "C"},
            {"text": "D) \"Nazoratchi\" – ishlarni vaqtida bitishini ta'minlovchi ⏱", "val": "D"}
        ]
    },
    {
        "text": "<b>4-savol:</b> Kutilmagan muammoga duch keldingiz. Birinchi reaksiyangiz qanday?",
        "options": [
            {"text": "A) Muammoning mantiqiy ildizini (bug) qidiraman 🔍", "val": "A"},
            {"text": "B) Yangicha, nostandart yechim o'ylab topaman 💡", "val": "B"},
            {"text": "C) Boshqalar bilan maslahatlashib, birga hal qilaman 👥", "val": "C"},
            {"text": "D) Yo'riqnoma va qoidalarga qarab harakat qilaman 📖", "val": "D"}
        ]
    },
    {
        "text": "<b>5-savol:</b> Siz uchun eng ideal ish muhiti qanday?",
        "options": [
            {"text": "A) Tinch, sokin, kompyuterim bilan yolg'iz 🎧", "val": "A"},
            {"text": "B) Ilhom beruvchi, erkin va ijodiy muhit 🌈", "val": "B"},
            {"text": "C) Odamlar gavjum, muzokaralar qaynaydigan joy 🏢", "val": "C"},
            {"text": "D) Har bir narsa o'z joyida bo'lgan, qat'iy tartibli ofis 📁", "val": "D"}
        ]
    },
    {
        "text": "<b>6-savol:</b> Ishingizda siz uchun eng muhim qadriyat nima?",
        "options": [
            {"text": "A) Intellektual o'sish va yangi texnologiyalar 📈", "val": "A"},
            {"text": "B) O'z g'oyalarimni erkin namoyon etish 🕊", "val": "B"},
            {"text": "C) Jamiyatga ta'sir qilish va tanilish 🌟", "val": "C"},
            {"text": "D) Barqarorlik, aniqlik va xotirjamlik ⚓️", "val": "D"}
        ]
    },
    {
        "text": "<b>7-savol:</b> Hozirgi yo'lingizni (kasb/o'qish) tanlashda eng katta ta'sir kim/nima bo'lgan?",
        "options": [
            {"text": "Shaxsan o'zimning qiziqishim", "val": "CustDev"},
            {"text": "Ota-onam yoki oilam", "val": "CustDev"},
            {"text": "Ustozlar yoki do'stlarim", "val": "CustDev"},
            {"text": "Daromad, obro' yoki tasodif", "val": "CustDev"}
        ]
    },
    {
        "text": "<b>8-savol:</b> Kasb bo'yicha noto'g'ri qaror qilganingizni his qilgan paytingiz bo'lganmi? Agar bo'lsa, bu asosan nima yo'qotishga olib keldi?",
        "options": [
            {"text": "Vaqt (yillarim ketdi)", "val": "CustDev"},
            {"text": "Pul (samarasiz kurs/kontrakt)", "val": "CustDev"},
            {"text": "Motivatsiya va asablarim", "val": "CustDev"},
            {"text": "Bunday holat bo'lmagan", "val": "CustDev"}
        ]
    },
    {
        "text": "<b>9-savol:</b> Hozirgi holatingizda aynan nimani bilishni eng ko'p xohlardingiz?",
        "options": [
            {"text": "Menga mos aniq kasblar ro'yxatini", "val": "CustDev"},
            {"text": "O'z qobiliyatim va kuchli tomonlarimni", "val": "CustDev"},
            {"text": "Qaysi sohada tezroq ish topish mumkinligini", "val": "CustDev"},
            {"text": "Qayerdan va qanday ta'lim olishni", "val": "CustDev"}
        ]
    },
    {
        "text": "<b>10-savol (Yakuniy):</b> Agar sizga qobiliyatingizga to'liq mos kasblar va aniq qadamlar ko'rsatilgan \"Shaxsiy Yo'l Xaritasi\" (PDF) tayyorlab berilsa, bunday yordam uchun pul to'lashga tayyor bo'larmidingiz?",
        "options": [
            {"text": "Sifatiga qarab to'lashim mumkin 💳", "val": "Monetize"},
            {"text": "Hozir pul to'lashga tayyorman 💰", "val": "Monetize"},
            {"text": "Faqat bepul bo'lsa foydalanaman 🎁", "val": "Monetize"},
            {"text": "Hozircha kerak emas ✋", "val": "Monetize"}
        ]
    }
]

# ⚡️ TELEGRAM API FUNKSIYALARI
async def send_message(chat_id: int, text: str, reply_markup: dict = None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

async def edit_message(chat_id: int, message_id: int, text: str, reply_markup: dict = None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

# 📄 PDF YUBORISH FUNKSIYASI
async def send_document(chat_id: int, document_id: str, caption: str = ""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    payload = {"chat_id": chat_id, "document": document_id, "caption": caption, "parse_mode": "HTML"}
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

# 🤖 YAGONA VA TOZA WEBHOOK
@app.post("/webhook")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    
    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        
        if "text" in msg and msg["text"] == "/start":
            keyboard = {
                "keyboard": [[{"text": "🎯 Holatni aniqlash (1-bosqich)", "web_app": {"url": WEBAPP_URL}}]],
                "resize_keyboard": True
            }
            await send_message(chat_id, "👋 Assalomu alaykum!\nPastdagi tugmani bosib, dastlabki holatingizni aniqlang:", keyboard)
            
        elif "web_app_data" in msg:
            try:
                raw_data = msg["web_app_data"]["data"]
                parsed = json.loads(raw_data)
                name = parsed.get("name", "Noma'lum")
                
                success_text = (
                    f"✅ Rahmat, <b>{name}</b>! Sizning holatingizni tahlil qildik.\n\n"
                    f"Aynan sizga qaysi kasb mos kelishini aniqlash va <b>Shaxsiy Yo'l xaritangizni</b> "
                    f"yaratish uchun 10 savollik Chuqur Diagnostikani boshlaymiz.\n\n👇 Tayyor bo'lsangiz, tugmani bosing!"
                )
                keyboard = {"inline_keyboard": [[{"text": "🚀 Diagnostikani boshlash", "callback_data": "start_test"}]]}
                await send_message(chat_id, success_text, keyboard)
            except Exception as e:
                print("Xatolik:", e)
                
    elif "callback_query" in data:
        cb = data["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        message_id = cb["message"]["message_id"]
        cb_data = cb["data"] 
        
        if cb_data == "start_test":
            user_test_state[chat_id] = {"step": 0, "profile_answers": []}
            q = QUESTIONS[0]
            keyboard = {"inline_keyboard": [[{"text": opt["text"], "callback_data": f"ans_0_{idx}"}] for idx, opt in enumerate(q["options"])]}
            await edit_message(chat_id, message_id, q["text"], keyboard)
            
        elif cb_data.startswith("ans_"):
            if chat_id not in user_test_state:
                await send_message(chat_id, "Iltimos, testni qaytadan boshlang (/start).")
                return {"status": "ok"}
                
            parts = cb_data.split("_")
            step = int(parts[1])
            opt_idx = int(parts[2])
            selected_val = QUESTIONS[step]["options"][opt_idx]["val"]
            
            if selected_val in ["A", "B", "C", "D"]:
                user_test_state[chat_id]["profile_answers"].append(selected_val)
                
            next_step = step + 1
            user_test_state[chat_id]["step"] = next_step
            
            if next_step < len(QUESTIONS):
                q = QUESTIONS[next_step]
                keyboard = {"inline_keyboard": [[{"text": opt["text"], "callback_data": f"ans_{next_step}_{idx}"}] for idx, opt in enumerate(q["options"])]}
                await edit_message(chat_id, message_id, q["text"], keyboard)
                
            else:
                profile = user_test_state[chat_id]["profile_answers"]
                a_count = profile.count("A")
                b_count = profile.count("B")
                c_count = profile.count("C")
                d_count = profile.count("D")
                
                counts = {"A": a_count, "B": b_count, "C": c_count, "D": d_count}
                best_match = max(counts, key=counts.get)
                
                # ----------------------------------------------------
                # DIQQAT: SHU YERGA O'ZINGIZNING FILE ID'LARINGIZNI QO'YASIZ
                # ----------------------------------------------------
                FILE_ID_DATA_ANALYST = "AgADPaMAAi7z-Us" 
                FILE_ID_UI_UX = "AgADPKMAAi7z-Us"
                FILE_ID_PM = "AgADOqMAAi7z-Us"
                
                file_to_send = None

                if best_match == "A":
                    avatar = "💻 Texnologiyalar va Analitika (Data Analyst)"
                    file_to_send = FILE_ID_DATA_ANALYST
                elif best_match == "B":
                    avatar = "🎨 Kreativ va Dizayn (UX/UI Designer)"
                    file_to_send = FILE_ID_UI_UX
                elif best_match == "C":
                    avatar = "🗣 Boshqaruv va Muloqot (Project Manager)"
                    file_to_send = FILE_ID_PM
                else:
                    avatar = "📋 Tizim va Tartib (QA / Biznes Analitik)"
                    file_to_send = None # D uchun PDF hali tayyor emas
                
                result_text = (
                    f"🎉 <b>Diagnostika muvaffaqiyatli yakunlandi!</b>\n\n"
                    f"Sizning javoblaringiz tahlil qilinib, eng kuchli fitratingiz aniqlandi:\n"
                    f"👉 <b>{avatar}</b>\n\n"
                    f"<i>Siz uchun maxsus tayyorlangan Shaxsiy Yo'l Xaritasini (PDF) qabul qiling! 👇</i>"
                )
                
                # 1. Matnni yangilaymiz
                await edit_message(chat_id, message_id, result_text)
                
                # 2. PDF faylni jo'natamiz (Agar fayl ID kiritilgan bo'lsa)
                if file_to_send and file_to_send != "SHU_YERGA_FILE_ID_YOZILADI":
                    await send_document(chat_id, file_to_send, f"🔥 Sizning Shaxsiy Yo'l xaritangiz: {avatar}")
                elif best_match == "D":
                    await send_message(chat_id, "📋 Tizim va Tartib yo'nalishi bo'yicha PDF xarita tayyorlanmoqda. Tez orada sizga yuboramiz!")
                
                del user_test_state[chat_id]

    return {"status": "ok"}