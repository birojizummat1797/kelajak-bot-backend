import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# .env faylini o'qish
load_dotenv()

# Bazaga ulanish havolasini olish
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 🚨 ENG MUHIM FIX (Aqlli filtr):
# Agar URL "postgres://" deb boshlansa, uni "postgresql://" ga o'zgartirib olamiz.
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

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