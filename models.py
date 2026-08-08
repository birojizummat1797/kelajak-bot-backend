from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)     # <--- MANA SHU QATOR YETISHMAYOTGAN EDI
    fitrat_type = Column(String, nullable=True)

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    stage = Column(String) # Masalan: "global_filter", "tech_branch"

# models.py faylining Answer qismi
class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    text = Column(String)
    next_question_id = Column(Integer, ForeignKey("questions.id"), nullable=True)
    
    # MANA SHU YANGI QATORNI QO'SHAMIZ:
    trait_score = Column(Integer, nullable=True)

class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    fitrat_type = Column(String)
    top_professions = Column(Text)
    recommendation = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())