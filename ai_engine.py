# import json
# import os
# import re  # <--- YANGI QO'SHILDI
# import google.generativeai as genai
# from dotenv import load_dotenv

# load_dotenv()

# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# model = genai.GenerativeModel('gemini-pro')

# async def analyze_user_profile(user_data: dict) -> dict:
#     user_data_str = json.dumps(user_data, indent=2, ensure_ascii=False)
    
#     prompt = f"""
#     Sen xalqaro miqyosdagi Senior IT-Karyera maslahatchisi va biznes psixologsan. 
#     Sening vazifang quyida berilgan mijoz javoblarini juda chuqur tahlil qilib, uning yashirin potensialini ochib berish va unga 100% mos keladigan Karyera Yo'l Xaritasini tuzib chiqish.

#     MIJOZNING MA'LUMOTLARI (JSON):
#     {user_data_str}

#     QAT'IY QOIDALAR:
#     1. Tahlil shunchaki oddiy emas, balki qimmatbaho (Premium) maslahat darajasida bo'lishi shart.
#     2. 'Constraints' va 'Values' dagi mijozning vaqti, kompyuteri va ingliz tili darajasiga mos reja tuz. Agar kompyuteri yo'q bo'lsa, qat'iyan faqat telefonda yuqori daromad keltiradigan kasblarni tavsiya qil.
#     3. Javob mutlaqo o'zbek tilida bo'lsin.
#     4. Hech qanday markdown (```json ... ```) ishlatma! Faqat va faqat SOF JSON obyektni qaytar. Boshqa bitta ham so'z yozma!

#     KUTILAYOTGAN JSON FORMATI:
#     {{
#       "psychological_profile": {{
#         "archetype": "Mijozning psixologik arxetipi",
#         "super_power": "Mijozning eng kuchli yashirin qobiliyati (1-2 gap)",
#         "growth_area": "Mijoz rivojlantirishi kerak bo'lgan asosiy jihat"
#       }},
#       "careers": {{
#         "top_match": {{
#           "title": "Eng mos Top Kasb nomi",
#           "match_score": 98,
#           "why_this": "Nega aynan bu kasb mijozning xarakteriga mos?",
#           "core_skills": ["Ko'nikma 1", "Ko'nikma 2", "Ko'nikma 3"]
#         }},
#         "alternatives": ["Muqobil kasb 1", "Muqobil kasb 2"]
#       }},
#       "roadmap": [
#         {{"phase": "1-2 oylar", "focus": "Poydevor va Asos", "action": "Aynan nimalarni o'rganish kerak?"}},
#         {{"phase": "3-4 oylar", "focus": "Amaliyot va Portfel", "action": "Qanday real loyihalar qilish kerak?"}},
#         {{"phase": "5-6 oylar", "focus": "Bozorga chiqish", "action": "Birinchi daromadni qanday topish mumkin?"}}
#       ],
#       "financial_forecast": {{
#         "starting_income": "$300 - $500",
#         "potential_1_year": "$1000+"
#       }},
#       "pro_tips": [
#         "Raqobatchilardan bir qadam oldinda bo'lish uchun maxsus tavsiya",
#         "Ish topish bo'yicha maxsus tavsiya"
#       ]
#     }}
#     """
    
#     try:
#         response = await model.generate_content_async(prompt)
#         result_text = response.text.strip()
        
#         # LOGLAR UCHUN MAXSUS PRINT (AI nima qaytarganini ko'rishimiz uchun)
#         print(f"\n--- AI QAYTARGAN JAVOB ---\n{result_text}\n-------------------------\n", flush=True)
        
#         # REGEX ORQALI FAQAT JSON QISMINI KESIB OLISH
#         match = re.search(r'\{[\s\S]*\}', result_text)
#         if match:
#             clean_json = match.group(0)
#             return json.loads(clean_json)
#         else:
#             print("JSON formati topilmadi!", flush=True)
#             return {}
            
#     except Exception as e:
#         print(f"AI Analizida JSON parse xatosi: {e}", flush=True)
#         return {}

import json
import os
import re
import httpx
from dotenv import load_dotenv

load_dotenv()

async def analyze_user_profile(user_data: dict) -> dict:
    user_data_str = json.dumps(user_data, indent=2, ensure_ascii=False)
    
    prompt = f"""
    Sen xalqaro miqyosdagi Senior IT-Karyera maslahatchisi va biznes psixologsan. 
    Sening vazifang quyida berilgan mijoz javoblarini juda chuqur tahlil qilib, uning yashirin potensialini ochib berish va unga 100% mos keladigan Karyera Yo'l Xaritasini tuzib chiqish.

    MIJOZNING MA'LUMOTLARI (JSON):
    {user_data_str}

    QAT'IY QOIDALAR:
    1. Tahlil shunchaki oddiy emas, balki qimmatbaho (Premium) maslahat darajasida bo'lishi shart.
    2. 'Constraints' va 'Values' dagi mijozning vaqti, kompyuteri va ingliz tili darajasiga mos reja tuz. Agar kompyuteri yo'q bo'lsa, qat'iyan faqat telefonda yuqori daromad keltiradigan kasblarni tavsiya qil.
    3. Javob mutlaqo o'zbek tilida bo'lsin.
    4. Hech qanday markdown (```json ... ```) ishlatma! Faqat va faqat SOF JSON obyektni qaytar. Boshqa bitta ham so'z yozma!

    KUTILAYOTGAN JSON FORMATI:
    {{
      "psychological_profile": {{
        "archetype": "Mijozning psixologik arxetipi",
        "super_power": "Mijozning eng kuchli yashirin qobiliyati (1-2 gap)",
        "growth_area": "Mijoz rivojlantirishi kerak bo'lgan asosiy jihat"
      }},
      "careers": {{
        "top_match": {{
          "title": "Eng mos Top Kasb nomi",
          "match_score": 98,
          "why_this": "Nega aynan bu kasb mijozning xarakteriga mos?",
          "core_skills": ["Ko'nikma 1", "Ko'nikma 2", "Ko'nikma 3"]
        }},
        "alternatives": ["Muqobil kasb 1", "Muqobil kasb 2"]
      }},
      "roadmap": [
        {{"phase": "1-2 oylar", "focus": "Poydevor va Asos", "action": "Aynan nimalarni o'rganish kerak?"}},
        {{"phase": "3-4 oylar", "focus": "Amaliyot va Portfel", "action": "Qanday real loyihalar qilish kerak?"}},
        {{"phase": "5-6 oylar", "focus": "Bozorga chiqish", "action": "Birinchi daromadni qanday topish mumkin?"}}
      ],
      "financial_forecast": {{
        "starting_income": "$300 - $500",
        "potential_1_year": "$1000+"
      }},
      "pro_tips": [
        "Raqobatchilardan bir qadam oldinda bo'lish uchun maxsus tavsiya",
        "Ish topish bo'yicha maxsus tavsiya"
      ]
    }}
    """
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("API KEY TOPILMADI!", flush=True)
        return {}

    # Dasturchilar usuli: SDK ni chetlab o'tib, to'g'ridan-to'g'ri API ga murojaat qilamiz
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            
        if response.status_code != 200:
            print(f"API XATOLIGI ({response.status_code}): {response.text}", flush=True)
            return {}

        data = response.json()
        result_text = data['candidates'][0]['content']['parts'][0]['text'].strip()
        
        print(f"\n--- AI QAYTARGAN JAVOB ---\n{result_text}\n-------------------------\n", flush=True)
        
        match = re.search(r'\{[\s\S]*\}', result_text)
        if match:
            clean_json = match.group(0)
            return json.loads(clean_json)
        else:
            print("JSON formati topilmadi!", flush=True)
            return {}
            
    except Exception as e:
        print(f"AI Analizida Xatolik: {e}", flush=True)
        return {}