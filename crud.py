from sqlalchemy.orm import Session
import models, schemas

# Foydalanuvchini Telegram ID orqali bazadan qidirish
def get_user_by_telegram_id(db: Session, telegram_id: str):
    return db.query(models.User).filter(models.User.telegram_id == telegram_id).first()

# Yangi foydalanuvchini bazaga yozish
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(telegram_id=user.telegram_id, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ... oldingi yozilgan get_user_by_telegram_id va create_user tursin

# Boshlang'ich (birinchi) savolni topish
def get_start_question(db: Session):
    return db.query(models.Question).filter(models.Question.stage == "global_filter").first()

# ID orqali istalgan savolni topish
def get_question(db: Session, question_id: int):
    return db.query(models.Question).filter(models.Question.id == question_id).first()

# Berilgan savolga tegishli barcha javoblarni topish
def get_answers_for_question(db: Session, question_id: int):
    return db.query(models.Answer).filter(models.Answer.question_id == question_id).all()

# ... oldingi kodlar tursin

def create_result(db: Session, user_id: int, fitrat_type: str, top_professions: str, recommendation: str):
    db_result = models.Result(
        user_id=user_id,
        fitrat_type=fitrat_type,
        top_professions=top_professions,
        recommendation=recommendation
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result