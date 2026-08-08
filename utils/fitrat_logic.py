from collections import Counter

def calculate_fitrat(answers_categories: list[str]):
    # Eng ko'p tanlangan yo'nalishni topish
    if not answers_categories:
        return "Noma'lum", "Noma'lum", "Iltimos, testni qayta topshiring."
        
    most_common_category = Counter(answers_categories).most_common(1)[0][0]

    if most_common_category == 'A':
        fitrat = "Tizimli Analitik va Karyeraviy Quruvchi"
        professions = "1. Dasturchi/Muhandis\n2. Ma'lumotlar tahlilchisi\n3. Moliya va Buxgalteriya"
        recommendation = "Sizda aniqlik va mantiq kuchli. Oliy ta'lim (IT yoki Moliya) siz uchun maqsadga muvofiq, o'z yo'lingizda davom eting."
        
    elif most_common_category == 'B':
        fitrat = "Ijtimoiy Empat va Ustoz"
        professions = "1. Psixolog/Konsultant\n2. O'qituvchi/Ustoz\n3. Ijtimoiy/Tibbiyot xodimi"
        recommendation = "Odamlar bilan ishlash va ularga yordam berish sizning kuchingiz. Pedagogika yoki tibbiyot yo'nalishida akademik ta'lim olish tavsiya etiladi."
        
    elif most_common_category == 'C':
        fitrat = "Lider va Biznes Boshqaruvchi"
        professions = "1. Tadbirkor\n2. Loyiha Menejeri (PM)\n3. Marketing va Sotuv bo'yicha rahbar"
        recommendation = "Sizda yetakchilik va tavakkal qilish qobiliyati bor. An'anaviy 4 yillik o'qishdan ko'ra, amaliy biznes kurslar va real loyihalarda qatnashish ko'proq foyda beradi."
        
    elif most_common_category == 'D':
        fitrat = "Amaliyotchi va Tabiat Boshqaruvchisi"
        professions = "1. Zamonaviy Agronom\n2. Landshaft Dizayneri\n3. Chorvachilik Menejeri / Usta"
        recommendation = "Sizning fitratingiz amaliy natijalarga bog'langan. Sizga 4 yillik nazariy oliy ta'lim vaqtingizni o'g'irlashi mumkin. Buning o'rniga qisqa muddatli maxsus kurslar yoki amaliyotchi usta yonida shogird tushish tavsiya etiladi."
        
    else:
        fitrat = "Aralash Iqtidor Egasi"
        professions = "Turli sohalarda o'zingizni sinab ko'rishingiz mumkin"
        recommendation = "Sizda barcha yo'nalishlardan qiziqishlar bor, sizga shaxsiy mentor bilan maslahatlashish tavsiya etiladi."

    return fitrat, professions, recommendation