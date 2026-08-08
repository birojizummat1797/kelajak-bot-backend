from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models, database

router = APIRouter(prefix="/users", tags=["Users"])

# Har qanday turdagi yozuvlarni qabul qiladigan sodda qolip
class UserCreate(BaseModel):
    telegram_id: str
    full_name: str = "Foydalanuvchi"

@router.post("")
@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.telegram_id == user.telegram_id).first()
    if not db_user:
        db_user = models.User(telegram_id=user.telegram_id, full_name=user.full_name)
        db.add(db_user)
        db.commit()
    return {"status": "ok"}