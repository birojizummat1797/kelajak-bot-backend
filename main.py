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

# ⚡️ TELEGRAMGA XABAR YUBORISH FUNKSIYASI
async def send_message(chat_id: int, text: str, reply_markup: dict = None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

# 🤖 YAGONA VA TOZA WEBHOOK
@app.post("/webhook")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    
    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        
        # 1. /start bosilganda
        if "text" in msg and msg["text"] == "/start":
            keyboard = {
                "keyboard": [[{"text": "🎯 Diagnostikani boshlash", "web_app": {"url": WEBAPP_URL}}]],
                "resize_keyboard": True
            }
            await send_message(chat_id, "👋 Assalomu alaykum!\nPastdagi tugmani bosib diagnostikani boshlang:", keyboard)
            
        # 2. Frontend'dan ma'lumot kelganda (WebApp yopilganda)
        # 2. Frontend'dan ma'lumot kelganda (WebApp yopilganda)
        elif "web_app_data" in msg:
            try:
                raw_data = msg["web_app_data"]["data"]
                parsed = json.loads(raw_data)
                
                name = parsed.get("name", "Noma'lum")
                phone = parsed.get("phone", "Noma'lum")
                # XATO SHU YERDA EDI: endi "survey_answers" deb qabul qilamiz
                answers = parsed.get("survey_answers", {})
                
                # Bazaga yozish (Ism va raqam)
                user = db.query(models.User).filter(models.User.telegram_id == str(chat_id)).first()
                if not user:
                    user = models.User(telegram_id=str(chat_id), full_name=name, phone_number=phone)
                    db.add(user)
                else:
                    user.full_name = name
                    user.phone_number = phone
                db.commit()
                db.refresh(user)
                
                # Bazaga yozish (Og'riqlar va holat / Avatar)
                survey = models.SurveyResponse(user_id=user.id, raw_answers=answers)
                db.add(survey)
                db.commit()
                
                # Mijozga yuboriladigan ZANJIR (Funnel) xabari
                success_text = (
                    f"✅ Rahmat, {name}! Sizning holatingizni tahlil qildik.\n\n"
                    f"Muammoni to'liq hal qilish va sizga eng mos kasbni topish uchun "
                    f"tez orada <b>15 savollik Chuqur Diagnostikani</b> boshlaymiz! Bizdan uzoqlashmang."
                )
                await send_message(chat_id, success_text)
                
            except Exception as e:
                print("Xatolik:", e)
                await send_message(chat_id, "Kechirasiz, ma'lumotni saqlashda xatolik yuz berdi.")
                
    # return {"status": "ok"}
    return {"status": "ok"}