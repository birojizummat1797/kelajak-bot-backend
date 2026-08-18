import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Barqaror kutubxona va model
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

async def analyze_user_profile(user_data: dict) -> dict:
    """
    Foydalanuvchining ma'lumotlarini xalqaro standartlar asosida chuqur tahlil qiluvchi 
    Premium AI Dvigateli (JSON qaytaradi).
    """
    
    prompt = f"""
    Sen xalqaro miqyosdagi Senior IT-Karyera maslahatchisi va biznes psixologsan. 
    Sening vazifang quyida berilgan mijoz javoblarini (32 ta diagnostika savollarini) juda chuqur tahlil qilib, uning yashirin potensialini ochib berish va unga 100% mos keladigan Karyera Yo'l Xaritasini tuzib chiqish.

    MIJOZNING MA'LUMOTLARI (JSON):
    {json.dumps(user_data, indent=2, ensure_ascii=False)}

    QAT'IY QOIDALAR:
    1. Tahlil shunchaki oddiy emas, balki qimmatbaho (Premium) maslahat darajasida bo'lishi shart.
    2. 'Constraints' (Cheklovlar) va 'Values' (Qadriyatlar) dagi mijozning vaqti, kompyuteri va ingliz tili darajasiga mos reja tuz. Agar kompyuteri yo'q bo'lsa, qat'iyan faqat telefonda yuqori daromad keltiradigan kasblarni tavsiya qil.
    3. Javob mutlaqo o'zbek tilida bo'lsin.
    4. Hech qanday ortiqcha matn, tushuntirish yozma. Faqat va faqat quyidagi tuzilishdagi SOF JSON obyektni qaytar.

    KUTILAYOTGAN JSON FORMATI:
    {{
      "psychological_profile": {{
        "archetype": "Mijozning psixologik arxetipi (Masalan: 'Strategik Fikrlovchi')",
        "super_power": "Mijozning eng kuchli yashirin qobiliyati (1-2 gap)",
        "growth_area": "Mijoz rivojlantirishi kerak bo'lgan asosiy jihat"
      }},
      "careers": {{
        "top_match": {{
          "title": "Eng mos Top Kasb nomi",
          "match_score": 98,
          "why_this": "Nega aynan bu kasb mijozning xarakteriga va hozirgi sharoitiga mos? (Chuqur asos)",
          "core_skills": ["Ko'nikma 1", "Ko'nikma 2", "Ko'nikma 3"]
        }},
        "alternatives": ["Muqobil kasb 1", "Muqobil kasb 2"]
      }},
      "roadmap": [
        {{"phase": "1-2 oylar", "focus": "Poydevor va Asos", "action": "Aynan nimalarni o'rganish kerak va qanday resurslardan foydalanish lozim?"}},
        {{"phase": "3-4 oylar", "focus": "Amaliyot va Portfel", "action": "Qanday real loyihalar ustida ishlash va tajriba to'plash kerak?"}},
        {{"phase": "5-6 oylar", "focus": "Bozorga chiqish", "action": "Birinchi daromadni qanday topish mumkin?"}}
      ],
      "financial_forecast": {{
        "starting_income": "$300 - $500",
        "potential_1_year": "$1000+"
      }},
      "pro_tips": [
        "Raqobatchilardan bir qadam oldinda bo'lish uchun 1-maxsus tavsiya",
        "Ish topish bo'yicha 2-maxsus tavsiya"
      ]
    }}
    """
    
    try:
        response = await model.generate_content_async(prompt)
        result_text = response.text.strip()
        
        # Markdown backtick'larni tozalash (JSON ni sof holda ajratib olish)
        if result_text.startswith("```json"):
            result_text = result_text.replace("```json", "", 1)
        if result_text.endswith("```"):
            result_text = result_text.rsplit("```", 1)[0]
            
        return json.loads(result_text.strip())
        
    except Exception as e:
        print(f"AI Analizida xatolik yuz berdi: {e}")
        # Xatolik yuz berganda bo'sh lug'at qaytariladi, PDF generator qulab tushmaydi
        return {}