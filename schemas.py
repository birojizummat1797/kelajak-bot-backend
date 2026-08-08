from pydantic import BaseModel
from typing import Optional, List
class UserCreate(BaseModel):
    telegram_id: str
    name: str
    full_name: str

class UserResponse(BaseModel):
    id: int
    telegram_id: str
    name: str

    class Config:
        from_attributes = True

# ... oldingi yozilgan UserCreate va UserResponse kodlari tursin

class AnswerResponse(BaseModel):
    id: int
    text: str
    next_question_id: int | None = None
    category: str | None = None

    class Config:
        from_attributes = True

class QuestionResponse(BaseModel):
    id: int
    text: str
    stage: str
    answers: list[AnswerResponse] = [] # Savolga tegishli javoblar ro'yxati

    class Config:
        from_attributes = True

# ... oldingi kodlar tursin

class ResultCreate(BaseModel):
    telegram_id: str
    answers: list[str] # Masalan: ['A', 'A', 'B']

class ResultResponse(BaseModel):
    id: int
    fitrat_type: str
    top_professions: str
    recommendation: str

    class Config:
        from_attributes = True