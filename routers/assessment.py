from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, database

router = APIRouter(prefix="/questions", tags=["Assessment"])

# 1. BAZANI YANGILASH VA TOZALASH UCHUN MAXSUS YO'L
@router.get("/seed-v2")
def seed_database_v2(db: Session = Depends(database.get_db)):
    # Eski ma'lumotlarni ildizi bilan tozalaymiz
    db.query(models.Answer).delete()
    db.query(models.Question).delete()
    db.commit()

    # ENG BIRINCHI SAVOL (Baza aynan shuni 1-chi bo'lib o'qiydi)
    q_main = models.Question(text="Tasavvur qiling, sizga kattagina mablag' va bo'sh vaqt berildi. Kuningizni qanday o'tkazgan bo'lardingiz?")
    db.add(q_main)
    db.commit()
    db.refresh(q_main)

    # TARMOQLI SAVOLLAR
    q_a = models.Question(text="Biror muammoga duch kelganda, odatda qanday yechim qidirasiz?")
    q_b = models.Question(text="Do'stlaringiz sizni ko'proq qaysi xislatingiz uchun qadrlashadi?")
    q_c = models.Question(text="Qaysi holat sizga ko'proq motivatsiya beradi?")
    q_d = models.Question(text="Siz uchun qaysi jarayon ko'proq ruhiy xotirjamlik va zavq beradi?")
    
    db.add_all([q_a, q_b, q_c, q_d])
    db.commit()
    db.refresh(q_a); db.refresh(q_b); db.refresh(q_c); db.refresh(q_d)

    # 1-savolning javoblari (Ular foydalanuvchini keyingi savollarga yo'naltiradi)
    db.add(models.Answer(question_id=q_main.id, text="Yangi texnologiyalarni o'rganish yoki mexanizmlarni tahlil qilish", next_question_id=q_a.id, trait_score=1))
    db.add(models.Answer(question_id=q_main.id, text="Odamlarga yordam berish yoki ularga yangi narsalarni o'rgatish", next_question_id=q_b.id, trait_score=2))
    db.add(models.Answer(question_id=q_main.id, text="Jamoani yig'ib biznes loyiha boshlash yoki savdo qilish", next_question_id=q_c.id, trait_score=3))
    db.add(models.Answer(question_id=q_main.id, text="Tabiat qo'ynida ishlash yoki o'z qo'llarim bilan foydali narsa yasash", next_question_id=q_d.id, trait_score=4))

    # Tarmoqli savollarning oxirgi javoblari (Bunda next_question_id yo'q, chunki test shu yerda tugaydi)
    db.add(models.Answer(question_id=q_a.id, text="Faqat aniq faktlar va raqamlarga asoslanaman.", next_question_id=None, trait_score=1))
    db.add(models.Answer(question_id=q_a.id, text="Tizimdagi xatolikni topib, to'liq qayta qurishga harakat qilaman.", next_question_id=None, trait_score=1))

    db.add(models.Answer(question_id=q_b.id, text="Boshqalarning dardini tinglab, to'g'ri maslahat bera olishimni.", next_question_id=None, trait_score=2))
    db.add(models.Answer(question_id=q_b.id, text="Fikrimni chiroyli va ta'sirli yetkazib bera olishimni (ijodkorlik).", next_question_id=None, trait_score=2))

    db.add(models.Answer(question_id=q_c.id, text="Katta guruhni orqamdan ergashtirish va yetakchilik qilish.", next_question_id=None, trait_score=3))
    db.add(models.Answer(question_id=q_c.id, text="Foyda keltiradigan va tavakkal (risk) talab qiladigan qarorlar qabul qilish.", next_question_id=None, trait_score=3))

    db.add(models.Answer(question_id=q_d.id, text="Yerni parvarish qilib ekin ekish, tabiat bilan ishlash.", next_question_id=None, trait_score=4))
    db.add(models.Answer(question_id=q_d.id, text="O'z qo'lim bilan aniq, amaliy buyumlar yaratish.", next_question_id=None, trait_score=4))
    
    db.commit()
    return {"message": "MashaAlloh! Yangi tarmoqli baza jonli serverda 100% o'rnatildi!"}

# 2. Xavfsiz birinchi savol
@router.get("/first")
def get_first_question(db: Session = Depends(database.get_db)):
    question = db.query(models.Question).first()
    if not question:
        raise HTTPException(status_code=404, detail="Savollar topilmadi. Avval /seed-v2 qiling.")
    answers = db.query(models.Answer).filter(models.Answer.question_id == question.id).all()
    return {"id": question.id, "text": question.text, "answers": answers}

# 3. Keyingi savollar
@router.get("/{question_id}")
def get_question(question_id: int, db: Session = Depends(database.get_db)):
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Savol topilmadi")
    answers = db.query(models.Answer).filter(models.Answer.question_id == question.id).all()
    return {"id": question.id, "text": question.text, "answers": answers}