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
WEBAPP_URL = "https://kelajak-bot-frontend.vercel.app" 

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 🧠 Foydalanuvchilarning testdagi holatini saqlab turuvchi vaqtinchalik xotira
user_test_state = {}

# 📋 DIAGNOSTIKA SAVOLLARI BAZASI
QUESTIONS = [
    {
        "text": "<b>1-savol:</b> Qaysi muhitda ishlash sizga ko'proq zavq beradi?",
        "options": [
            {"text": "A) Odamlar gavjum, jamoaviy muhit 👥", "val": "A"},
            {"text": "B) Sokin, kompyuter va men 💻", "val": "B"},
            {"text": "C) Doimiy harakat va ijod 🎨", "val": "C"},
            {"text": "D) Qat'iy tartib va qoidalar 📊", "val": "D"}
        ]
    },
    {
        "text": "<b>2-savol:</b> Bo'sh vaqtingizda nima qilishni yoqtirasiz?",
        "options": [
            {"text": "A) Do'stlar bilan suhbatlashish 🗣", "val": "A"},
            {"text": "B) Yangi texnologiyalarni o'rganish 📱", "val": "B"},
            {"text": "C) Nimadir yasash, chizish 🖌", "val": "C"},
            {"text": "D) Kitob o'qish, faktlarni tahlil qilish 📖", "val": "D"}
        ]
    },
    {
        "text": "<b>3-savol:</b> Kelajakdagi daromadingiz qanday bo'lishini xohlaysiz?",
        "options": [
            {"text": "A) Barqaror oylik maosh 💰", "val": "A"},
            {"text": "B) Loyihaga qarab, katta daromad 🚀", "val": "B"},
            {"text": "C) Shaxsiy brendim orqali keladigan foyda 🌟", "val": "C"},
            {"text": "D) Passiv daromad va sarmoyalar 📈", "val": "D"}
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

# 🤖 YAGONA VA TOZA WEBHOOK
@app.post("/webhook")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    
    # === 1. ODDIY XABARLAR VA WEBAPP KELGANDA ===
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
                phone = parsed.get("phone", "Noma'lum")
                answers = parsed.get("survey_answers", {})
                
                user = db.query(models.User).filter(models.User.telegram_id == str(chat_id)).first()
                if not user:
                    user = models.User(telegram_id=str(chat_id), full_name=name, phone_number=phone)
                    db.add(user)
                else:
                    user.full_name = name
                    user.phone_number = phone
                db.commit()
                db.refresh(user)
                
                survey = models.SurveyResponse(user_id=user.id, raw_answers=answers)
                db.add(survey)
                db.commit()
                
                # 1-Bosqich tugadi, 2-Bosqichga o'tish tugmasi
                success_text = (
                    f"✅ Rahmat, <b>{name}</b>! Sizning holatingizni tahlil qildik.\n\n"
                    f"Aynan sizga qaysi kasb mos kelishini aniqlash uchun "
                    f"<b>15 savollik Chuqur Diagnostikani</b> boshlaymiz.\n\n👇 Tayyor bo'lsangiz, tugmani bosing!"
                )
                keyboard = {
                    "inline_keyboard": [[{"text": "🚀 Diagnostikani boshlash", "callback_data": "start_test"}]]
                }
                await send_message(chat_id, success_text, keyboard)
                
            except Exception as e:
                print("Xatolik:", e)
                await send_message(chat_id, "Kechirasiz, ma'lumotni saqlashda xatolik yuz berdi.")
                
    # === 2. INLINE TUGMALAR BOSILGANDA (DIAGNOSTIKA) ===
    elif "callback_query" in data:
        cb = data["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        message_id = cb["message"]["message_id"]
        cb_data = cb["data"]  # Tugmaga yashiringan kod
        
        # Testni boshlash
        if cb_data == "start_test":
            user_test_state[chat_id] = {"step": 0, "answers": []}
            q = QUESTIONS[0]
            
            keyboard = {"inline_keyboard": [[{"text": opt["text"], "callback_data": f"ans_{opt['val']}"}] for opt in q["options"]]}
            await edit_message(chat_id, message_id, q["text"], keyboard)
            
        # Savolga javob berilganda
        elif cb_data.startswith("ans_"):
            if chat_id not in user_test_state:
                await send_message(chat_id, "Iltimos, testni qaytadan boshlang (/start).")
                return {"status": "ok"}
                
            answer_val = cb_data.split("_")[1]
            current_step = user_test_state[chat_id]["step"]
            
            # Javobni saqlab qo'yamiz
            user_test_state[chat_id]["answers"].append(answer_val)
            user_test_state[chat_id]["step"] += 1
            next_step = user_test_state[chat_id]["step"]
            
            # Agar savollar tugamagan bo'lsa, keyingisini chiqaramiz
            if next_step < len(QUESTIONS):
                q = QUESTIONS[next_step]
                keyboard = {"inline_keyboard": [[{"text": opt["text"], "callback_data": f"ans_{opt['val']}"}] for opt in q["options"]]}
                await edit_message(chat_id, message_id, q["text"], keyboard)
                
            # Agar savollar tugagan bo'lsa, NATIJA
            else:
                final_answers = user_test_state[chat_id]["answers"]
                
                # Bu yerda javoblarni sanash mantiqini yozamiz
                a_count = final_answers.count("A")
                b_count = final_answers.count("B")
                
                # Hozircha oddiy xabar
                result_text = (
                    f"🎉 <b>Tabriklaymiz! Siz diagnostikadan o'tdingiz.</b>\n\n"
                    f"Sizning javoblaringiz bazaga qabul qilindi. A variantlar: {a_count} ta.\n"
                    f"<i>Sizning shaxsiy PDF yo'l xaritangiz tayyorlanmoqda...</i>"
                )
                await edit_message(chat_id, message_id, result_text)
                
                # Xotirani tozalash
                del user_test_state[chat_id]

    return {"status": "ok"}