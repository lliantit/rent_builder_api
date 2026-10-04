from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.core.config import settings

# Створення рушія для підключення
engine = create_engine(settings.DATABASE_URL)

# Налаштування сесій для взаємодії з БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовий клас, від якого будуть успадковуватись моделі
Base = declarative_base()


# Функція для отримання сесії бази даних в ендпоінтах (Dependency)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
