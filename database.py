import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# .env faylini o'qish
load_dotenv()

# Bazaga ulanish havolasini olish
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Dvigatelni ishga tushirish
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Xavfsiz sessiya boshqaruvi
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()