from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
import models
import database
import httpx  # type: ignore[import]
import csv
import io
import os  # Fayl bor-yo'qligini tekshirish uchun (Senior yondashuv)

from dotenv import load_dotenv

load_dotenv() # .env faylini o'qiydi
BOT_TOKEN = os.getenv("BOT_TOKEN") # Maxfiy tokenni tortib oladi

router = APIRouter(tags=["Admin"])

# O'zingizning aniq token va ID ingiz:
# BOT_TOKEN = "8826583094:AAED10ZR8QxAOtMwZdrlZEqlf5jLmay4U-w"
ADMIN_ID = 2056237329
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

@router.post("/webhook")
async def telegram_webhook(request: Request, db: Session = Depends(database.get_db)):
    try:
        update = await request.json()
        
        async with httpx.AsyncClient() as client:
            
            # 1. ADMIN TUGMALARNI BOSGANDA (Tasdiqlash / Rad etish)
            if "callback_query" in update:
                cb = update["callback_query"]
                data = cb["data"]
                admin_chat_id = cb["message"]["chat"]["id"]
                message_id = cb["message"]["message_id"]
                
                if admin_chat_id == ADMIN_ID:
                    action, client_id = data.split("_")
                    
                    # Tugmalarni yopamiz
                    await client.post(f"{TELEGRAM_API}/editMessageReplyMarkup", json={
                        "chat_id": admin_chat_id, "message_id": message_id, "reply_markup": {"inline_keyboard": []}
                    })

                    if action == "confirm":
                        # Mijozning qaysi fitratga tushganini bazadan topamiz
                        user = db.query(models.User).filter(models.User.telegram_id == str(client_id)).first()
                        
                        # Mos PDF faylini tanlash mantiqi
                        pdf_filename = "amaliy_usta.pdf"  # Standart fayl
                        if user and user.fitrat_type:
                            if "Tizimli" in user.fitrat_type:
                                pdf_filename = "tizimli_arxitektor.pdf"
                            elif "Ijtimoiy" in user.fitrat_type:
                                pdf_filename = "ijtimoiy_boglovchi.pdf"
                            elif "Strategik" in user.fitrat_type:
                                pdf_filename = "strategik_yetakchi.pdf"
                        
                        pdf_path = f"pdfs/{pdf_filename}"
                        success_text = (
                            "🎉 Tabriklaymiz! To'lov muvaffaqiyatli tasdiqlandi.\n\n"
                            "Mana sizning maxsus Yo'l xaritangiz! O'qib chiqing va o'z kelajagingiz sari qadam tashlang.\n\n"
                            "Savollar bo'yicha: @ulugbek_aliboyev"
                        )
                        
                        # XAVFSIZLIK: PDF fayl haqiqatan ham serverda bormi?
                        if os.path.exists(pdf_path):
                            with open(pdf_path, "rb") as pdf_file:
                                files = {"document": (pdf_filename, pdf_file, "application/pdf")}
                                await client.post(f"{TELEGRAM_API}/sendDocument", data={"chat_id": client_id, "caption": success_text}, files=files)
                        else:
                            # Agar fayl topilmasa, bot qulamaydi, shunchaki xabar boradi
                            fallback_text = success_text + "\n\n*(Fayl yuklanmoqda, tez orada admin to'g'ridan-to'g'ri yuboradi)*"
                            await client.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": client_id, "text": fallback_text})
                            
                        await client.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": admin_chat_id, "text": f"✅ {client_id} ga tasdiq va PDF yuborildi."})
                    
                    elif action == "reject":
                        fail_text = "❌ Kechirasiz, siz yuborgan to'lov cheki tasdiqlanmadi.\n\nAgar xatolik yuz bergan bo'lsa, iltimos bizga yozing: @ulugbek_aliboyev"
                        await client.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": client_id, "text": fail_text})
                        await client.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": admin_chat_id, "text": f"❌ {client_id} to'lovi rad etildi."})
                        
                return {"status": "ok"}

            # 2. XABARLAR KELGANDA
            if "message" in update:
                msg = update["message"]
                chat_id = msg["chat"]["id"]
                user_id = msg["from"]["id"]
                text = msg.get("text", "")

                # A) Botga ilk kirganda
                if text == "/start":
                    welcome_text = (
                        "Assalamu alaykum! Kelajak kasbini tanlash botiga xush kelibsiz. 🚀\n\n"
                        "Shaxsiy fitratingiz va qobiliyatingizga eng mos keluvchi daromadli kasblarni aniqlash uchun "
                        "pastdagi **«Testni boshlash»** tugmasini bosing!\n\n"
                        "👨‍💻 Muallif: @ulugbek_aliboyev"
                    )
                    await client.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": welcome_text, "parse_mode": "Markdown"})

                # B) Mijoz rasm (chek) yuborsa
                elif "photo" in msg:
                    if user_id != ADMIN_ID:
                        photo_id = msg["photo"][-1]["file_id"]
                        
                        await client.post(f"{TELEGRAM_API}/sendMessage", json={
                            "chat_id": chat_id, "text": "⏳ Chek qabul qilindi. 1-2 daqiqada adminlarimiz to'lovni tasdiqlashadi...\n(Muammo bo'lsa @ulugbek_aliboyev ga yozing)"
                        })
                        
                        keyboard = {
                            "inline_keyboard": [
                                [{"text": "✅ Tasdiqlash", "callback_data": f"confirm_{user_id}"}],
                                [{"text": "❌ Rad etish", "callback_data": f"reject_{user_id}"}]
                            ]
                        }
                        await client.post(f"{TELEGRAM_API}/sendPhoto", json={
                            "chat_id": ADMIN_ID,
                            "photo": photo_id,
                            "caption": f"💰 YANGI TO'LOV KELDI!\nMijoz ID: {user_id}\nIsmi: {msg['from'].get('first_name', '')}",
                            "reply_markup": keyboard
                        })
                
                # C) Admin stat buyrug'i
                elif text == "/admin_stats":
                    if user_id == ADMIN_ID:
                        users = db.query(models.User).all()
                        csv_file = io.StringIO()
                        writer = csv.writer(csv_file)
                        writer.writerow(["Baza ID", "Telegram ID", "Ism", "Fitrat Tipi"])
                        for u in users:
                            writer.writerow([u.id, u.telegram_id, u.full_name, u.fitrat_type or "Tugallanmagan"])
                        
                        files_upload = {"document": ("Natijalar.csv", csv_file.getvalue().encode('utf-8'), "text/csv")}
                        await client.post(f"{TELEGRAM_API}/sendDocument", data={"chat_id": chat_id, "caption": f"📊 Jami {len(users)} ta odam:"}, files=files_upload)

        return {"status": "ok"}
    except Exception as e:
        print("Webhook xatosi:", e)
        return {"status": "error"}