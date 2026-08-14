import os
import json
import httpx
import asyncio
from datetime import datetime
from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv

import gspread
from google.oauth2.service_account import Credentials

import models
from database import engine, get_db

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = "https://kelajak-bot-frontend.vercel.app" 

# Google Sheets sozlamalari
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
CREDS_JSON = os.getenv("GOOGLE_CREDENTIALS")

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
user_test_state = {}
http_client = httpx.AsyncClient(timeout=15.0)

# 📋 GIBRID DIAGNOSTIKA SAVOLLARI (10 TA)
QUESTIONS = [
    {
        "text": "<b>1-savol:</b> Bo'sh vaqtingizda oldingizda 4 ta loyiha turibdi. Qaysi birini tanlaysiz?",
        "options": [
            {"text": "A) Boshqotirma, tizim yoki kod 💻", "val": "A"},
            {"text": "B) Dizayn yoki vizual asar 🎨", "val": "B"},
            {"text": "C) Muloqot va yangi g'oyalar 🗣", "val": "C"},
            {"text": "D) Hujjatlar va tartib 📋", "val": "D"}
        ]
    },
    {
        "text": "<b>2-savol:</b> Qanday turdagi ma'lumotlar sizni jalb qiladi?",
        "options": [
            {"text": "A) Texnologiyalar va kashfiyotlar 🚀", "val": "A"},
            {"text": "B) San'at va ijod sirlari 🎭", "val": "B"},
            {"text": "C) Biznes va liderlik 📈", "val": "C"},
            {"text": "D) Taym-menejment va tartib ⏳", "val": "D"}
        ]
    },
    {
        "text": "<b>3-savol:</b> Jamoaviy ishda qanday rolni tanlaysiz?",
        "options": [
            {"text": "A) Mantiqiy yechim topuvchi 🧩", "val": "A"},
            {"text": "B) Kreativlik kirituvchi 🎨", "val": "B"},
            {"text": "C) Yo'l ko'rsatuvchi lider 🚩", "val": "C"},
            {"text": "D) Nazoratchi ⏱", "val": "D"}
        ]
    },
    {
        "text": "<b>4-savol:</b> Muammoga birinchi reaksiyangiz?",
        "options": [
            {"text": "A) Mantiqiy ildizini qidiraman 🔍", "val": "A"},
            {"text": "B) Nostandart yechim o'ylayman 💡", "val": "B"},
            {"text": "C) Maslahatlashib hal qilaman 👥", "val": "C"},
            {"text": "D) Qoidalarga qarab harakat qilaman 📖", "val": "D"}
        ]
    },
    {
        "text": "<b>5-savol:</b> Siz uchun eng ideal ish muhiti?",
        "options": [
            {"text": "A) Sokin, kompyuterim bilan yolg'iz 🎧", "val": "A"},
            {"text": "B) Ilhom beruvchi erkin muhit 🌈", "val": "B"},
            {"text": "C) Odamlar gavjum joy 🏢", "val": "C"},
            {"text": "D) Qat'iy tartibli ofis 📁", "val": "D"}
        ]
    },
    {
        "text": "<b>6-savol:</b> Ishdagi eng muhim qadriyatingiz?",
        "options": [
            {"text": "A) Yangi texnologiyalar o'rganish 📈", "val": "A"},
            {"text": "B) O'z g'oyalarimni namoyon etish 🕊", "val": "B"},
            {"text": "C) Jamiyatga ta'sir qilish 🌟", "val": "C"},
            {"text": "D) Barqarorlik va aniqlik ⚓️", "val": "D"}
        ]
    },
    {
        "text": "<b>7-savol:</b> Kasb tanlashda eng katta ta'sir kim/nima bo'lgan?",
        "options": [
            {"text": "Shaxsan o'zimning qiziqishim", "val": "CustDev"},
            {"text": "Ota-onam yoki oilam", "val": "CustDev"},
            {"text": "Ustozlar yoki do'stlarim", "val": "CustDev"},
            {"text": "Daromad, obro' yoki tasodif", "val": "CustDev"}
        ]
    },
    {
        "text": "<b>8-savol:</b> Noto'g'ri qaroringiz qanday yo'qotishga olib keldi?",
        "options": [
            {"text": "Vaqt (yillarim ketdi)", "val": "CustDev"},
            {"text": "Pul (samarasiz kurs/kontrakt)", "val": "CustDev"},
            {"text": "Motivatsiya va asablarim", "val": "CustDev"},
            {"text": "Bunday holat bo'lmagan", "val": "CustDev"}
        ]
    },
    {
        "text": "<b>9-savol:</b> Hozir nimani bilishni ko'proq xohlaysiz?",
        "options": [
            {"text": "Menga mos kasblar ro'yxatini", "val": "CustDev"},
            {"text": "O'z kuchli tomonlarimni", "val": "CustDev"},
            {"text": "Qaysi sohada ish topish osonligini", "val": "CustDev"},
            {"text": "Qayerdan ta'lim olishni", "val": "CustDev"}
        ]
    },
    {
        "text": "<b>10-savol:</b> Agar sizga aniq qadamli \"Shaxsiy Yo'l Xaritasi\" tayyorlansa, to'lov qilishga tayyormisiz?",
        "options": [
            {"text": "Sifatiga qarab to'lashim mumkin 💳", "val": "Monetize"},
            {"text": "Hozir pul to'lashga tayyorman 💰", "val": "Monetize"},
            {"text": "Faqat bepul bo'lsa foydalanaman 🎁", "val": "Monetize"},
            {"text": "Hozircha kerak emas ✋", "val": "Monetize"}
        ]
    }
]

# 📝 GOOGLE JADVALGA YOZISH FUNKSIYASI
def append_to_sheet(name, phone, result_text, payment_intent):
    try:
        if not CREDS_JSON or not SHEET_ID:
            print("Google kalitlari topilmadi!")
            return
            
        creds_dict = json.loads(CREDS_JSON)
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).sheet1
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([now, name, phone, result_text, payment_intent])
        print(f"Jadvalga yozildi: {name}")
    except Exception as e:
        print(f"Google Sheets xatosi: {e}")

# ⚡️ TELEGRAM API FUNKSIYALARI
async def send_message(chat_id: int, text: str, reply_markup: dict = None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup: payload["reply_markup"] = reply_markup
    try: await http_client.post(url, json=payload)
    except: pass

async def edit_message(chat_id: int, message_id: int, text: str, reply_markup: dict = None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML"}
    if reply_markup: payload["reply_markup"] = reply_markup
    try: await http_client.post(url, json=payload)
    except: pass

async def send_document(chat_id: int, document_id: str, caption: str = ""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    payload = {"chat_id": chat_id, "document": document_id, "caption": caption, "parse_mode": "HTML"}
    try: await http_client.post(url, json=payload)
    except: pass

async def answer_callback(callback_id: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
    try: await http_client.post(url, json={"callback_query_id": callback_id})
    except: pass

# 🤖 WEBHOOK
@app.post("/webhook")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    try: data = await request.json()
    except: return {"status": "ok"}
    
    if "message" in data:
        msg = data["message"]
        chat_id = msg.get("chat", {}).get("id")
        if not chat_id: return {"status": "ok"}
        
        if "text" in msg and msg["text"] == "/start":
            keyboard = {"keyboard": [[{"text": "🎯 Holatni aniqlash (1-bosqich)", "web_app": {"url": WEBAPP_URL}}]], "resize_keyboard": True}
            await send_message(chat_id, "👋 Assalomu alaykum!\nPastdagi tugmani bosib, dastlabki holatingizni aniqlang:", keyboard)
            
        elif "document" in msg:
            doc_id = msg["document"]["file_id"]
            doc_name = msg["document"].get("file_name", "Noma'lum fayl")
            await send_message(chat_id, f"✅ <b>{doc_name}</b> qabul qilindi!\n\nSizning FILE ID kodingiz:\n<code>{doc_id}</code>")
            
        elif "web_app_data" in msg:
            try:
                raw_data = msg["web_app_data"]["data"]
                parsed = json.loads(raw_data)
                name = parsed.get("name", "Noma'lum")
                
                success_text = (
                    f"✅ Rahmat, <b>{name}</b>!\n\n"
                    f"Aynan sizga qaysi kasb mos kelishini aniqlash va <b>Shaxsiy Yo'l xaritangizni</b> "
                    f"yaratish uchun 10 savollik Diagnostikani boshlaymiz.\n\n👇 Tayyor bo'lsangiz, tugmani bosing!"
                )
                keyboard = {"inline_keyboard": [[{"text": "🚀 Diagnostikani boshlash", "callback_data": "start_test"}]]}
                await send_message(chat_id, success_text, keyboard)
            except Exception as e:
                print("Xatolik WebApp:", e)
                
    elif "callback_query" in data:
        cb = data["callback_query"]
        cb_id = cb["id"]
        chat_id = cb["message"]["chat"]["id"]
        message_id = cb["message"]["message_id"]
        cb_data = cb["data"] 
        
        await answer_callback(cb_id)
        
        try:
            if cb_data == "start_test":
                user_test_state[chat_id] = {"step": 0, "profile_answers": [], "all_answers": {}}
                q = QUESTIONS[0]
                keyboard = {"inline_keyboard": [[{"text": opt["text"], "callback_data": f"ans_0_{idx}"}] for idx, opt in enumerate(q["options"])]}
                await edit_message(chat_id, message_id, q["text"], keyboard)
                
            elif cb_data.startswith("ans_"):
                if chat_id not in user_test_state:
                    await send_message(chat_id, "⚠️ Iltimos, testni qaytadan boshlang (/start).")
                    return {"status": "ok"}
                    
                parts = cb_data.split("_")
                step = int(parts[1])  
                opt_idx = int(parts[2])
                
                if step != user_test_state[chat_id]["step"]:
                    return {"status": "ok"}
                
                selected_val = QUESTIONS[step]["options"][opt_idx]["val"]
                selected_text = QUESTIONS[step]["options"][opt_idx]["text"]
                
                # Barcha javoblarni saqlaymiz (Jadval uchun)
                user_test_state[chat_id]["all_answers"][step] = selected_text
                
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
                    
                    # ⚠️ O'ZINGIZNING FILE ID LARINGIZNI QO'YISHNI UNUTMANG !!!
                    FILE_ID_DATA_ANALYST = "SHU_YERGA_FILE_ID_YOZILADI" 
                    FILE_ID_UI_UX = "SHU_YERGA_FILE_ID_YOZILADI"
                    FILE_ID_PM = "SHU_YERGA_FILE_ID_YOZILADI"
                    
                    file_to_send = None

                    if best_match == "A":
                        avatar = "💻 Data Analyst (Ma'lumotlar Tahlilchisi)"
                        file_to_send = FILE_ID_DATA_ANALYST
                    elif best_match == "B":
                        avatar = "🎨 UX/UI Designer (Dizayner)"
                        file_to_send = FILE_ID_UI_UX
                    elif best_match == "C":
                        avatar = "🗣 Project Manager (Boshqaruvchi)"
                        file_to_send = FILE_ID_PM
                    else:
                        avatar = "📋 Tizim va Tartib"
                        file_to_send = None
                    
                    result_text = (
                        f"🎉 <b>Diagnostika yakunlandi!</b>\n\n"
                        f"👉 Eng kuchli moslik: <b>{avatar}</b>\n\n"
                        f"<i>Siz uchun Shaxsiy Yo'l Xaritasi (PDF) tayyorlandi! 👇</i>"
                    )
                    
                    await edit_message(chat_id, message_id, result_text)
                    
                    if file_to_send and file_to_send != "SHU_YERGA_FILE_ID_YOZILADI":
                        await send_document(chat_id, file_to_send, f"🔥 Sizning Shaxsiy Yo'l xaritangiz: {avatar}")
                    else:
                        await send_message(chat_id, "⚠️ <i>(Eslatma: Hozircha bu yo'nalish uchun PDF fayl tayyorlanmoqda.)</i>")
                    
                    # ----------------------------------------------------
                    # 📊 GOOGLE SHEETS GA MA'LUMOTLARNI YUBORISH
                    # ----------------------------------------------------
                    payment_intent = user_test_state[chat_id]["all_answers"].get(9, "Noma'lum")
                    user = db.query(models.User).filter(models.User.telegram_id == str(chat_id)).first()
                    u_name = user.full_name if user else "Noma'lum"
                    u_phone = user.phone_number if user else "Noma'lum"
                    
                    # Jadvalga yozish jarayoni botni qotirib qo'ymasligi uchun orqa fonda (thread) ishlatamiz
                    asyncio.create_task(asyncio.to_thread(append_to_sheet, u_name, u_phone, avatar, payment_intent))
                    
                    del user_test_state[chat_id]

        except Exception as e:
            print("Callback Xatosi:", e)

    return {"status": "ok"}