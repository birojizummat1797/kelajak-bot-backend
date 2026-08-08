import os
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv

# Routerlarni chaqiramiz
from routers import users, admin, assessment, results

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# DIQQAT: Bu yerga ALOHIDA FRONTEND loyihangizning Vercel domenini yozasiz
WEBAPP_URL = "https://kelajak-bot-frontend.vercel.app"

app = FastAPI()

# Routerlarni ulaymiz
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(assessment.router)
app.include_router(results.router)

# ==========================================
# 🤖 BACKEND: TELEGRAM WEBHOOK (Faqat API)
# ==========================================
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        
        # A) /start bosilganda Frontend ssilkasini berish
        if "text" in message and message["text"] == "/start":
            keyboard = {
                "inline_keyboard": [
                    [{"text": "🎮 Kvestni boshlash", "web_app": {"url": WEBAPP_URL}}]
                ]
            }
            
            reply_text = (
                "👋 <b>Assalomu alaykum!</b>\n\n"
                "Sizga ko'proq kompyuter bilan ishlash yoqadimi yoki odamlar bilan?\n\n"
                "Atigi 3 daqiqalik qiziqarli kvestdan o'ting, yashirin qobiliyatingizni toping "
                "va maxsus grantlarga ega bo'ling!\n\n"
                "👇 <b>Pastdagi tugmani bosing va boshlang:</b>"
            )
            
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                json={"chat_id": chat_id, "text": reply_text, "parse_mode": "HTML", "reply_markup": keyboard}
            )
            
        # B) Frontend'dan kelgan natijani ushlab olish
        elif "web_app_data" in message:
            result_data = message["web_app_data"]["data"] 
            
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                json={"chat_id": chat_id, "text": f"✅ Tizim qabul qildi. Sizning natijangiz: {result_data}"}
            )
            
    return {"status": "ok"}