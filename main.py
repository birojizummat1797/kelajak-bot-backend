import os
import json
import httpx
from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv

import models
from database import engine, get_db
from routers import users, admin, assessment, results

models.Base.metadata.create_all(bind=engine)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# DIQQAT: Frontend loyihangiz manzili
WEBAPP_URL = "https://kelajak-bot-frontend.vercel.app"

app = FastAPI()

app.include_router(users.router)
app.include_router(admin.router)
app.include_router(assessment.router)
app.include_router(results.router)

async def send_telegram_message(chat_id: int, text: str, reply_markup: dict = None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
        
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

@app.post("/webhook")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        
        # A) /start komandasi (TUGMA TURI O'ZGARTIRILDI ✅)
        if "text" in message and message["text"] == "/start":
            # Endi bu Inline emas, pastki klaviatura o'rnida chiquvchi tugma
            keyboard = {
                "keyboard": [
                    [{"text": "🎯 Diagnostikani boshlash", "web_app": {"url": WEBAPP_URL}}]
                ],
                "resize_keyboard": True
            }
            
            reply_text = (
                "👋 <b>Assalomu alaykum!</b>\n\n"
                "To'g'ri kasb tanlash va kelajagingizni qurish yo'lidagi "
                "maxsus diagnostika tizimiga xush kelibsiz.\n\n"
                "👇 <b>Pastdagi 'Diagnostikani boshlash' tugmasini bosing:</b>"
            )
            
            await send_telegram_message(chat_id, reply_text, keyboard)
            
        # B) Frontend'dan Diagnostika natijasi va Raqam kelganda
        elif "web_app_data" in message:
            try:
                web_app_data_str = message["web_app_data"]["data"]
                parsed_data = json.loads(web_app_data_str)
                
                full_name = parsed_data.get("name", "Noma'lum")
                phone_number = parsed_data.get("phone", "Noma'lum")
                raw_answers = parsed_data.get("answers", {}) 
                
                # Shaxsiy ma'lumotlarni saqlash
                user = db.query(models.User).filter(models.User.telegram_id == str(chat_id)).first()
                if not user:
                    user = models.User(telegram_id=str(chat_id), full_name=full_name, phone_number=phone_number)
                    db.add(user)
                    db.commit()
                    db.refresh(user)
                else:
                    user.full_name = full_name
                    user.phone_number = phone_number
                    db.commit()
                
                # Analitikani saqlash
                survey_response = models.SurveyResponse(
                    user_id=user.id,
                    raw_answers=raw_answers
                )
                db.add(survey_response)
                db.commit()
                
                success_text = (
                    f"✅ <b>Rahmat, {full_name}!</b>\n\n"
                    f"Ma'lumotlaringiz va diagnostika natijalari bazaga xavfsiz saqlandi.\n"
                    f"Tez orada sizga mos Yo'l Xaritasi taqdim etiladi!"
                )
                
                await send_telegram_message(chat_id, success_text)
                
            except Exception as e:
                print("Xatolik yuz berdi:", e)
                await send_telegram_message(chat_id, "Kechirasiz, xatolik yuz berdi. Iltimos qayta urinib ko'ring.")
                
    return {"status": "ok"}