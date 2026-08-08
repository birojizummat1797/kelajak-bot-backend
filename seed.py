from database import SessionLocal
from models import Question, Answer

def seed_data():
    db = SessionLocal()
    
    # Eski savollarni tozalash (yangi va toza mantiq yozish uchun)
    db.query(Answer).delete()
    db.query(Question).delete()
    db.commit()

    print("Eski baza tozalandi. Yangi tarmoqli savollar kiritilmoqda...")

    # 1. Tarmoqli savollarni yaratamiz
    q_a = Question(text="Biror muammoga duch kelganda, odatda qanday yechim qidirasiz?")
    q_b = Question(text="Do'stlaringiz sizni ko'proq qaysi xislatingiz uchun qadrlashadi?")
    q_c = Question(text="Qaysi holat sizga ko'proq motivatsiya beradi?")
    q_d = Question(text="Siz uchun qaysi jarayon ko'proq ruhiy xotirjamlik va zavq beradi?")
    
    db.add_all([q_a, q_b, q_c, q_d])
    db.commit()
    db.refresh(q_a); db.refresh(q_b); db.refresh(q_c); db.refresh(q_d)

    # 2. A Yo'nalish javoblari (Texnik)
    db.add(Answer(question_id=q_a.id, text="Faqat aniq faktlar va raqamlarga asoslanaman.", trait_score=1))
    db.add(Answer(question_id=q_a.id, text="Tizimdagi xatolikni topib, uni to'liq qayta qurishga harakat qilaman.", trait_score=1))

    # 3. B Yo'nalish javoblari (Ijtimoiy)
    db.add(Answer(question_id=q_b.id, text="Boshqalarni dardini tinglab, to'g'ri maslahat bera olishim uchun.", trait_score=2))
    db.add(Answer(question_id=q_b.id, text="Fikrimni chiroyli va ta'sirli yetkazib bera olishim (ijodkorlik).", trait_score=2))

    # 4. C Yo'nalish javoblari (Boshqaruv)
    db.add(Answer(question_id=q_c.id, text="Katta guruhni orqamdan ergashtirish va yetakchilik qilish.", trait_score=3))
    db.add(Answer(question_id=q_c.id, text="Foyda keltiradigan va tavakkal (risk) talab qiladigan qarorlar qabul qilish.", trait_score=3))

    # 5. D Yo'nalish javoblari (Tabiat/Hunar)
    db.add(Answer(question_id=q_d.id, text="Yerni parvarish qilib ekin ekish, tabiat bilan ishlash.", trait_score=4))
    db.add(Answer(question_id=q_d.id, text="O'z qo'lim bilan aniq, amaliy buyumlar yaratish.", trait_score=4))
    db.commit()

    # 6. GLOBAL FILTR (Eng birinchi savol)
    q_main = Question(text="Tasavvur qiling, sizga kattagina mablag' va bo'sh vaqt berildi. Kuningizni qanday o'tkazgan bo'lardingiz?")
    db.add(q_main)
    db.commit()
    db.refresh(q_main)

    # Global filtr javoblari (ular keyingi savollarga yo'naltiradi)
    db.add(Answer(question_id=q_main.id, text="Yangi texnologiyalarni o'rganish yoki mexanizmlarni tahlil qilish", next_question_id=q_a.id, trait_score=1))
    db.add(Answer(question_id=q_main.id, text="Odamlarga yordam berish yoki ularga yangi narsalarni o'rgatish", next_question_id=q_b.id, trait_score=2))
    db.add(Answer(question_id=q_main.id, text="Jamoani yig'ib yangi loyiha boshlash yoki savdo-sotiq qilish", next_question_id=q_c.id, trait_score=3))
    db.add(Answer(question_id=q_main.id, text="Tabiat qo'ynida ishlash yoki o'z qo'llarim bilan foydali narsa yasash", next_question_id=q_d.id, trait_score=4))
    db.commit()

    print("MashaAlloh! Haqiqiy savollar va tarmoqli yo'nalishlar bazaga joylandi!")
    db.close()

if __name__ == "__main__":
    seed_data()