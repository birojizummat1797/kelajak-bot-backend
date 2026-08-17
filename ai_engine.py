import os
import json
import asyncio
from google import genai  # YANGI KUTUBXONA
from dotenv import load_dotenv

load_dotenv()

# Yangi usulda klient yaratish
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def analyze_user_profile(user_data: dict) -> dict:
    """
    Foydalanuvchining diagnostika javoblarini AI orqali tahlil qilib, 
    eng mos kasb va PDF uchun ma'lumotlarni JSON formatida qaytaradi.
    """
    
    prompt = f"""
    Sen dunyodagi eng kuchli IT va Karyera maslahatchisisan. Sening vazifang mijozning psixologik portreti, qiziqishlari, byudjeti va sharoitlaridan kelib chiqib, unga mutlaqo mos keladigan 1 ta eng kuchli zamonaviy kasbni va 2 ta muqobil variantni topish.

    MIJOZNING MA'LUMOTLARI (JSON):
    {json.dumps(user_data, indent=2, ensure_ascii=False)}

    QAT'IY QOIDALAR:
    1. Agar kompyuter yo'q bo'lsa, SMM, Copywriting kabi telefon kasblarini ber.
    2. Natija o'zbek tilida (lotin yozuvida) bo'lishi shart.

    NATIJA FORMATI (Faqat sof JSON):
    {{
      "top_career": {{
          "title": "Kasb nomi",
          "fit_score": 92,
          "reason": "Nima uchun aynan shu kasb?",
          "technologies": ["Python", "SQL"],
          "time_to_learn": "6-8 oy",
          "salary_expectation": "$500 - $1500",
          "biggest_risk": "Sohadagi xavf"
      }}
    }}
    """
    
    try:
        # YANGI USUL: client.models orqali murojaat qilish
        # response = await asyncio.to_thread(
        #     client.models.generate_content,
        #     model='gemini-3.6-flash', # Model nomini o'zingiz xohlaganga o'zgartirishingiz mumkin
        #     contents=prompt
        # )

        # YANGI USUL: Asinxron ishlashi uchun client.aio.models ishlatamiz
        # Va eng barqaror gemini-1.5-flash modelini qo'yamiz
        response = await client.aio.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )

        result_text = response.text.strip()
        
        if result_text.startswith("```json"):
            result_text = result_text.replace("```json", "", 1)
        if result_text.endswith("```"):
            result_text = result_text.rsplit("```", 1)[0]
            
        return json.loads(result_text.strip())
        
    except Exception as e:
        print(f"AI Analizida xatolik yuz berdi: {e}")
        return {
            "top_career": {
                "title": "Business Analyst",
                "fit_score": 85,
                "reason": "Tizimda vaqtinchalik xatolik yuz berdi, lekin analitik qobiliyatlaringiz bu kasbga mos keladi.",
                "technologies": ["Excel", "Jira", "Muloqot"],
                "time_to_learn": "3-6 oy",
                "salary_expectation": "$400 - $1000",
                "biggest_risk": "Doimiy muloqot"
            }
        }