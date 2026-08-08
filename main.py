import os
import requests
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

# Barcha papkalaringizdagi routerlarni chaqiramiz
from routers import users, admin, assessment, results

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# VERCEL DOMENINGIZNI SHU YERGA YOZING (oxirida / bo'lmasin)
WEBAPP_URL = "https://kelajak-bot-frontend.vercel.app/webapp"

app = FastAPI()

# HTML fayllar papkasi
templates = Jinja2Templates(directory="templates")

# Routerlarni tizimga ulaymiz
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(assessment.router)
app.include_router(results.router)

# ==========================================
# 🌐 FRONTEND: WEBAPP NI KO'RSATISH YO'LAGI
# ==========================================
@app.get("/webapp", response_class=HTMLResponse)
async def serve_webapp(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ==========================================
# 🤖 BACKEND: TELEGRAM WEBHOOK (Xabarlarni ushlab olish)
# ==========================================
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        
        # A) Mijoz /start bosganda o'yin tugmasini yuborish
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
            
            payload = {
                "chat_id": chat_id,
                "text": reply_text,
                "parse_mode": "HTML",
                "reply_markup": keyboard
            }
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json=payload)
            
        # B) Mijoz o'yinni tugatib, natija jo'natganda
        elif "web_app_data" in message:
            result_data = message["web_app_data"]["data"] 
            
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                json={"chat_id": chat_id, "text": f"✅ Tizim qabul qildi. Sizning natijangiz: {result_data}"}
            )
            
    return {"status": "ok"}