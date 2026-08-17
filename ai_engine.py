import os
import json
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
# Gemini API kalitini sozlash (Buni .env faylga qo'shib qo'yish yodingizdan chiqmasin!)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

async def analyze_user_profile(user_data: dict) -> dict:
    """
    Foydalanuvchining diagnostika javoblarini AI orqali tahlil qilib, 
    eng mos kasb va PDF uchun ma'lumotlarni JSON formatida qaytaradi.
    """
    
    # 🎯 MASTER PROMPT (AI ga qat'iy buyruq)
    prompt = f"""
    Sen dunyodagi eng kuchli IT va Karyera maslahatchisisan. Sening vazifang mijozning psixologik portreti, qiziqishlari, byudjeti va sharoitlaridan kelib chiqib, unga mutlaqo mos keladigan 1 ta eng kuchli zamonaviy kasbni va 2 ta muqobil variantni topish.

    MIJOZNING MA'LUMOTLARI (JSON):
    {json.dumps(user_data, indent=2, ensure_ascii=False)}

    QAT'IY QOIDALAR:
    1. Agar mijozning kompyuteri bo'lmasa ("Kompyuter yo'q, faqat telefon"), unga og'ir dasturlash (Backend, Mobile) tavsiya qilma. SMM, Copywriting yoki Mobil Mobilografiya tavsiya qil.
    2. Agar mijozning byudjeti "Faqat bepul" bo'lsa, unga bepul resurslari ko'p bo'lgan kasblarni (Frontend, Design) ber.
    3. Agar "Odamlar bilan" ishlashni tanlagan bo'lsa, Project Manager, Sales Manager yoki HR tavsiya qil.
    4. Natija mijozga tushunarli, o'zbek tilida (lotin yozuvida) bo'lishi shart.

    NATIJA FORMATI:
    Javobni FAQATGINA quyidagi aniq JSON formatida qaytar. Hech qanday boshqa so'z, tushuntirish yoki markdown (```json) belgilari qo'shma, faqat sof JSON obyekt bo'lsin:
    {{
      "top_career": {{
          "title": "Kasb nomi (Masalan: Data Analyst)",
          "fit_score": 92,
          "reason": "Nima uchun aynan shu kasb mos keldi? (1-2 ta qisqa gap)",
          "technologies": ["Python", "SQL", "Excel", "PowerBI"],
          "time_to_learn": "6-8 oy",
          "salary_expectation": "$500 - $1500",
          "biggest_risk": "Bu sohadagi eng katta qiyinchilik va xavf nima?"
      }}
    }}
    """
    
    try:
        # Eng yangi va tezkor modelni tanlaymiz
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Asinxron tarzda AI ga so'rov yuborish
        response = await asyncio.to_thread(model.generate_content, prompt)
        result_text = response.text.strip()
        
        # Markdown backtick'larni tozalash (agar AI baribir qo'shib yuborsa)
        if result_text.startswith("```json"):
            result_text = result_text.replace("```json", "", 1)
        if result_text.endswith("```"):
            result_text = result_text.rsplit("```", 1)[0]
            
        # JSON ni lug'atga (dict) o'girish
        parsed_result = json.loads(result_text.strip())
        return parsed_result
        
    except Exception as e:
        print(f"AI Analizida xatolik yuz berdi: {e}")
        # Xato bo'lganda zaxira (fallback) ma'lumot qaytariladi
        return {
            "top_career": {
                "title": "Business Analyst",
                "fit_score": 85,
                "reason": "Tizimda vaqtinchalik xatolik yuz berdi, lekin analitik qobiliyatlaringiz bu kasbga mos keladi.",
                "technologies": ["Excel", "Jira", "Muloqot"],
                "time_to_learn": "3-6 oy",
                "salary_expectation": "$400 - $1000",
                "biggest_risk": "Doimiy muloqot va bosim"
            }
        }