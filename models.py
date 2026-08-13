from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from database import Base

class User(Base):
    __tablename__ = "customers_v2"  # ESKI users O'RNIGA TOZA JADVAL

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    full_name = Column(String)
    phone_number = Column(String)

class SurveyResponse(Base):
    __tablename__ = "survey_v2"  # ESKI survey_responses O'RNIGA

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("customers_v2.id"))
    raw_answers = Column(JSON)  # Ma'lumotlar to'g'ridan-to'g'ri JSON saqlanadi