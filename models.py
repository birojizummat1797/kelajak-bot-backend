from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from database import Base

# 1. SHAXSIY MA'LUMOTLAR JADVALI (PII - Personally Identifiable Information)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True) 
    phone_number = Column(String, nullable=True) # <-- Yig'ib olinadigan raqam
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# 2. DIAGNOSTIKA VA ANALITIKA JADVALI (Research Dataset)
class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # users jadvaliga bog'lanadi
    
    # Ma'lumotlarni JSONB formatida saqlaymiz (Tezkor va moslashuvchan)
    demographics = Column(JSON, nullable=True)      # Yosh, manzil, status
    current_state = Column(JSON, nullable=True)     # Hozirgi holat, kasb, qoniqish
    career_problem = Column(JSON, nullable=True)    # Noaniqlik, og'riqlar
    current_solutions = Column(JSON, nullable=True) # Nimalardan foydalanadi
    past_cost = Column(JSON, nullable=True)         # Yo'qotilgan vaqt va pul
    product_signal = Column(JSON, nullable=True)    # To'lashga tayyorligi
    
    # Barcha original javoblarni (Frontenddan kelgan) bitta ob'ektda saqlash uchun
    raw_answers = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())