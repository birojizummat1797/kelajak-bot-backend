import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Aqlli filtr: postgres:// ni postgresql:// ga aylantiradi
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Eski kodingiz taxminan shunday bo'lishi kerak:
# engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SHUNI QUYIDAGICHA O'ZGARTIRING:
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True, # Aloqa uzilgan bo'lsa, crash bo'lmaydi, qayta ulanadi
    connect_args={"sslmode": "require"} # Neon DB talab qiladigan xavfsizlik
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()