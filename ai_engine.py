import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

# # Yangi usulda klient yaratish
# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# async def analyze_user_profile(user_data: dict) -> dict:
#     """
#     Foydalanuvchining ma'lumotlarini xalqaro standartlar asosida chuqur tahlil qiluvchi 
#     Premium AI Dvigateli.
#     """
    
#     prompt = f"""
#     Sen xalqaro miqyosdagi Senior IT-Karyera maslahatchisi va biznes psixologsan. 
#     Sening vazifang quyida berilgan mijoz javoblarini juda chuqur tahlil qilib, uning yashirin potensialini ochib berish va unga 100% mos keladigan 6 oylik Karyera Yo'l Xaritasini tuzib chiqish.

#     MIJOZNING MA'LUMOTLARI (JSON):
#     {json.dumps(user_data, indent=2, ensure_ascii=False)}

#     QAT'IY QOIDALAR:
#     1. Tahlil shunchaki oddiy emas, balki qimmatbaho (Premium) maslahat darajasida bo'lishi shart. So'z boyligingni kengaytir va ilhomlantiruvchi tildan foydalan.
#     2. Agar mijozda kompyuter yo'q bo'lsa, unga qat'iyan faqat telefonda yuqori daromad keltiradigan kasblarni (Mobilografiya, SMM, Copywriting, Targetolog, Telegram Botlar Menejeri) tavsiya qil.
#     3. Javob mutlaqo o'zbek tilida (lotin alifbosida) bo'lsin.
#     4. Hech qanday ortiqcha matn, tushuntirish yoki salomlashish yozma. Faqat va faqat quyidagi tuzilishdagi SOF JSON obyektni qaytar.

#     KUTILAYOTGAN JSON FORMATI:
#     {{
#       "psychological_profile": {{
#         "archetype": "Mijozning psixologik arxetipi (Masalan: 'Strategik Fikrlovchi', 'Ijodkor Yaratuvchi', 'Lider-Tashkilotchi')",
#         "super_power": "Mijozning eng kuchli yashirin qobiliyati (1-2 gap)",
#         "growth_area": "Mijoz rivojlantirishi kerak bo'lgan asosiy jihat"
#       }},
#       "careers": {{
#         "top_match": {{
#           "title": "Eng mos Top Kasb nomi",
#           "match_score": 98,
#           "why_this": "Nega aynan bu kasb mijozning xarakteriga va hozirgi sharoitiga mos? (Chuqur va ishonchli asos)",
#           "core_skills": ["Ko'nikma 1", "Ko'nikma 2", "Ko'nikma 3"]
#         }},
#         "alternatives": ["Muqobil kasb 1", "Muqobil kasb 2"]
#       }},
#       "roadmap": [
#         {{"phase": "1-2 oylar", "focus": "Poydevor va Asos", "action": "Aynan nimalarni o'rganish kerak va qanday resurslardan foydalanish lozim?"}},
#         {{"phase": "3-4 oylar", "focus": "Amaliyot va Portfel", "action": "Qanday real loyihalar ustida ishlash va tajriba to'plash kerak?"}},
#         {{"phase": "5-6 oylar", "focus": "Bozorga chiqish", "action": "Birinchi daromadni qanday va qayerdan topish mumkin?"}}
#       ],
#       "financial_forecast": {{
#         "starting_income": "$300 - $500",
#         "potential_1_year": "$1000+"
#       }},
#       "pro_tips": [
#         "Raqobatchilardan bir qadam oldinda bo'lish uchun 1-maxsus tavsiya",
#         "Ish topish yoki mijoz jalb qilish bo'yicha 2-maxsus tavsiya"
#       ]
#     }}
#     """
    
#     try:
#         response = await client.aio.models.generate_content(
#             model='gemini-3.6-flash',
#             contents=prompt
#         )
#         result_text = response.text.strip()
        
#         # Markdown backtick'larni tozalash
#         if result_text.startswith("```json"):
#             result_text = result_text.replace("```json", "", 1)
#         if result_text.endswith("```"):
#             result_text = result_text.rsplit("```", 1)[0]
            
#         return json.loads(result_text.strip())
        
#     except Exception as e:
#         print(f"AI Analizida xatolik yuz berdi: {e}")
#         # Xatolik yuz berganda bo'sh lug'at qaytariladi
#         return {}

# Gemini sozlamalari (agar sizda boshqacha bo'lsa, o'zinikini qoldiring)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash') # yoki o'zingizdagi 3.6-flash modeli

async def analyze_user_profile(user_answers: dict) -> str:
    # JSON ma'lumotni chiroyli matn formatiga o'tkazamiz
    user_data_str = json.dumps(user_answers, indent=2, ensure_ascii=False)
    
    prompt = f"""
    Sen global miqyosdagi eng tajribali IT-Karyera maslahatchisi va psixologsan.
    Mijozimiz sening qabulingga keldi va uning chuqurlashtirilgan 32 ta diagnostika savollariga bergan javoblari quyidagi JSON formatida keltirilgan:
    
    {user_data_str}
    
    Sening VAZIFANG:
    Ushbu ma'lumotlarni tahlil qilib, mijoz uchun 100% shaxsiylashtirilgan "Shaxsiy Yo'l Xaritasi"ni (Roadmap) tuzib berish. 
    
    TAHLIL QOIDALARI:
    1. 'Goal' va 'Values': Mijoz nima xohlayotganini va uning qadriyatlarini (masalan, erkinlik yoki barqarorlik) inobatga ol.
    2. 'Skills' va 'Aptitude': Uning hozirgi qobiliyatlariga qarab, qaysi soha unga osonroq kechishini aniqla.
    3. 'Constraints': Mijozning vaqti, kompyuteri va ingliz tili darajasiga mos reja tuz (masalan, telefoni bo'lsa, og'ir dasturlash emas, SMM yoki mobil dizayn tavsiya qil).
    
    PDF GENERATOR UCHUN QAT'IY STRUKTURA (Markdown formatida yoz):
    # [Mijozga eng mos kelgan bitta IT Kasb nomi]
    
    ## 🎯 Nima uchun aynan shu kasb?
    (Mijozning javoblaridan 2-3 ta aniq sabab keltirib, psixologik dalda ber)
    
    ## 🚀 3 Oylik Harakatlar Rejasi (Roadmap)
    * **1-Oy: Poydevor** - (Qanday ko'nikmalarni o'rganishi kerak va qaysi resurslardan)
    * **2-Oy: Amaliyot** - (Qanday loyihalar qilishi kerak)
    * **3-Oy: Natija** - (Ish topish yoki daromadga chiqish sirlari)
    
    ## ⚠️ Kuchli va Zaif tomonlaringiz
    * **Kuchli tomoningiz:** (Tahlildan kelib chiqib)
    * **Ehtiyot bo'lishingiz kerak:** (Mijozning qadriyati yoki cheklovlaridan kelib chiqib ogohlantirish)
    
    Diqqat: Hech qanday HTML ishlatma, faqat standart Markdown (#, ##, *, bold) ishlat. Ortiqcha kirish so'zlarisiz to'g'ridan-to'g'ri tahlilni boshla!
    """
    
    try:
        # AI ga so'rov yuborish (Asinxron usulda)
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        print(f"AI Dvigatelda xatolik: {e}")
        return "Kechirasiz, tahlil jarayonida xatolik yuz berdi. Iltimos, mutaxassisga murojaat qiling."