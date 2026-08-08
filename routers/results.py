from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models, database

router = APIRouter(prefix="/results", tags=["Results"])

# Qat'iy cheklovlarsiz qolip (422 xatosi bermasligi uchun)
class ResultRequest(BaseModel):
    telegram_id: str
    full_name: str = "Foydalanuvchi"
    answers: list[int] = []

@router.post("")
@router.post("/")
def calculate_and_save_result(req: ResultRequest, db: Session = Depends(database.get_db)):
    try:
        # Ballarni tahlil qilish
        scores = {1: 0, 2: 0, 3: 0, 4: 0}
        if req.answers:
            answers_in_db = db.query(models.Answer).filter(models.Answer.id.in_(req.answers)).all()
            for ans in answers_in_db:
                if ans.trait_score in scores:
                    scores[ans.trait_score] += 1

        top_trait = max(scores, key=scores.get)

        if top_trait == 1:
            f_type = "Tizimli Arxitektor (Texnik)"
        elif top_trait == 2:
            f_type = "Ijtimoiy Bog'lovchi (Gumanitar)"
        elif top_trait == 3:
            f_type = "Strategik Yetakchi (Boshqaruv)"
        else:
            f_type = "Amaliy Usta (Tabiat va Hunar)"

        # Kafolatlangan saqlash (Upsert)
        user = db.query(models.User).filter(models.User.telegram_id == req.telegram_id).first()
        if not user:
            user = models.User(telegram_id=req.telegram_id, full_name=req.full_name)
            db.add(user)
            
        user.fitrat_type = f_type
        db.commit()

        return {"status": "ok", "fitrat": f_type}
    
    except Exception as e:
        print("Backend saqlashda xatolik:", e)
        return {"status": "error"}